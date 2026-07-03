"""
内容抽取服务
支持从 PDF 文件和网页链接中抽取文本内容
"""

import logging
import re
from io import BytesIO
from typing import Any
from urllib.parse import urlparse

import pdfplumber
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_content: bytes) -> dict[str, Any]:
    """从 PDF 文件中抽取文本。"""
    try:
        text_parts = []
        with pdfplumber.open(BytesIO(file_content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

        full_text = "\n\n".join(text_parts).strip()
        if not full_text:
            return {"success": False, "error": "PDF 中未提取到文本内容", "text": ""}

        # 简单清理
        full_text = re.sub(r"\n{3,}", "\n\n", full_text)

        return {
            "success": True,
            "text": full_text,
            "pages": len(pdf.pages),
        }
    except Exception as e:
        logger.error(f"PDF 解析失败: {e}")
        return {"success": False, "error": f"PDF 解析失败: {str(e)}", "text": ""}


def extract_text_from_url(url: str, timeout: int = 15) -> dict[str, Any]:
    """从网页链接中抽取文章正文。"""
    try:
        # 基础 URL 校验
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return {"success": False, "error": "无效的 URL", "text": ""}

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        # 自动检测编码
        response.encoding = response.apparent_encoding

        soup = BeautifulSoup(response.text, "html.parser")

        # 移除无关标签
        for tag in soup(["script", "style", "nav", "header", "footer", "aside", "advertisement"]):
            tag.decompose()

        # 优先尝试获取 article 标签内容
        article = soup.find("article")
        if article:
            text = article.get_text(separator="\n", strip=True)
        else:
            # 尝试获取 main 内容
            main = soup.find("main")
            if main:
                text = main.get_text(separator="\n", strip=True)
            else:
                # 兜底：获取 body 内容
                body = soup.find("body")
                if body:
                    text = body.get_text(separator="\n", strip=True)
                else:
                    text = soup.get_text(separator="\n", strip=True)

        # 清理文本
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)

        if not text or len(text) < 50:
            return {"success": False, "error": "网页内容过短，可能未正确解析", "text": text}

        # 尝试提取标题
        title = ""
        if soup.find("h1"):
            title = soup.find("h1").get_text(strip=True)
        elif soup.title:
            title = soup.title.get_text(strip=True)

        return {
            "success": True,
            "text": text,
            "title": title,
            "url": url,
        }
    except requests.RequestException as e:
        logger.error(f"网页抓取失败: {e}")
        return {"success": False, "error": f"网页抓取失败: {str(e)}", "text": ""}
    except Exception as e:
        logger.error(f"网页解析失败: {e}")
        return {"success": False, "error": f"网页解析失败: {str(e)}", "text": ""}


def truncate_text(text: str, max_chars: int = 12000) -> str:
    """截断文本，避免超出模型上下文。"""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[内容已截断]"
