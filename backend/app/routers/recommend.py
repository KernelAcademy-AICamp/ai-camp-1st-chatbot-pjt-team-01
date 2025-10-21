"""자료 추천 라우터"""
from fastapi import APIRouter, HTTPException, Depends
from app.models.common import RecommendRequest, RecommendResponse, Bookmark
from app.services.openai_svc import generate_recommendations
from app.db.mongo import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime

router = APIRouter(tags=["recommend"])


@router.post("/recommend", response_model=RecommendResponse)
async def get_recommendations(request: RecommendRequest):
    """
    자료 추천 생성
    """
    try:
        items = await generate_recommendations(
            topic=request.topic,
            level=request.level,
            purpose=request.purpose
        )
        
        return RecommendResponse(items=items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"추천 생성 실패: {str(e)}")


@router.post("/recommend/bookmark")
async def create_bookmark(bookmark: Bookmark, db: AsyncIOMotorDatabase = Depends(get_database)):
    """
    북마크 저장
    """
    try:
        bookmark_dict = bookmark.model_dump()
        result = await db.bookmarks.insert_one(bookmark_dict)
        
        return {
            "id": str(result.inserted_id),
            "message": "북마크가 저장되었습니다."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"북마크 저장 실패: {str(e)}")


@router.get("/recommend/bookmarks")
async def get_bookmarks(db: AsyncIOMotorDatabase = Depends(get_database)):
    """
    북마크 목록 조회
    """
    try:
        cursor = db.bookmarks.find().sort("created_at", -1).limit(50)
        bookmarks = await cursor.to_list(length=50)
        
        # ObjectId를 문자열로 변환
        for bookmark in bookmarks:
            bookmark["id"] = str(bookmark.pop("_id"))
        
        return {"bookmarks": bookmarks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"북마크 조회 실패: {str(e)}")

