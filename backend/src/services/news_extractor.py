"""
AI 新闻结构化抽取服务
支持单条和批量新闻的结构化抽取
"""

import json
import logging
import time
from datetime import datetime, timezone
from typing import Any

from openai import OpenAI
from pydantic import ValidationError

from src.config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
from src.schema.news_schema import StructuredNewsItem

logger = logging.getLogger(__name__)

# 结构化抽取 Prompt
SYSTEM_PROMPT = """你是一位专业的 AI 产业分析师。请根据用户提供的新闻原文，抽取并生成一份结构化的 AI 新闻分析报告。

要求：
1. 严格按照下方的 JSON Schema 输出，不要添加 schema 以外的字段。
2. 输出必须是合法 JSON，不要包含 Markdown 代码块标记。
3. title 使用原文标题，title_en 只在原文是英文时提供英文标题的中文翻译，或原文是中文时提供英文翻译（可选）。
4. category 必须从以下分类中选择：大模型、AI芯片、自动驾驶、机器人、AIGC、AI政策、AI应用、AI融资、AI安全、学术前沿、其他。
5. tags 请提取 3-8 个关键词标签。
6. source.name 使用原文来源名称，source.type 从：科技媒体、官方博客、社交媒体、学术平台、聚合平台、其他 中选择。
7. publish_time 必须是 ISO 8601 格式（如 2026-07-01T10:30:00+08:00），若原文只有日期则假设为当天 08:00:00+08:00。
8. language 根据原文语言选择：zh（中文）、en（英文）、zh-en（中英混合）。
9. original_text 由系统在模型输出后自动填充，你不需要在 JSON 中重复输出原文。
10. ai_summary 要求结构化：主体 + 动作 + 关键数据 + 影响，控制在 80-150 字。
11. ai_opinion.viewpoint 用一句话总结核心观点；significance 从 重大/重要/一般/轻微 中选择；impact_direction 从 积极/消极/中性/复杂 中选择。
12. entities 提取新闻中的关键实体（公司、产品、人物、机构、技术、事件），至少 2 个。
13. technologies 提取涉及的技术关键词，如没有则留空数组。
14. event_type 从以下选择：产品发布、技术突破、融资并购、政策监管、合作签约、安全争议、人事变动、业绩报告、学术发表、其他。
15. sentiment 给出整体情感标签（positive/negative/neutral/mixed）、-1 到 1 的分数、以及判断理由。
16. key_points 提取最多 5 条核心要点，每条一句，包含关键事实或数据。
17. relations 提取实体关系三元组（subject-predicate-object），至少 1 条，如没有明显关系可留空数组。

输出 Schema：
{
  "title": "string",
  "title_en": "string | null",
  "category": "string",
  "tags": ["string"],
  "source": {"name": "string", "name_en": "string | null", "type": "string", "url": "string"},
  "author": "string | null",
  "publish_time": "string",
  "language": "string",
  "translated_text": "string | null",
  "original_summary": "string | null",
  "ai_summary": "string",
  "ai_opinion": {"viewpoint": "string", "significance": "string", "impact_direction": "string"},
  "entities": [{"name": "string", "type": "string"}],
  "technologies": ["string"],
  "event_type": "string",
  "sentiment": {"overall": "string", "score": "number", "reason": "string"},
  "key_points": ["string"],
  "relations": [{"subject": "string", "predicate": "string", "object": "string"}]
}
"""


def build_user_prompt(news: dict[str, Any]) -> str:
    """为单条新闻构建用户输入 prompt。"""
    return f"""请对以下新闻进行结构化抽取：

标题：{news['title']}
来源：{news['source']}
发布时间：{news['published_at']}
原文链接：{news['url']}

正文：
{news['content']}
"""


def format_publish_time(publish_time: str) -> str:
    """将 YYYY-MM-DD 格式转换为 ISO 8601。"""
    return f"{publish_time}T08:00:00+08:00"


def extract_structured_news(
    client: OpenAI,
    news: dict[str, Any],
    news_id: str,
    batch_id: str,
    max_retries: int = 3,
) -> dict[str, Any] | None:
    """
    对单条新闻调用 OpenAI API 进行结构化抽取。
    """
    extracted_at = datetime.now(timezone.utc).isoformat()

    for attempt in range(max_retries):
        try:
            logger.info(f"正在抽取: {news['title'][:40]}... (尝试 {attempt + 1}/{max_retries})")

            temperature = 1.0 if OPENAI_MODEL == "kimi-for-coding" else 0.3
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": build_user_prompt(news)},
                ],
                response_format={"type": "json_object"},
                temperature=temperature,
                max_tokens=8192,
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
                "batch_id": batch_id,
                "status": "success",
                "retry_count": attempt,
                "error_msg": None,
            }

            # 使用 Pydantic 验证
            validated = StructuredNewsItem.model_validate(parsed)
            logger.info(f"抽取成功: {validated.title[:40]}...")
            return validated.model_dump()

        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            logger.warning(f"抽取失败 尝试 {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                logger.error(f"抽取失败 已达最大重试次数: {e}")
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
                        "batch_id": batch_id,
                        "status": "failed",
                        "retry_count": attempt,
                        "error_msg": str(e),
                    },
                }
        except Exception as e:
            logger.error(f"OpenAI API 调用异常: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                return None

    return None


def get_extractor_client() -> OpenAI | None:
    """获取 AI 抽取客户端，未配置 API Key 时返回 None。"""
    if not OPENAI_API_KEY:
        logger.error("未配置 OPENAI_API_KEY")
        return None
    return OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
