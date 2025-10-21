import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import settings
from app.db.mongo import get_database
from app.deps import get_database_or_none

# 로거 설정
logger = logging.getLogger("econ.demo")

router = APIRouter(tags=["demo"], prefix="/demo")

def check_demo_mode():
    """DEMO 모드에서만 접근 가능한지 확인"""
    if not settings.DEMO:
        raise HTTPException(status_code=403, detail="DEMO 모드에서만 사용 가능합니다.")

@router.post("/reset", summary="데이터베이스 초기화")
async def reset_database(
    db: AsyncIOMotorDatabase = Depends(get_database_or_none)
):
    """
    DEMO 모드에서 데이터베이스 컬렉션을 초기화합니다.
    
    - **problems**: 문제 컬렉션 삭제
    - **quiz_attempts**: 퀴즈 시도 컬렉션 삭제  
    - **retry_problems**: 재시도 문제 컬렉션 삭제
    """
    check_demo_mode()
    
    try:
        if db is None:
            return {
                "message": "MongoDB 연결 없음 - DEMO 모드에서는 더미 데이터 사용",
                "demo_mode": True,
                "reset_results": {"note": "MongoDB 연결이 없어 실제 초기화는 수행되지 않았습니다."}
            }
        
        # 컬렉션 초기화
        collections_to_reset = ["problems", "quiz_attempts", "retry_problems"]
        results = {}
        
        for collection_name in collections_to_reset:
            try:
                result = await db[collection_name].delete_many({})
                results[collection_name] = result.deleted_count
                logger.info(f"[DEMO] {collection_name} 컬렉션 초기화: {result.deleted_count}개 문서 삭제")
            except Exception as e:
                logger.error(f"[DEMO] {collection_name} 컬렉션 초기화 실패: {e}")
                results[collection_name] = f"오류: {str(e)}"
        
        return {
            "message": "데이터베이스 초기화 완료",
            "demo_mode": True,
            "reset_results": results
        }
        
    except Exception as e:
        logger.error(f"[DEMO] 데이터베이스 초기화 실패: {e}")
        raise HTTPException(status_code=500, detail=f"초기화 실패: {str(e)}")

@router.post("/seed", summary="샘플 데이터 삽입")
async def seed_database(
    db: AsyncIOMotorDatabase = Depends(get_database_or_none)
):
    """
    DEMO 모드에서 샘플 데이터를 삽입합니다.
    
    - **problems**: 샘플 문제 데이터 삽입
    - **quiz_attempts**: 샘플 퀴즈 시도 데이터 삽입
    """
    check_demo_mode()
    
    try:
        if db is None:
            return {
                "message": "MongoDB 연결 없음 - DEMO 모드에서는 더미 데이터 사용",
                "demo_mode": True,
                "inserted": {"note": "MongoDB 연결이 없어 실제 삽입은 수행되지 않았습니다."}
            }
        
        from app.services.demo_service import load_sample_problems
        
        # 샘플 문제 데이터 로드
        sample_data = load_sample_problems()
        
        # 문제 데이터 삽입
        problems_inserted = 0
        if sample_data.get("items"):
            for item in sample_data["items"]:
                problem_doc = {
                    "items": [item],
                    "topic": item.get("topic", "macro"),
                    "level": item.get("level", "basic"),
                    "created_at": "2024-01-01T00:00:00Z"
                }
                await db["problems"].insert_one(problem_doc)
                problems_inserted += 1
        
        # 샘플 퀴즈 시도 데이터 생성
        sample_attempt = {
            "attempt_id": "demo-attempt-001",
            "problemset_id": None,
            "total": 3,
            "correct": 2,
            "score": 67,
            "items": [
                {
                    "question_id": "demo-q1",
                    "user_answer": "A",
                    "correct_answer": "A",
                    "is_correct": True
                },
                {
                    "question_id": "demo-q2", 
                    "user_answer": "B",
                    "correct_answer": "C",
                    "is_correct": False
                },
                {
                    "question_id": "demo-q3",
                    "user_answer": "D",
                    "correct_answer": "D", 
                    "is_correct": True
                }
            ],
            "started_at": "2024-01-01T10:00:00Z",
            "finished_at": "2024-01-01T10:15:00Z",
            "created_at": "2024-01-01T10:15:00Z"
        }
        
        await db["quiz_attempts"].insert_one(sample_attempt)
        
        logger.info(f"[DEMO] 샘플 데이터 삽입 완료: {problems_inserted}개 문제, 1개 시도")
        
        return {
            "message": "샘플 데이터 삽입 완료",
            "demo_mode": True,
            "inserted": {
                "problems": problems_inserted,
                "quiz_attempts": 1
            }
        }
        
    except Exception as e:
        logger.error(f"[DEMO] 샘플 데이터 삽입 실패: {e}")
        raise HTTPException(status_code=500, detail=f"데이터 삽입 실패: {str(e)}")

@router.get("/status", summary="DEMO 상태 확인")
async def get_demo_status(
    db: AsyncIOMotorDatabase = Depends(get_database_or_none)
):
    """
    DEMO 모드 상태와 데이터베이스 통계를 확인합니다.
    
    - **demo**: DEMO 모드 활성화 여부
    - **counts**: 각 컬렉션의 문서 수
    """
    check_demo_mode()
    
    try:
        if db is None:
            return {
                "demo": True,
                "message": "DEMO 모드가 활성화되어 있습니다 (MongoDB 연결 없음)",
                "counts": {"note": "MongoDB 연결이 없어 카운트를 조회할 수 없습니다."},
                "settings": {
                    "demo_mode": settings.DEMO,
                    "app_name": settings.APP_NAME,
                    "mongo_db": settings.MONGO_DB
                }
            }
        
        # 컬렉션별 문서 수 조회
        counts = {}
        collections = ["problems", "quiz_attempts", "retry_problems"]
        
        for collection_name in collections:
            try:
                count = await db[collection_name].count_documents({})
                counts[collection_name] = count
            except Exception as e:
                logger.error(f"[DEMO] {collection_name} 카운트 실패: {e}")
                counts[collection_name] = f"오류: {str(e)}"
        
        return {
            "demo": True,
            "message": "DEMO 모드가 활성화되어 있습니다",
            "counts": counts,
            "settings": {
                "demo_mode": settings.DEMO,
                "app_name": settings.APP_NAME,
                "mongo_db": settings.MONGO_DB
            }
        }
        
    except Exception as e:
        logger.error(f"[DEMO] 상태 확인 실패: {e}")
        raise HTTPException(status_code=500, detail=f"상태 확인 실패: {str(e)}")
