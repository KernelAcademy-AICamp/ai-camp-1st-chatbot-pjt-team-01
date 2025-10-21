"""의존성 주입"""
from typing import Optional
from app.db.mongo import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase


async def get_db() -> AsyncIOMotorDatabase:
    """데이터베이스 의존성"""
    return get_database()


async def get_database_or_none() -> Optional[AsyncIOMotorDatabase]:
    """데이터베이스 의존성 (연결 실패 시 None 반환)"""
    try:
        return get_database()
    except Exception:
        return None

