"""
AI舆情分析日报系统 - FastAPI 接口
"""
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from src.config import (
    DAILY_REPORT_HOUR,
    DAILY_REPORT_MINUTE,
    DATA_DIR,
    NEWS_LIMIT,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)
from src.db import get_upload_record, init_db, insert_upload_record
from src.services.daily_report_generator import (
    generate_daily_report,
    get_latest_report,
    generate_daily_report_pdf,
    OUTPUT_DIR,
)
from src.services.report_generator import generate_reports

app = FastAPI(title="AI舆情分析日报系统", version="0.1.0")


@app.on_event("startup")
async def startup_event():
    """服务启动时初始化 SQLite 数据库和日报定时任务。"""
    init_db()
    _init_scheduler()


@app.on_event("shutdown")
async def shutdown_event():
    """服务关闭时停止调度器。"""
    _stop_scheduler()


def _init_scheduler():
    """初始化 APScheduler，每天固定时间自动生成日报。"""
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.cron import CronTrigger

        scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")
        scheduler.add_job(
            _scheduled_daily_report,
            CronTrigger(hour=DAILY_REPORT_HOUR, minute=DAILY_REPORT_MINUTE),
            id="daily_report_job",
            replace_existing=True,
        )
        scheduler.start()
        logger.info(
            "日报定时任务已启动: 每天 %02d:%02d",
            DAILY_REPORT_HOUR,
            DAILY_REPORT_MINUTE,
        )
        app.state.scheduler = scheduler
    except Exception as e:
        logger.error("初始化日报定时任务失败: %s", e)


def _stop_scheduler():
    """停止调度器。"""
    scheduler = getattr(app.state, "scheduler", None)
    if scheduler:
        scheduler.shutdown()
        logger.info("日报定时任务已停止")


async def _scheduled_daily_report():
    """定时任务：生成当日日报。"""
    try:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        logger.info("定时任务触发，正在生成 %s 的日报", today)
        generate_daily_report(date_str=today, force=True)
    except Exception as e:
        logger.exception("定时生成日报失败: %s", e)


@app.get("/api/daily-report")
async def daily_report(date: str | None = None, force: bool = False):
    """获取或生成 AI 领域日报。"""
    try:
        return generate_daily_report(date_str=date, force=force)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception("日报生成失败: %s", e)
        raise HTTPException(status_code=500, detail=f"日报生成失败: {e}") from e


@app.post("/api/daily-report/generate")
async def generate_daily_report_endpoint(date: str | None = None, force: bool = True):
    """强制重新生成 AI 领域日报。"""
    try:
        return generate_daily_report(date_str=date, force=force)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception("日报生成失败: %s", e)
        raise HTTPException(status_code=500, detail=f"日报生成失败: {e}") from e


@app.get("/api/daily-report/pdf")
async def download_daily_report_pdf(date: str | None = None):
    """下载指定日期的日报 PDF，若不存在则先生成。"""
    try:
        target_date = date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        pdf_path = OUTPUT_DIR / f"daily_report_{target_date}.pdf"

        if not pdf_path.exists():
            generate_daily_report_pdf(date_str=target_date)

        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail="日报 PDF 生成失败")

        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"daily_report_{target_date}.pdf",
        )
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("生成日报 PDF 失败: %s", e)
        raise HTTPException(status_code=500, detail=f"生成日报 PDF 失败: {e}") from e


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
    upload_type: str,
    pdf_pages: int | None = None,
) -> dict[str, Any]:
    """保存文章、调用 AI 进行结构化分析、生成报告并写入数据库。"""
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

    # 生成 AI 分析报告 PDF 和结构化分析报告 PDF
    report_pdf_path, structured_pdf_path = generate_reports(structured)
    if report_pdf_path:
        structured["report_pdf_path"] = report_pdf_path
    if structured_pdf_path:
        structured["structured_pdf_path"] = structured_pdf_path

    # 写入 SQLite 数据库
    insert_upload_record(
        record_id=news_id,
        upload_type=upload_type,
        title=new_record["title"],
        source=new_record["source"],
        url=new_record["url"],
        language=new_record["language"],
        published_at=published_at,
        content=new_record["content"],
        structured=structured,
        report_pdf_path=report_pdf_path,
        structured_pdf_path=structured_pdf_path,
        pdf_pages=pdf_pages,
    )

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
        upload_type="manual",
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
        upload_type="pdf",
        pdf_pages=extract_result.get("pages"),
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
        upload_type="url",
    )

    return UploadNewsResponse(
        status="ok",
        id=structured["id"],
        message="网页抓取并成功完成 AI 结构化分析",
        structured=structured,
    )


@app.get("/api/reports/{record_id}/analysis")
async def download_analysis_report(record_id: str):
    """下载 AI 分析报告 PDF。"""
    record = get_upload_record(record_id)
    if not record or not record.get("report_pdf_path"):
        raise HTTPException(status_code=404, detail="报告不存在")

    pdf_path = Path(record["report_pdf_path"])
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="报告文件已丢失")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"{record_id}_analysis_report.pdf",
    )


@app.get("/api/reports/{record_id}/structured")
async def download_structured_report(record_id: str):
    """下载结构化分析报告 PDF。"""
    record = get_upload_record(record_id)
    if not record or not record.get("structured_pdf_path"):
        raise HTTPException(status_code=404, detail="报告不存在")

    pdf_path = Path(record["structured_pdf_path"])
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="报告文件已丢失")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"{record_id}_structured_report.pdf",
    )


@app.get("/api/reports/{record_id}/original")
async def download_original_text(record_id: str):
    """下载原文 TXT。"""
    record = get_upload_record(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    original_path = DATA_DIR / "reports" / record_id / "original_text.txt"
    if not original_path.exists():
        # 兼容旧数据：从数据库内容生成
        if not record.get("content"):
            raise HTTPException(status_code=404, detail="原文不存在")
        original_path.parent.mkdir(parents=True, exist_ok=True)
        original_path.write_text(record["content"], encoding="utf-8")

    return FileResponse(
        original_path,
        media_type="text/plain; charset=utf-8",
        filename=f"{record_id}_original_text.txt",
    )
