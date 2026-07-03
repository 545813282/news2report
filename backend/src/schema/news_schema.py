"""
AI舆情分析日报系统 - 新闻结构化数据模型 (Pydantic)
对应数据模型版本: 1.0.0
"""

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, HttpUrl


class Category(str, Enum):
    """新闻顶层分类"""
    LLM = "大模型"
    CHIP = "AI芯片"
    AUTONOMOUS = "自动驾驶"
    ROBOT = "机器人"
    AIGC = "AIGC"
    POLICY = "AI政策"
    APPLICATION = "AI应用"
    FINANCE = "AI融资"
    SAFETY = "AI安全"
    ACADEMIC = "学术前沿"
    OTHER = "其他"


class SourceType(str, Enum):
    """来源类型"""
    TECH_MEDIA = "科技媒体"
    OFFICIAL_BLOG = "官方博客"
    SOCIAL_MEDIA = "社交媒体"
    ACADEMIC = "学术平台"
    AGGREGATOR = "聚合平台"
    OTHER = "其他"


class Language(str, Enum):
    """原文语言"""
    ZH = "zh"
    EN = "en"
    ZH_EN = "zh-en"


class Significance(str, Enum):
    """事件重要性评级"""
    MAJOR = "重大"
    IMPORTANT = "重要"
    NORMAL = "一般"
    MINOR = "轻微"


class ImpactDirection(str, Enum):
    """整体影响方向"""
    POSITIVE = "积极"
    NEGATIVE = "消极"
    NEUTRAL = "中性"
    COMPLEX = "复杂"


class EventType(str, Enum):
    """事件类型"""
    PRODUCT_RELEASE = "产品发布"
    TECH_BREAKTHROUGH = "技术突破"
    FINANCE_MA = "融资并购"
    POLICY_REGULATION = "政策监管"
    PARTNERSHIP = "合作签约"
    SAFETY_CONTROVERSY = "安全争议"
    PERSONNEL = "人事变动"
    EARNINGS = "业绩报告"
    ACADEMIC = "学术发表"
    OTHER = "其他"


class SentimentLabel(str, Enum):
    """情感标签"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class ProcessingStatus(str, Enum):
    """处理状态"""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


class Source(BaseModel):
    """新闻来源信息"""
    name: str = Field(description="来源名称，如：机器之心")
    name_en: str | None = Field(default=None, description="来源英文名称，如：Synced")
    type: SourceType = Field(default=SourceType.TECH_MEDIA, description="来源类型")
    url: str = Field(description="来源链接")


class AIOpinion(BaseModel):
    """AI观点"""
    viewpoint: str = Field(description="核心观点一句话总结")
    significance: Significance = Field(description="事件重要性评级")
    impact_direction: ImpactDirection = Field(description="整体影响方向判断")


class Entity(BaseModel):
    """命名实体"""
    name: str = Field(description="实体名称")
    type: str = Field(description="实体类型，如：公司、产品、人物、机构、技术、事件")


class Sentiment(BaseModel):
    """情感分析"""
    overall: SentimentLabel = Field(description="整体情感标签")
    score: float = Field(ge=-1, le=1, description="情感分数，范围 -1 到 1")
    reason: str = Field(description="情感判断理由")


class Relation(BaseModel):
    """实体关系三元组"""
    subject: str = Field(description="主体")
    predicate: str = Field(description="关系/动作")
    object: str = Field(description="客体")


class ProcessingMeta(BaseModel):
    """处理元数据"""
    extracted_at: str = Field(description="抽取时间，ISO 8601格式")
    model: str = Field(description="使用的AI模型")
    batch_id: str = Field(description="批次ID")
    status: ProcessingStatus = Field(description="处理状态")
    retry_count: int = Field(default=0, description="重试次数")
    error_msg: str | None = Field(default=None, description="错误信息")


class StructuredNewsItem(BaseModel):
    """
    单条新闻的结构化数据模型
    """
    # ========== 基础信息层 ==========
    id: str = Field(description="全局唯一标识")
    title: str = Field(description="新闻标题")
    title_en: str | None = Field(default=None, description="英文标题")
    category: Category = Field(description="顶层分类")
    tags: list[str] = Field(default_factory=list, description="相关标签")
    source: Source = Field(description="来源信息")
    author: str | None = Field(default=None, description="作者")
    publish_time: str = Field(description="发布时间，ISO 8601格式")
    language: Language = Field(description="原文语言")
    original_text: str = Field(default="", description="新闻原始正文（由系统注入，模型输出可省略）")
    translated_text: str | None = Field(default=None, description="翻译后的文本")
    original_summary: str | None = Field(default=None, description="来源网站自带摘要")

    # ========== AI结构化层 ==========
    ai_summary: str = Field(description="AI摘要：主体+动作+关键数据+影响")
    ai_opinion: AIOpinion = Field(description="AI观点")
    entities: list[Entity] = Field(default_factory=list, description="命名实体")
    technologies: list[str] = Field(default_factory=list, description="技术关键词")
    event_type: EventType = Field(description="事件类型")
    sentiment: Sentiment = Field(description="情感分析")
    key_points: list[str] = Field(default_factory=list, max_length=5, description="核心要点，最多5条")
    relations: list[Relation] = Field(default_factory=list, description="实体关系三元组")

    # ========== 处理元数据层 ==========
    processing: ProcessingMeta = Field(description="处理元数据")


class StructuredNewsOutput(BaseModel):
    """批量结构化新闻输出"""
    items: list[StructuredNewsItem] = Field(description="结构化新闻列表")
