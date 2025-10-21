"""경제 용어 검색 모델"""
from pydantic import BaseModel, Field
from typing import List


class TermSearchRequest(BaseModel):
    """용어 검색 요청"""
    query: str = Field(..., min_length=1, max_length=500, description="검색 질문")
    top_k: int = Field(default=3, ge=1, le=10, description="반환할 결과 개수")


class TermSearchResult(BaseModel):
    """용어 검색 결과"""
    term: str = Field(..., description="용어명")
    english: str = Field(default="", description="영문명")
    definition: str = Field(..., description="용어 정의")
    similarity: float = Field(..., description="유사도 (0-1)")
    similarity_percent: float = Field(..., description="유사도 백분율")


class TermSearchResponse(BaseModel):
    """용어 검색 응답"""
    query: str = Field(..., description="검색 쿼리")
    results: List[TermSearchResult] = Field(..., description="검색 결과")
    count: int = Field(..., description="결과 개수")
