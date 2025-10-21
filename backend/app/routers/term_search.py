"""경제 용어 검색 라우터"""
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.deps import get_database
from app.models.term_search import TermSearchRequest, TermSearchResponse, TermSearchResult
from app.services.term_search_service import TermSearchService

router = APIRouter(prefix="/term-search", tags=["term-search"])


@router.post("/", response_model=TermSearchResponse)
async def search_economic_terms(
    request: TermSearchRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    경제 용어 벡터 검색

    사용자가 입력한 질문과 가장 유사한 경제 용어를 검색합니다.
    """
    try:
        # 검색 서비스 초기화
        search_service = TermSearchService(db)

        # 유사 용어 검색
        results = await search_service.search_similar_terms(
            query=request.query,
            top_k=request.top_k
        )

        # 응답 생성
        return TermSearchResponse(
            query=request.query,
            results=[TermSearchResult(**result) for result in results],
            count=len(results)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"검색 중 오류가 발생했습니다: {str(e)}"
        )
