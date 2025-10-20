"""MongoDB 연결 관리"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from app.core.config import settings

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

mongo = MongoDB()


async def connect_to_mongo():
    """MongoDB 연결 초기화"""
    try:
        mongo.client = AsyncIOMotorClient(settings.MONGO_URI)
        mongo.db = mongo.client[settings.MONGO_DB]
        # 연결 테스트
        await mongo.client.admin.command('ping')
        print(f"[OK] MongoDB Connected: {settings.MONGO_DB}")
    except Exception as e:
        print(f"[WARNING] MongoDB Connection Failed: {e}")
        print("[INFO] Application will run without MongoDB (bookmarks disabled)")


async def close_mongo_connection():
    """MongoDB 연결 종료"""
    if mongo.client:
        mongo.client.close()
        print("[OK] MongoDB Connection Closed")


def get_database() -> AsyncIOMotorDatabase:
    """데이터베이스 인스턴스 반환"""
    if mongo.db is None:
        raise RuntimeError("데이터베이스가 초기화되지 않았습니다.")
    return mongo.db

