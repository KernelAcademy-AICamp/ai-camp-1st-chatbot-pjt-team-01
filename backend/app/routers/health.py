"""헬스 체크 라우터"""
from fastapi import APIRouter
from app.models.common import HealthResponse
from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """서비스 상태 확인"""
    return HealthResponse(
        status="ok",
        app_name=settings.APP_NAME
    )

