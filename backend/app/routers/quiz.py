import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
import uuid
import csv
import io
import json

from app.models.problems import (
    QuizAttemptIn, QuizAttemptOut, QuizAttemptItem, 
    GradeRequest, GradeResponse, AnswerItem, QuizAttemptsResponse,
    RetryRequest, RetryResponse, RetryProblemItem
)
from app.db.mongo import get_database, mongo
from app.services.llm_service import generate_retry_problems_payload

# 로거 설정
logger = logging.getLogger("econ.quiz")

router = APIRouter(tags=["quiz"], prefix="/quiz")

def get_database_or_none() -> Optional[AsyncIOMotorDatabase]:
    """데이터베이스 인스턴스 반환 (연결 실패 시 None 반환)"""
    try:
        return get_database()
    except RuntimeError:
        logger.warning("MongoDB 연결 실패 - in-memory fallback 모드로 동작")
        return None

# In-memory fallback 저장소
_in_memory_attempts: List[dict] = []

async def _grade_answers_fallback(answers: List[AnswerItem]) -> GradeResponse:
    """
    MongoDB 연결 실패 시 더미 데이터로 채점합니다.
    """
    # 더미 정답 데이터
    dummy_answers = {
        "1": "A", "2": "D", "3": "B", "4": "C", "5": "A",
        "6": "B", "7": "C", "8": "D", "9": "A", "10": "B"
    }
    
    results = []
    correct_count = 0
    
    for answer in answers:
        correct_answer = dummy_answers.get(answer.question_id, "A")
        is_correct = answer.user_answer.strip().upper() == correct_answer.strip().upper()
        
        if is_correct:
            correct_count += 1
        
        results.append({
            "question_id": answer.question_id,
            "is_correct": is_correct,
            "correct_answer": correct_answer
        })
    
    total = len(answers)
    score = int((correct_count / total) * 100) if total > 0 else 0
    
    return GradeResponse(
        total=total,
        correct=correct_count,
        score=score,
        results=results
    )

@router.post("/attempts", response_model=QuizAttemptOut, summary="퀴즈 시도 및 채점")
async def create_quiz_attempt(
    attempt_data: QuizAttemptIn,
    db: Optional[AsyncIOMotorDatabase] = Depends(get_database_or_none),
):
    """
    퀴즈 시도를 생성하고 채점한 후 결과를 저장합니다.
    
    - **problemset_id**: 문제 세트 ID (선택사항)
    - **items**: 답안 목록
    - **started_at**: 시작 시간
    - **finished_at**: 완료 시간
    """
    try:
        # 고유 시도 ID 생성
        attempt_id = str(uuid.uuid4())
        
        # 기존 채점 API 로직 활용
        grade_request = GradeRequest(answers=attempt_data.items)
        
        # 채점 수행 (MongoDB 연결 상태에 따라 다른 방식 사용)
        if db is not None:
            try:
                # MongoDB에서 정답 조회하여 채점
                question_ids = [answer.question_id for answer in attempt_data.items]
                
                problems_cursor = db["problems"].find(
                    {"items.question_id": {"$in": question_ids}},
                    {"items": 1}
                )
                problems_docs = await problems_cursor.to_list(length=None)
                
                # 문제 데이터를 딕셔너리로 변환
                correct_answers = {}
                for doc in problems_docs:
                    for item in doc.get("items", []):
                        if "question_id" in item:
                            correct_answers[item["question_id"]] = item["answer"]
                
                # 채점 결과 생성
                results = []
                correct_count = 0
                
                for answer in attempt_data.items:
                    correct_answer = correct_answers.get(answer.question_id, "정답 없음")
                    is_correct = answer.user_answer.strip().upper() == correct_answer.strip().upper()
                    
                    if is_correct:
                        correct_count += 1
                    
                    results.append({
                        "question_id": answer.question_id,
                        "is_correct": is_correct,
                        "correct_answer": correct_answer
                    })
                
                total = len(attempt_data.items)
                score = int((correct_count / total) * 100) if total > 0 else 0
                
                grade_result = GradeResponse(
                    total=total,
                    correct=correct_count,
                    score=score,
                    results=results
                )
                
            except Exception as e:
                logger.warning(f"MongoDB 채점 실패, fallback 사용: {e}")
                grade_result = await _grade_answers_fallback(attempt_data.items)
        else:
            # MongoDB 연결 없음 - fallback 사용
            grade_result = await _grade_answers_fallback(attempt_data.items)
        
        # QuizAttemptItem 리스트 생성
        attempt_items = []
        for i, result in enumerate(grade_result.results):
            attempt_items.append(QuizAttemptItem(
                question_id=result.question_id,
                user_answer=attempt_data.items[i].user_answer,
                correct_answer=result.correct_answer,
                is_correct=result.is_correct
            ))
        
        # 결과 객체 생성
        attempt_result = QuizAttemptOut(
            attempt_id=attempt_id,
            problemset_id=attempt_data.problemset_id,
            total=grade_result.total,
            correct=grade_result.correct,
            score=grade_result.score,
            items=attempt_items,
            started_at=attempt_data.started_at,
            finished_at=attempt_data.finished_at
        )
        
        # 저장 (MongoDB 또는 in-memory)
        if db is not None:
            try:
                await db["quiz_attempts"].insert_one(attempt_result.dict())
                logger.info(f"퀴즈 시도 저장 완료: {attempt_id}")
            except Exception as e:
                logger.warning(f"MongoDB 저장 실패, in-memory 저장: {e}")
                _in_memory_attempts.append(attempt_result.dict())
        else:
            _in_memory_attempts.append(attempt_result.dict())
            logger.info(f"퀴즈 시도 in-memory 저장 완료: {attempt_id}")
        
        return attempt_result
        
    except Exception as e:
        logger.error(f"퀴즈 시도 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=f"퀴즈 시도 생성 실패: {str(e)}")

@router.get("/attempts", response_model=QuizAttemptsResponse, summary="퀴즈 시도 목록 조회")
async def get_quiz_attempts(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지 크기"),
    db: Optional[AsyncIOMotorDatabase] = Depends(get_database_or_none),
):
    """
    퀴즈 시도 목록을 최신순으로 조회합니다.
    
    - **page**: 페이지 번호 (1부터 시작)
    - **size**: 페이지 크기 (1-100)
    """
    try:
        skip = (page - 1) * size
        
        if db is not None:
            try:
                # 전체 개수 조회
                total_count = await db["quiz_attempts"].count_documents({})
                
                # 페이지네이션된 결과 조회
                cursor = db["quiz_attempts"].find().sort("created_at", -1).skip(skip).limit(size)
                results = await cursor.to_list(length=size)
                
                if not results:
                    return QuizAttemptsResponse(
                        items=[],
                        total=total_count,
                        page=page,
                        size=size,
                        pages=0
                    )
                
                attempts = [QuizAttemptOut(**result) for result in results]
                total_pages = (total_count + size - 1) // size
                
                return QuizAttemptsResponse(
                    items=attempts,
                    total=total_count,
                    page=page,
                    size=size,
                    pages=total_pages
                )
                
            except Exception as e:
                logger.warning(f"MongoDB 조회 실패, in-memory 조회: {e}")
                # fallback to in-memory
                pass
        
        # In-memory fallback
        sorted_attempts = sorted(_in_memory_attempts, key=lambda x: x.get("created_at", datetime.utcnow()), reverse=True)
        total_count = len(sorted_attempts)
        paginated_attempts = sorted_attempts[skip:skip + size]
        
        attempts = [QuizAttemptOut(**attempt) for attempt in paginated_attempts]
        total_pages = (total_count + size - 1) // size
        
        return QuizAttemptsResponse(
            items=attempts,
            total=total_count,
            page=page,
            size=size,
            pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"퀴즈 시도 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"퀴즈 시도 목록 조회 실패: {str(e)}")

@router.get("/attempts/{attempt_id}", response_model=QuizAttemptOut, summary="퀴즈 시도 상세 조회")
async def get_quiz_attempt(
    attempt_id: str,
    db: Optional[AsyncIOMotorDatabase] = Depends(get_database_or_none),
):
    """
    특정 퀴즈 시도의 상세 정보를 조회합니다.
    
    - **attempt_id**: 시도 ID
    """
    try:
        if db is not None:
            try:
                result = await db["quiz_attempts"].find_one({"attempt_id": attempt_id})
                
                if not result:
                    raise HTTPException(status_code=404, detail="퀴즈 시도를 찾을 수 없습니다.")
                
                return QuizAttemptOut(**result)
                
            except Exception as e:
                logger.warning(f"MongoDB 조회 실패, in-memory 조회: {e}")
                # fallback to in-memory
                pass
        
        # In-memory fallback
        for attempt in _in_memory_attempts:
            if attempt.get("attempt_id") == attempt_id:
                return QuizAttemptOut(**attempt)
        
        raise HTTPException(status_code=404, detail="퀴즈 시도를 찾을 수 없습니다.")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"퀴즈 시도 상세 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"퀴즈 시도 상세 조회 실패: {str(e)}")

@router.get("/attempts/{attempt_id}/export.json", summary="퀴즈 시도 결과 JSON 내보내기")
async def export_quiz_attempt_json(
    attempt_id: str,
    db: Optional[AsyncIOMotorDatabase] = Depends(get_database_or_none),
):
    """
    특정 퀴즈 시도 결과를 JSON 형식으로 내보냅니다.
    
    - **attempt_id**: 시도 ID
    """
    try:
        # 퀴즈 시도 데이터 조회
        attempt_data = None
        
        if db is not None:
            try:
                result = await db["quiz_attempts"].find_one({"attempt_id": attempt_id})
                if result:
                    attempt_data = QuizAttemptOut(**result)
            except Exception as e:
                logger.warning(f"MongoDB 조회 실패, in-memory 조회: {e}")
        
        if attempt_data is None:
            # In-memory fallback
            for attempt in _in_memory_attempts:
                if attempt.get("attempt_id") == attempt_id:
                    attempt_data = QuizAttemptOut(**attempt)
                    break
        
        if not attempt_data:
            raise HTTPException(status_code=404, detail="퀴즈 시도를 찾을 수 없습니다.")
        
        # JSON 응답 반환
        return Response(
            content=json.dumps(attempt_data.dict(), ensure_ascii=False, indent=2),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=quiz_attempt_{attempt_id}.json"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"퀴즈 시도 JSON 내보내기 실패: {e}")
        raise HTTPException(status_code=500, detail=f"퀴즈 시도 JSON 내보내기 실패: {str(e)}")

@router.get("/attempts/{attempt_id}/export.csv", summary="퀴즈 시도 결과 CSV 내보내기")
async def export_quiz_attempt_csv(
    attempt_id: str,
    db: Optional[AsyncIOMotorDatabase] = Depends(get_database_or_none),
):
    """
    특정 퀴즈 시도 결과를 CSV 형식으로 내보냅니다.
    
    - **attempt_id**: 시도 ID
    """
    try:
        # 퀴즈 시도 데이터 조회
        attempt_data = None
        
        if db is not None:
            try:
                result = await db["quiz_attempts"].find_one({"attempt_id": attempt_id})
                if result:
                    attempt_data = QuizAttemptOut(**result)
            except Exception as e:
                logger.warning(f"MongoDB 조회 실패, in-memory 조회: {e}")
        
        if attempt_data is None:
            # In-memory fallback
            for attempt in _in_memory_attempts:
                if attempt.get("attempt_id") == attempt_id:
                    attempt_data = QuizAttemptOut(**attempt)
                    break
        
        if not attempt_data:
            raise HTTPException(status_code=404, detail="퀴즈 시도를 찾을 수 없습니다.")
        
        # CSV 생성
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 헤더 작성
        writer.writerow([
            "문제 ID", "사용자 답안", "정답", "정답 여부", 
            "시작 시간", "완료 시간", "총 문제 수", "정답 수", "점수"
        ])
        
        # 각 문제별 데이터 작성
        for item in attempt_data.items:
            writer.writerow([
                item.question_id,
                item.user_answer,
                item.correct_answer,
                "정답" if item.is_correct else "오답",
                attempt_data.started_at.strftime("%Y-%m-%d %H:%M:%S"),
                attempt_data.finished_at.strftime("%Y-%m-%d %H:%M:%S"),
                attempt_data.total,
                attempt_data.correct,
                f"{attempt_data.score}%"
            ])
        
        # CSV 응답 반환 (UTF-8 BOM 포함)
        csv_content = output.getvalue()
        csv_bytes = csv_content.encode('utf-8-sig')  # UTF-8 BOM 추가
        
        return Response(
            content=csv_bytes,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=quiz_attempt_{attempt_id}.csv",
                "Content-Type": "text/csv; charset=utf-8"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"퀴즈 시도 CSV 내보내기 실패: {e}")
        raise HTTPException(status_code=500, detail=f"퀴즈 시도 CSV 내보내기 실패: {str(e)}")

@router.post("/retry", response_model=RetryResponse, summary="틀린 문제 기반 맞춤형 문제 생성")
async def create_retry_problems(
    retry_request: RetryRequest,
    db: Optional[AsyncIOMotorDatabase] = Depends(get_database_or_none),
):
    """
    사용자가 틀린 문제들을 분석하여 맞춤형 재시도 문제를 생성합니다.
    
    - **attempt_id**: 시도 ID
    - **model**: 사용할 LLM 모델 (기본값: gpt-4o-mini)
    - **num_questions**: 생성할 문제 수 (기본값: 5, 최대: 10)
    """
    try:
        logger.info(f"[INFO] 재시도 문제 생성 시작: {retry_request.attempt_id}, {retry_request.num_questions}문제")
        
        # MongoDB에서 시도 기록 조회
        attempt_data = None
        
        if db is not None:
            try:
                result = await db["quiz_attempts"].find_one({"attempt_id": retry_request.attempt_id})
                if result:
                    attempt_data = QuizAttemptOut(**result)
            except Exception as e:
                logger.warning(f"MongoDB 조회 실패, in-memory 조회: {e}")
        
        if attempt_data is None:
            # In-memory fallback
            for attempt in _in_memory_attempts:
                if attempt.get("attempt_id") == retry_request.attempt_id:
                    attempt_data = QuizAttemptOut(**attempt)
                    break
        
        if not attempt_data:
            raise HTTPException(status_code=404, detail="퀴즈 시도를 찾을 수 없습니다.")
        
        # 틀린 문제들 추출
        wrong_questions = []
        for item in attempt_data.items:
            if not item.is_correct:
                # 문제 상세 정보를 위해 원본 문제 조회 시도
                question_detail = None
                if db is not None:
                    try:
                        # problems 컬렉션에서 해당 문제 찾기
                        problem_doc = await db["problems"].find_one(
                            {"items.question_id": item.question_id},
                            {"items.$": 1}
                        )
                        if problem_doc and problem_doc.get("items"):
                            question_detail = problem_doc["items"][0]
                    except Exception as e:
                        logger.warning(f"문제 상세 조회 실패: {e}")
                
                # 기본 정보로 틀린 문제 구성
                wrong_question = {
                    "question_id": item.question_id,
                    "question": question_detail.get("question", f"문제 {item.question_id}") if question_detail else f"문제 {item.question_id}",
                    "correct_answer": item.correct_answer,
                    "user_answer": item.user_answer,
                    "explanation": question_detail.get("explanation", "해설 없음") if question_detail else "해설 없음",
                    "topic": question_detail.get("topic", "macro") if question_detail else "macro",
                    "level": question_detail.get("level", "basic") if question_detail else "basic"
                }
                wrong_questions.append(wrong_question)
        
        if not wrong_questions:
            raise HTTPException(status_code=400, detail="틀린 문제가 없어 재시도 문제를 생성할 수 없습니다.")
        
        # LLM으로 재시도 문제 생성
        try:
            logger.info(f"[INFO] LLM 호출 시작: {len(wrong_questions)}개 틀린 문제 분석")
            payload = generate_retry_problems_payload(
                wrong_questions, 
                retry_request.num_questions, 
                retry_request.model
            )
            logger.info(f"[INFO] LLM 응답 받음: {len(payload.get('items', []))}개 문제 생성")
            
            # 생성된 문제들을 RetryProblemItem으로 변환
            retry_problems = []
            for item_data in payload.get("items", []):
                retry_problem = RetryProblemItem(**item_data)
                retry_problems.append(retry_problem)
            
            # 응답 생성
            retry_response = RetryResponse(
                attempt_id=retry_request.attempt_id,
                count=len(retry_problems),
                problems=retry_problems
            )
            
            # MongoDB에 저장 (연결된 경우에만)
            if db is not None:
                try:
                    await db["retry_problems"].insert_one(retry_response.dict())
                    logger.info(f"재시도 문제 저장 완료: {retry_request.attempt_id}")
                except Exception as e:
                    logger.warning(f"MongoDB 저장 실패: {e}")
            
            return retry_response
            
        except Exception as e:
            logger.error(f"LLM 문제 생성 실패: {e}")
            # LLM 실패 시 더미 문제 반환
            return await _create_dummy_retry_problems(retry_request.attempt_id, retry_request.num_questions)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"재시도 문제 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=f"재시도 문제 생성 실패: {str(e)}")

async def _create_dummy_retry_problems(attempt_id: str, num_questions: int) -> RetryResponse:
    """
    MongoDB 연결 실패 시 더미 재시도 문제를 생성합니다.
    """
    dummy_problems = []
    
    for i in range(min(num_questions, 3)):  # 최대 3개
        dummy_problems.append(RetryProblemItem(
            question=f"더미 재시도 문제 {i+1}: 경제학의 기본 개념에 대한 문제입니다.",
            options=["A) 선택지 1", "B) 선택지 2", "C) 선택지 3", "D) 선택지 4"],
            answer="A",
            explanation="이것은 더미 문제입니다. 실제 문제를 생성하려면 MongoDB 연결이 필요합니다.",
            topic="macro",
            level="basic"
        ))
    
    return RetryResponse(
        attempt_id=attempt_id,
        count=len(dummy_problems),
        problems=dummy_problems
    )
