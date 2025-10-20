"""시장 데이터 어댑터 (Mock)"""
from datetime import datetime, timedelta
from typing import List
import random
from app.models.common import KPIData, TrendsData, TimeSeriesPoint, NewsItem


def generate_mock_kpis() -> KPIData:
    """
    주요 경제 지표 Mock 데이터
    실제 환경에서는 FRED, ECOS, KRX API 등으로 교체
    """
    return KPIData(
        cpi=110.5,
        cpi_change=2.3,
        gdp_qoq=0.6,
        gdp_yoy=2.2,
        unemployment=3.4,
        unemployment_change=-0.1,
        base_rate=3.50,
        base_rate_change=0.0,
        usdkrw=1335.50,
        usdkrw_change=5.20,
        spx=4783.45,
        spx_change=0.85,
        kospi=2655.20,
        kospi_change=1.12
    )


def generate_mock_trends() -> TrendsData:
    """
    시계열 트렌드 Mock 데이터
    """
    # 36개월 데이터
    dates = []
    now = datetime.now()
    for i in range(36):
        date = now - timedelta(days=30 * (35 - i))
        dates.append(date.strftime("%Y-%m"))
    
    # CPI 시리즈 (상승 트렌드)
    cpi_base = 100.0
    cpi_series = []
    for i, date in enumerate(dates):
        value = cpi_base + (i * 0.3) + random.uniform(-0.5, 0.5)
        cpi_series.append(TimeSeriesPoint(date=date, value=round(value, 2)))
    
    # 실업률 시리즈 (변동)
    unemployment_series = []
    for i, date in enumerate(dates):
        value = 3.5 + random.uniform(-0.5, 0.5)
        unemployment_series.append(TimeSeriesPoint(date=date, value=round(value, 2)))
    
    # 기준금리 시리즈 (단계적 변화)
    rate_series = []
    for i, date in enumerate(dates):
        if i < 12:
            value = 0.5
        elif i < 24:
            value = 1.25
        else:
            value = 3.5
        rate_series.append(TimeSeriesPoint(date=date, value=value))
    
    # GDP 성장률 시리즈 (분기별)
    gdp_series = []
    for i in range(0, 36, 3):
        if i < len(dates):
            value = 2.0 + random.uniform(-1.0, 1.5)
            gdp_series.append(TimeSeriesPoint(date=dates[i], value=round(value, 2)))
    
    return TrendsData(
        cpi_series=cpi_series,
        unemployment_series=unemployment_series,
        rate_series=rate_series,
        gdp_series=gdp_series
    )


def generate_mock_news() -> List[NewsItem]:
    """
    경제 뉴스 Mock 데이터
    실제 환경에서는 뉴스 API로 교체
    """
    return [
        NewsItem(
            title="한국은행, 기준금리 3.50% 동결",
            summary="한국은행 금융통화위원회가 기준금리를 현 수준에서 유지하기로 결정했다. 물가 안정세와 경기 회복을 고려한 조치.",
            url="https://example.com/news/1",
            source="한국은행",
            published_at="2024-01-15"
        ),
        NewsItem(
            title="12월 소비자물가 2.3% 상승",
            summary="지난달 소비자물가지수가 전년 동월 대비 2.3% 상승했다. 식료품과 에너지 가격 상승이 주요 원인.",
            url="https://example.com/news/2",
            source="통계청",
            published_at="2024-01-05"
        ),
        NewsItem(
            title="4분기 GDP 성장률 0.6% 기록",
            summary="지난해 4분기 국내총생산(GDP)이 전분기 대비 0.6% 성장했다. 수출 회복과 민간소비 증가가 기여.",
            url="https://example.com/news/3",
            source="한국은행",
            published_at="2024-01-25"
        ),
        NewsItem(
            title="실업률 3.4%로 소폭 개선",
            summary="12월 실업률이 3.4%를 기록하며 전월 대비 0.1%p 개선됐다. 고용시장 회복세 지속.",
            url="https://example.com/news/4",
            source="통계청",
            published_at="2024-01-12"
        ),
        NewsItem(
            title="원달러 환율 1,335원대 등락",
            summary="원달러 환율이 1,330~1,340원 사이에서 등락을 거듭하고 있다. 글로벌 금리 전망 불확실성이 변동 요인.",
            url="https://example.com/news/5",
            source="서울외국환중개",
            published_at="2024-01-20"
        ),
        NewsItem(
            title="코스피 2,655선 회복",
            summary="국내 증시가 상승세를 보이며 코스피가 2,655선을 회복했다. 반도체·자동차 업종이 상승 주도.",
            url="https://example.com/news/6",
            source="한국거래소",
            published_at="2024-01-18"
        )
    ]

