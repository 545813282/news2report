"""
AI舆情分析日报系统 - 后端配置
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = DATA_DIR / "output"

# OpenAI 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# 数据采集配置
NEWS_LIMIT = int(os.getenv("NEWS_LIMIT", "15"))
NEWS_SOURCES = os.getenv("NEWS_SOURCES", "rss,search").split(",")

# 输出配置
OUTPUT_MD_PATH = OUTPUT_DIR / "daily_report.md"
OUTPUT_HTML_PATH = OUTPUT_DIR / "daily_report.html"

# 确保目录存在
for d in (RAW_DIR, PROCESSED_DIR, OUTPUT_DIR):
    d.mkdir(parents=True, exist_ok=True)
