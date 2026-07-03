"""
Step 1: 数据层 - 读取原始新闻数据，进行清洗与标准化

功能：
1. 读取 JSONL 格式原始新闻数据
2. 检查每条记录的必要字段（标题、正文、来源、发布时间、原文链接）
3. 去除空值、空白值
4. 去除重复新闻（基于标题+URL）
5. 标准化发布时间格式
6. 输出清洗后的 JSON 文件
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 项目路径
BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_FILE = BASE_DIR / "data" / "raw_news.jsonl"
OUTPUT_FILE = BASE_DIR / "data" / "cleaned_news.json"

# 必要字段
REQUIRED_FIELDS = ["title", "content", "source", "published_at", "url"]


def read_jsonl(file_path: Path) -> list[dict[str, Any]]:
    """读取 JSONL 文件，返回记录列表。"""
    records: list[dict[str, Any]] = []
    if not file_path.exists():
        logger.error(f"文件不存在: {file_path}")
        return records

    with file_path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                logger.warning(f"第 {line_num} 行为空，已跳过")
                continue
            try:
                record = json.loads(line)
                records.append(record)
            except json.JSONDecodeError as e:
                logger.error(f"第 {line_num} 行 JSON 解析失败: {e}")

    logger.info(f"成功读取 {len(records)} 条原始记录")
    return records


def has_required_fields(record: dict[str, Any]) -> bool:
    """检查记录是否包含所有必要字段且不为空。"""
    for field in REQUIRED_FIELDS:
        value = record.get(field)
        if value is None:
            return False
        if isinstance(value, str) and value.strip() == "":
            return False
    return True


def normalize_date(date_str: str) -> str:
    """将发布时间标准化为 ISO 8601 格式（YYYY-MM-DD）。"""
    date_str = date_str.strip()
    # 尝试多种常见格式
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%Y年%m月%d日",
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B %Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    # 兜底：尝试提取 yyyy-mm-dd / yyyy/mm/dd 模式
    match = re.search(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", date_str)
    if match:
        year, month, day = match.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"

    # 无法解析则保留原值，由调用方决定是否丢弃
    return date_str


def is_valid_date(date_str: str) -> bool:
    """检查字符串是否为有效的 YYYY-MM-DD 日期。"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def clean_record(record: dict[str, Any]) -> dict[str, Any] | None:
    """清洗单条记录，返回清洗后的记录；若不符合要求则返回 None。"""
    if not has_required_fields(record):
        logger.warning(f"字段缺失或为空: {record.get('title', '<无标题>')}")
        return None

    cleaned = {
        "title": record["title"].strip(),
        "content": record["content"].strip(),
        "source": record["source"].strip(),
        "published_at": normalize_date(record["published_at"]),
        "url": record["url"].strip(),
    }

    # 去重和过滤后的二次校验
    if not cleaned["title"] or not cleaned["content"]:
        logger.warning(f"标题或正文为空: {cleaned.get('title', '<无标题>')}")
        return None

    if not is_valid_date(cleaned["published_at"]):
        logger.warning(f"日期格式无效: {cleaned['published_at']} - {cleaned['title']}")
        return None

    return cleaned


def remove_duplicates(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """基于标题+URL 去除重复记录，保留第一条。"""
    seen: set[str] = set()
    unique_records: list[dict[str, Any]] = []

    for record in records:
        key = f"{record['title'].lower()}|{record['url'].lower()}"
        if key in seen:
            logger.info(f"重复记录已移除: {record['title']}")
            continue
        seen.add(key)
        unique_records.append(record)

    return unique_records


def clean_data(raw_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """完整的数据清洗流程。"""
    logger.info("开始清洗数据...")

    # 步骤1：单条清洗与字段校验
    cleaned_records = []
    for record in raw_records:
        cleaned = clean_record(record)
        if cleaned:
            cleaned_records.append(cleaned)

    logger.info(f"字段校验后剩余 {len(cleaned_records)} 条记录")

    # 步骤2：去重
    unique_records = remove_duplicates(cleaned_records)
    logger.info(f"去重后剩余 {len(unique_records)} 条记录")

    # 步骤3：按发布时间排序（从新到旧）
    unique_records.sort(key=lambda x: x["published_at"], reverse=True)

    return unique_records


def save_json(records: list[dict[str, Any]], file_path: Path) -> None:
    """将清洗后的记录保存为格式化的 JSON 文件。"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    logger.info(f"清洗结果已保存: {file_path}")


def main() -> None:
    """主入口函数。"""
    logger.info(f"读取原始数据: {RAW_FILE}")
    raw_records = read_jsonl(RAW_FILE)

    if not raw_records:
        logger.warning("未读取到任何原始记录")
        return

    cleaned_records = clean_data(raw_records)
    save_json(cleaned_records, OUTPUT_FILE)

    logger.info("数据清洗完成")
    logger.info(f"原始记录数: {len(raw_records)}")
    logger.info(f"清洗后记录数: {len(cleaned_records)}")


if __name__ == "__main__":
    main()
