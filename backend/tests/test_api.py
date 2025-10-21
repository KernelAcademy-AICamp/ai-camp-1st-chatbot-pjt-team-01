"""API 테스트"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """헬스 체크 테스트"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "app_name" in data


def test_market_kpis():
    """KPI 데이터 조회 테스트"""
    response = client.get("/api/market/kpis")
    assert response.status_code == 200
    data = response.json()
    assert "cpi" in data
    assert "gdp_qoq" in data
    assert "unemployment" in data


def test_market_trends():
    """트렌드 데이터 조회 테스트"""
    response = client.get("/api/market/trends")
    assert response.status_code == 200
    data = response.json()
    assert "cpi_series" in data
    assert len(data["cpi_series"]) > 0


def test_news():
    """뉴스 조회 테스트"""
    response = client.get("/api/market/news")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) > 0

