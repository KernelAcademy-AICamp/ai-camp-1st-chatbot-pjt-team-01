from __future__ import annotations
from pydantic import BaseModel, Field, conint, validator
from typing import List, Optional, Literal
from datetime import datetime

Topic = Literal["macro", "finance", "trade", "stats"]
Level = Literal["basic", "intermediate", "advanced"]
Style = Literal["mcq", "free"]

class ProblemItem(BaseModel):
    question: str = Field(..., min_length=8, max_length=200)
    options: Optional[List[str]] = None  # mcq일 때만 필수(라우터에서 검증)
    answer: str = Field(..., min_length=1, max_length=200)
    explanation: str = Field(..., min_length=10, max_length=800)
    topic: Topic
    level: Level

    @validator("options", always=False)
    def non_empty_options(cls, v):
        if v is not None:
            v = [opt for opt in v if (opt or "").strip()]
            if len(v) == 0:
                raise ValueError("options가 비어 있습니다.")
        return v

class ProblemRequest(BaseModel):
    topic: Topic
    level: Level
    style: Style = "mcq"
    count: conint(ge=1, le=20) = 5

class ProblemResponse(BaseModel):
    items: List[ProblemItem]
    topic: Topic
    level: Level
    created_at: datetime = Field(default_factory=datetime.utcnow)

# 채점 관련 모델들
class AnswerItem(BaseModel):
    question_id: str = Field(..., min_length=1)
    user_answer: str = Field(..., min_length=1)

class GradeRequest(BaseModel):
    answers: List[AnswerItem] = Field(..., min_items=1)

class GradeResult(BaseModel):
    question_id: str
    is_correct: bool
    correct_answer: str

class GradeResponse(BaseModel):
    total: int
    correct: int
    score: int
    results: List[GradeResult]

# 퀴즈 시도 관련 모델들
class QuizAttemptItem(BaseModel):
    question_id: str = Field(..., description="문제 ID")
    user_answer: str = Field(..., description="사용자 답안")
    correct_answer: str = Field(..., description="정답")
    is_correct: bool = Field(..., description="정답 여부")

class QuizAttemptIn(BaseModel):
    problemset_id: Optional[str] = Field(None, description="문제 세트 ID (선택사항)")
    items: List[AnswerItem] = Field(..., min_items=1, description="답안 목록")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="시작 시간")
    finished_at: datetime = Field(default_factory=datetime.utcnow, description="완료 시간")

class QuizAttemptOut(BaseModel):
    attempt_id: str = Field(..., description="시도 ID")
    problemset_id: Optional[str] = Field(None, description="문제 세트 ID")
    total: int = Field(..., description="총 문제 수")
    correct: int = Field(..., description="정답 수")
    score: int = Field(..., description="점수 (백분율)")
    items: List[QuizAttemptItem] = Field(..., description="문항별 채점 결과")
    started_at: datetime = Field(..., description="시작 시간")
    finished_at: datetime = Field(..., description="완료 시간")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성 시간")

class QuizAttemptsResponse(BaseModel):
    items: List[QuizAttemptOut] = Field(..., description="퀴즈 시도 목록")
    total: int = Field(..., description="전체 개수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    pages: int = Field(..., description="전체 페이지 수")

# 재시도 문제 생성 관련 모델들
class RetryRequest(BaseModel):
    attempt_id: str = Field(..., description="시도 ID")
    model: str = Field(default="gpt-4o-mini", description="사용할 LLM 모델")
    num_questions: int = Field(default=5, ge=1, le=10, description="생성할 문제 수")

class RetryProblemItem(BaseModel):
    question: str = Field(..., min_length=8, max_length=200)
    options: List[str] = Field(..., min_items=4, max_items=4)
    answer: str = Field(..., min_length=1, max_length=200)
    explanation: str = Field(..., min_length=10, max_length=800)
    topic: Topic
    level: Level

class RetryResponse(BaseModel):
    attempt_id: str = Field(..., description="시도 ID")
    count: int = Field(..., description="생성된 문제 수")
    problems: List[RetryProblemItem] = Field(..., description="생성된 문제 목록")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성 시간")