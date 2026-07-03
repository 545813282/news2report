"""
AI舆情分析日报系统 - FastAPI 接口
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from src.config import DATA_DIR, NEWS_LIMIT, OPENAI_API_KEY, OPENAI_MODEL

app = FastAPI(title="AI舆情分析日报系统", version="0.1.0")


class HealthResponse(BaseModel):
    status: str
    model: str
    news_limit: int


class UploadNewsRequest(BaseModel):
    title: str = Field(..., min_length=1, description="新闻标题")
    content: str = Field(..., min_length=10, description="新闻正文")
    source: str = Field(..., min_length=1, description="新闻来源")
    published_at: str = Field(..., description="发布时间，YYYY-MM-DD 格式")
    url: str = Field(default="", description="原文链接")
    language: str = Field(default="zh", description="语言：zh/en/zh-en")


class UploadNewsResponse(BaseModel):
    status: str
    id: str
    message: str
    structured: dict[str, Any] | None = None


class FetchUrlRequest(BaseModel):
    url: str = Field(..., min_length=1, description="网页链接")
    source: str = Field(default="", description="来源名称，留空自动提取")
    published_at: str = Field(default="", description="发布时间，YYYY-MM-DD，留空使用今天")
    language: str = Field(default="zh", description="语言：zh/en/zh-en")


class ExtractContentResponse(BaseModel):
    success: bool
    title: str = ""
    content: str = ""
    source: str = ""
    url: str = ""
    message: str = ""


@app.get("/api/", response_model=HealthResponse)
async def root():
    return HealthResponse(
        status="ok",
        model=OPENAI_MODEL,
        news_limit=NEWS_LIMIT,
    )


@app.get("/api/health")
async def health():
    return {"status": "healthy", "service": "news2report-backend"}


@app.get("/api/news")
async def get_news():
    """获取清洗后的原始新闻数据"""
    cleaned_file = DATA_DIR / "cleaned_news.json"
    if not cleaned_file.exists():
        return {"status": "error", "message": "新闻数据尚未生成"}

    with cleaned_file.open("r", encoding="utf-8") as f:
        news = json.load(f)

    return {
        "status": "ok",
        "total": len(news),
        "data": news,
    }


@app.get("/api/structured-news")
async def get_structured_news():
    """获取 AI 结构化后的新闻数据"""
    structured_file = DATA_DIR / "structured_news.json"
    if not structured_file.exists():
        return {"status": "error", "message": "结构化新闻数据尚未生成"}

    with structured_file.open("r", encoding="utf-8") as f:
        news = json.load(f)

    return {
        "status": "ok",
        "total": len(news),
        "data": news,
    }


def normalize_date(date_str: str) -> str:
    """将各种日期格式标准化为 YYYY-MM-DD。"""
    date_str = date_str.strip()
    # 尝试 ISO 格式直接返回日期部分
    if "T" in date_str:
        return date_str.split("T")[0]
    # 尝试 YYYY-MM-DD / YYYY/MM/DD
    match = re.search(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", date_str)
    if match:
        year, month, day = match.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"
    # 默认今天
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def read_json_file(file_path: Path) -> list[dict[str, Any]]:
    """读取 JSON 文件，不存在则返回空列表。"""
    if not file_path.exists():
        return []
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json_file(file_path: Path, data: list[dict[str, Any]]) -> None:
    """写入 JSON 文件。"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def append_jsonl_file(file_path: Path, record: dict[str, Any]) -> None:
    """追加写入 JSONL 文件。"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def generate_news_id(publish_time: str, existing_count: int) -> str:
    """生成新闻 ID。"""
    date_part = publish_time.replace("-", "")[:8]
    return f"news_{date_part}_{existing_count + 1:03d}"


def save_and_analyze_article(
    title: str,
    content: str,
    source: str,
    published_at: str,
    url: str,
    language: str,
) -> dict[str, Any]:
    """保存文章并调用 AI 进行结构化分析。"""
    from src.services.news_extractor import extract_structured_news, get_extractor_client

    client = get_extractor_client()
    if not client:
        raise HTTPException(status_code=500, detail="AI 客户端初始化失败")

    published_at = normalize_date(published_at)

    cleaned_news = read_json_file(DATA_DIR / "cleaned_news.json")
    structured_news = read_json_file(DATA_DIR / "structured_news.json")

    new_record = {
        "title": title.strip(),
        "content": content.strip(),
        "source": source.strip() or "未知来源",
        "published_at": published_at,
        "url": url.strip(),
        "language": language,
    }

    news_id = generate_news_id(published_at, len(cleaned_news))

    cleaned_news.append(new_record)
    write_json_file(DATA_DIR / "cleaned_news.json", cleaned_news)
    append_jsonl_file(DATA_DIR / "raw_news.jsonl", new_record)

    batch_id = datetime.now(timezone.utc).strftime("upload_%Y%m%d_%H%M%S")
    structured = extract_structured_news(client, new_record, news_id, batch_id)

    if not structured:
        raise HTTPException(status_code=500, detail="AI 结构化抽取失败")

    structured_news.append(structured)
    write_json_file(DATA_DIR / "structured_news.json", structured_news)
    append_jsonl_file(DATA_DIR / "structured_news.jsonl", structured)

    return structured


@app.post("/api/upload-news", response_model=UploadNewsResponse)
async def upload_news(request: UploadNewsRequest):
    """
    上传新文章，实时调用 AI 进行结构化分析，并追加到数据文件中。
    """
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="未配置 AI API Key，无法进行分析")

    structured = save_and_analyze_article(
        title=request.title,
        content=request.content,
        source=request.source,
        published_at=request.published_at,
        url=request.url,
        language=request.language,
    )

    return UploadNewsResponse(
        status="ok",
        id=structured["id"],
        message="文章上传并成功完成 AI 结构化分析",
        structured=structured,
    )


@app.post("/api/upload-pdf", response_model=UploadNewsResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    title: str = "",
    source: str = "",
    published_at: str = "",
    url: str = "",
    language: str = "zh",
):
    """
    上传 PDF 文件，抽取文本后实时调用 AI 进行结构化分析。
    """
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="未配置 AI API Key，无法进行分析")

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="请上传 PDF 文件")

    from src.services.content_extractor import extract_text_from_pdf, truncate_text

    content = await file.read()
    extract_result = extract_text_from_pdf(content)

    if not extract_result["success"]:
        raise HTTPException(status_code=400, detail=extract_result["error"])

    pdf_text = truncate_text(extract_result["text"])
    pdf_title = title.strip() or file.filename.replace(".pdf", "").replace("_", " ")
    pdf_source = source.strip() or "PDF 上传"

    structured = save_and_analyze_article(
        title=pdf_title,
        content=pdf_text,
        source=pdf_source,
        published_at=published_at,
        url=url,
        language=language,
    )

    return UploadNewsResponse(
        status="ok",
        id=structured["id"],
        message=f"PDF 上传并成功完成 AI 结构化分析（共 {extract_result.get('pages', 0)} 页）",
        structured=structured,
    )


@app.post("/api/fetch-url")
async def fetch_url(request: FetchUrlRequest):
    """
    抓取网页链接内容，可选择直接分析或仅预览内容。
    """
    from src.services.content_extractor import extract_text_from_url, truncate_text

    extract_result = extract_text_from_url(request.url)
    if not extract_result["success"]:
        raise HTTPException(status_code=400, detail=extract_result["error"])

    if not OPENAI_API_KEY:
        return ExtractContentResponse(
            success=True,
            title=extract_result.get("title", ""),
            content=truncate_text(extract_result["text"]),
            source=request.source.strip() or extract_result.get("source", "网页抓取"),
            url=request.url,
            message="内容抓取成功，但尚未配置 AI API Key，无法自动分析",
        )

    # 自动分析
    title = request.source.strip() or extract_result.get("title", "")
    source = request.source.strip() or extract_result.get("source", "网页抓取")
    published_at = request.published_at or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    structured = save_and_analyze_article(
        title=title,
        content=truncate_text(extract_result["text"]),
        source=source,
        published_at=published_at,
        url=request.url,
        language=request.language,
    )

    return UploadNewsResponse(
        status="ok",
        id=structured["id"],
        message="网页抓取并成功完成 AI 结构化分析",
        structured=structured,
    )
