"""시장 데이터 라우터"""
from fastapi import APIRouter
from app.models.common import KPIData, TrendsData, NewsResponse
from app.services.market_adapters import (
    generate_mock_kpis,
    generate_mock_trends,
    generate_mock_news
)

router = APIRouter(tags=["market"])


@router.get("/market/kpis", response_model=KPIData)
async def get_kpis():
    """
    주요 경제 지표 조회
    """
    return generate_mock_kpis()


@router.get("/market/trends", response_model=TrendsData)
async def get_trends():
    """
    경제 트렌드 시계열 데이터
    """
    return generate_mock_trends()


@router.get("/market/news", response_model=NewsResponse)
async def get_news():
    """
    경제 뉴스 조회
    """
    news_items = generate_mock_news()
    return NewsResponse(items=news_items)

