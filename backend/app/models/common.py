"""공통 데이터 모델"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ===== Q&A =====
class QARequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    context: Optional[str] = Field(None, max_length=5000)


class QAResponse(BaseModel):
    answer_md: str
    citations: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ===== 문제 생성 =====
class ProblemGenRequest(BaseModel):
    level: str = Field(..., pattern="^(basic|intermediate|advanced)$")
    topic: str = Field(..., pattern="^(macro|finance|trade|stats)$")
    count: int = Field(5, ge=1, le=20)
    style: str = Field("mcq", pattern="^(mcq|free)$")


class ProblemItem(BaseModel):
    question: str
    options: Optional[List[str]] = None
    answer: str
    explain: str


class ProblemGenResponse(BaseModel):
    items: List[ProblemItem]
    level: str
    topic: str


# ===== 자료 추천 =====
class RecommendRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200)
    level: str = Field(..., pattern="^(beginner|intermediate|advanced)$")
    purpose: str = Field(..., pattern="^(report|study|data|api)$")


class RecommendItem(BaseModel):
    title: str
    summary: str
    url: str
    tags: List[str] = []


class RecommendResponse(BaseModel):
    items: List[RecommendItem]


# ===== 시장 데이터 =====
class KPIData(BaseModel):
    cpi: float
    cpi_change: float
    gdp_qoq: float
    gdp_yoy: float
    unemployment: float
    unemployment_change: float
    base_rate: float
    base_rate_change: float
    usdkrw: float
    usdkrw_change: float
    spx: float
    spx_change: float
    kospi: float
    kospi_change: float
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TimeSeriesPoint(BaseModel):
    date: str
    value: float


class TrendsData(BaseModel):
    cpi_series: List[TimeSeriesPoint]
    unemployment_series: List[TimeSeriesPoint]
    rate_series: List[TimeSeriesPoint]
    gdp_series: List[TimeSeriesPoint]


class NewsItem(BaseModel):
    title: str
    summary: str
    url: str
    source: str
    published_at: str


class NewsResponse(BaseModel):
    items: List[NewsItem]


# ===== 북마크 =====
class Bookmark(BaseModel):
    title: str
    url: str
    tags: List[str] = []
    note: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ===== 헬스 체크 =====
class HealthResponse(BaseModel):
    status: str
    app_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

