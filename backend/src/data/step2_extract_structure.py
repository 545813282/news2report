"""
Step 2: 结构化层 - 使用 AI 将清洗后的新闻抽取为结构化报告

功能：
1. 读取 cleaned_news.json
2. 对每条新闻调用 OpenAI API，按照 schema 抽取结构化字段
3. 验证输出格式（Pydantic）
4. 保存为 structured_news.jsonl 和 structured_news.json
"""

import argparse
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openai import OpenAI
from pydantic import ValidationError

from src.config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
from src.schema.news_schema import StructuredNewsItem

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
INPUT_FILE = BASE_DIR / "data" / "cleaned_news.json"
OUTPUT_JSONL = BASE_DIR / "data" / "structured_news.jsonl"
OUTPUT_JSON = BASE_DIR / "data" / "structured_news.json"
BATCH_ID = datetime.now(timezone.utc).strftime("batch_%Y%m%d_%H%M%S")

# 结构化抽取 Prompt
SYSTEM_PROMPT = """你是一位专业的 AI 产业分析师。请根据用户提供的新闻原文，抽取并生成一份结构化的 AI 新闻分析报告。

要求：
1. 严格按照下方的 JSON Schema 输出，不要添加 schema 以外的字段。
2. 输出必须是合法 JSON，不要包含 Markdown 代码块标记。
3. id 字段请使用输入中的 publish_time 和自增序号生成，例如 "news_20260702_001"。
4. title 使用原文标题，title_en 只在原文是英文时提供英文标题的中文翻译，或原文是中文时提供英文翻译（可选）。
5. category 必须从以下分类中选择：大模型、AI芯片、自动驾驶、机器人、AIGC、AI政策、AI应用、AI融资、AI安全、学术前沿、其他。
6. tags 请提取 3-8 个关键词标签。
7. source.name 使用原文来源名称，source.type 从：科技媒体、官方博客、社交媒体、学术平台、聚合平台、其他 中选择。
8. publish_time 必须是 ISO 8601 格式（如 2026-07-01T10:30:00+08:00），若原文只有日期则假设为当天 08:00:00+08:00。
9. language 根据原文语言选择：zh（中文）、en（英文）、zh-en（中英混合）。
10. original_text 保留用户输入的新闻正文全文。
11. ai_summary 要求结构化：主体 + 动作 + 关键数据 + 影响，控制在 80-150 字。
12. ai_opinion.viewpoint 用一句话总结核心观点；significance 从 重大/重要/一般/轻微 中选择；impact_direction 从 积极/消极/中性/复杂 中选择。
13. entities 提取新闻中的关键实体（公司、产品、人物、机构、技术、事件），至少 2 个。
14. technologies 提取涉及的技术关键词，如没有则留空数组。
15. event_type 从以下选择：产品发布、技术突破、融资并购、政策监管、合作签约、安全争议、人事变动、业绩报告、学术发表、其他。
16. sentiment 给出整体情感标签（positive/negative/neutral/mixed）、-1 到 1 的分数、以及判断理由。
17. key_points 提取最多 5 条核心要点，每条一句，包含关键事实或数据。
18. relations 提取实体关系三元组（subject-predicate-object），至少 1 条，如没有明显关系可留空数组。

输出 Schema：
{
  "id": "string",
  "title": "string",
  "title_en": "string | null",
  "category": "string",
  "tags": ["string"],
  "source": {"name": "string", "name_en": "string | null", "type": "string", "url": "string"},
  "author": "string | null",
  "publish_time": "string",
  "language": "string",
  "original_text": "string",
  "translated_text": "string | null",
  "original_summary": "string | null",
  "ai_summary": "string",
  "ai_opinion": {"viewpoint": "string", "significance": "string", "impact_direction": "string"},
  "entities": [{"name": "string", "type": "string"}],
  "technologies": ["string"],
  "event_type": "string",
  "sentiment": {"overall": "string", "score": "number", "reason": "string"},
  "key_points": ["string"],
  "relations": [{"subject": "string", "predicate": "string", "object": "string"}],
  "processing": {"extracted_at": "string", "model": "string", "batch_id": "string", "status": "string", "retry_count": "integer", "error_msg": "string | null"}
}
"""


def build_user_prompt(news: dict[str, Any], index: int) -> str:
    """为单条新闻构建用户输入 prompt。"""
    return f"""请对以下第 {index} 条新闻进行结构化抽取：

标题：{news['title']}
来源：{news['source']}
发布时间：{news['published_at']}
原文链接：{news['url']}

正文：
{news['content']}
"""


def generate_id(publish_time: str, index: int) -> str:
    """根据发布时间和序号生成新闻 ID。"""
    date_part = publish_time.replace("-", "")[:8]
    return f"news_{date_part}_{index:03d}"


def format_publish_time(publish_time: str) -> str:
    """将 YYYY-MM-DD 格式转换为 ISO 8601。"""
    return f"{publish_time}T08:00:00+08:00"


def extract_single_news(
    client: OpenAI,
    news: dict[str, Any],
    index: int,
    max_retries: int = 3,
) -> dict[str, Any] | None:
    """对单条新闻调用 OpenAI API 进行结构化抽取。"""
    extracted_at = datetime.now(timezone.utc).isoformat()
    news_id = generate_id(news["published_at"], index)

    for attempt in range(max_retries):
        try:
            logger.info(f"正在抽取 [{index}] {news['title'][:40]}... (尝试 {attempt + 1}/{max_retries})")

            # Kimi Code 模型仅支持 temperature=1
            temperature = 1.0 if OPENAI_MODEL == "kimi-for-coding" else 0.3
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": build_user_prompt(news, index)},
                ],
                response_format={"type": "json_object"},
                temperature=temperature,
                max_tokens=4000,
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("模型返回空内容")

            parsed = json.loads(content)

            # 注入基础字段和处理元数据
            parsed["id"] = news_id
            parsed["title"] = news["title"]
            parsed["publish_time"] = format_publish_time(news["published_at"])
            parsed["original_text"] = news["content"]
            parsed["source"]["url"] = news["url"]

            # 如果模型没填 source.name，使用清洗后的 source
            if not parsed.get("source", {}).get("name"):
                parsed["source"]["name"] = news["source"]

            parsed["processing"] = {
                "extracted_at": extracted_at,
                "model": OPENAI_MODEL,
                "batch_id": BATCH_ID,
                "status": "success",
                "retry_count": attempt,
                "error_msg": None,
            }

            # 使用 Pydantic 验证
            validated = StructuredNewsItem.model_validate(parsed)
            logger.info(f"抽取成功 [{index}]: {validated.title[:40]}...")
            return validated.model_dump()

        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            logger.warning(f"抽取失败 [{index}] 尝试 {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                logger.error(f"抽取失败 [{index}] 已达最大重试次数: {e}")
                return {
                    "id": news_id,
                    "title": news["title"],
                    "category": "其他",
                    "tags": [],
                    "source": {"name": news["source"], "type": "其他", "url": news["url"]},
                    "publish_time": format_publish_time(news["published_at"]),
                    "language": "zh",
                    "original_text": news["content"],
                    "ai_summary": "",
                    "ai_opinion": {"viewpoint": "", "significance": "一般", "impact_direction": "中性"},
                    "entities": [],
                    "technologies": [],
                    "event_type": "其他",
                    "sentiment": {"overall": "neutral", "score": 0.0, "reason": ""},
                    "key_points": [],
                    "relations": [],
                    "processing": {
                        "extracted_at": extracted_at,
                        "model": OPENAI_MODEL,
                        "batch_id": BATCH_ID,
                        "status": "failed",
                        "retry_count": attempt,
                        "error_msg": str(e),
                    },
                }
        except Exception as e:
            logger.error(f"OpenAI API 调用异常 [{index}]: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                return None

    return None


def read_cleaned_news(file_path: Path) -> list[dict[str, Any]]:
    """读取清洗后的新闻数据。"""
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_jsonl(items: list[dict[str, Any]], file_path: Path) -> None:
    """保存为 JSONL 格式。"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    logger.info(f"已保存 JSONL: {file_path}")


def save_json(items: list[dict[str, Any]], file_path: Path) -> None:
    """保存为 JSON 格式。"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    logger.info(f"已保存 JSON: {file_path}")


def mock_extract_single_news(news: dict[str, Any], index: int) -> dict[str, Any]:
    """演示模式：不调用 API，生成符合 schema 的 mock 数据。"""
    extracted_at = datetime.now(timezone.utc).isoformat()
    news_id = generate_id(news["published_at"], index)

    return StructuredNewsItem(
        id=news_id,
        title=news["title"],
        title_en=None,
        category="其他",
        tags=["AI", "演示"],
        source={
            "name": news["source"],
            "type": "科技媒体",
            "url": news["url"],
        },
        publish_time=format_publish_time(news["published_at"]),
        language="zh",
        original_text=news["content"],
        ai_summary=f"该新闻来自 {news['source']}，主要内容是：{news['content'][:60]}...",
        ai_opinion={
            "viewpoint": "（演示数据）需要调用真实 API 生成完整观点",
            "significance": "一般",
            "impact_direction": "中性",
        },
        entities=[{"name": news["source"], "type": "机构"}],
        technologies=["人工智能"],
        event_type="其他",
        sentiment={"overall": "neutral", "score": 0.0, "reason": "演示数据"},
        key_points=[news["content"][:50]],
        relations=[],
        processing={
            "extracted_at": extracted_at,
            "model": "mock-model",
            "batch_id": BATCH_ID,
            "status": "success",
            "retry_count": 0,
            "error_msg": None,
        },
    ).model_dump()


def main() -> None:
    parser = argparse.ArgumentParser(description="新闻结构化抽取")
    parser.add_argument("--mock", action="store_true", help="使用 mock 数据演示，不调用 OpenAI API")
    args = parser.parse_args()

    logger.info(f"批次ID: {BATCH_ID}")

    use_mock = args.mock or not OPENAI_API_KEY
    if use_mock:
        logger.info("演示模式：使用 mock 数据生成结构化输出（不调用 API）")
    else:
        logger.info(f"使用模型: {OPENAI_MODEL}")
        logger.info(f"API Base: {OPENAI_BASE_URL}")

    client = None if use_mock else OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

    logger.info(f"读取清洗数据: {INPUT_FILE}")
    cleaned_news = read_cleaned_news(INPUT_FILE)
    logger.info(f"共 {len(cleaned_news)} 条新闻待抽取")

    structured_items: list[dict[str, Any]] = []
    for idx, news in enumerate(cleaned_news, start=1):
        if use_mock:
            item = mock_extract_single_news(news, idx)
        else:
            item = extract_single_news(client, news, idx)  # type: ignore[arg-type]
            if idx < len(cleaned_news):
                time.sleep(0.5)
        if item:
            structured_items.append(item)

    save_jsonl(structured_items, OUTPUT_JSONL)
    save_json(structured_items, OUTPUT_JSON)

    success_count = sum(1 for item in structured_items if item["processing"]["status"] == "success")
    logger.info("结构化抽取完成")
    logger.info(f"总新闻数: {len(cleaned_news)}")
    logger.info(f"成功生成: {success_count}")


if __name__ == "__main__":
    main()
