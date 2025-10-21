from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.problems import ProblemRequest, ProblemResponse, ProblemItem, GradeRequest, GradeResponse, GradeResult, AnswerItem
from app.db.mongo import get_database, mongo
from app.services.llm_service import generate_econ_problems_payload

router = APIRouter(tags=["problems"])

def get_database_or_none() -> Optional[AsyncIOMotorDatabase]:
    """데이터베이스 인스턴스 반환 (연결 실패 시 None 반환)"""
    try:
        return get_database()
    except RuntimeError:
        return None

# -------------------------------
# 1) 문제 생성 (안정화 버전)
# -------------------------------
@router.post("/problems", response_model=ProblemResponse, summary="경제 문제 생성")
async def create_problems(
    req: ProblemRequest,
    db: Optional[AsyncIOMotorDatabase] = Depends(get_database_or_none),
):
    """
    OpenAI를 호출해 문제를 생성하고, 품질 규칙을 검증한 뒤 MongoDB에 저장합니다.
    MongoDB 연결이 실패한 경우에도 문제를 생성하여 반환합니다.
    """
    try:
        print(f"[INFO] 문제 생성 시작: {req.topic}, {req.level}, {req.count}문제, {req.style}")
        payload = generate_econ_problems_payload(req.topic, req.level, req.count, req.style)
        print(f"[INFO] OpenAI 응답 받음: {len(payload.get('items', []))}개 항목")

        # 항목 수 일치 보정
        items_raw = payload.get("items", [])[: req.count]

        # 스키마 검증 + mcq 규칙 준수 확인
        items: List[ProblemItem] = []
        for i, raw in enumerate(items_raw):
            item = ProblemItem(**raw)
            if req.style == "mcq":
                if item.options is None or len(item.options) != 4:
                    raise HTTPException(status_code=422, detail=f"{i+1}번 문항: 객관식은 보기 4개가 필요합니다.")
            items.append(item)

        doc = ProblemResponse(items=items, topic=req.topic, level=req.level)
        
        # MongoDB에 저장 시도 (연결된 경우에만)
        if db is not None:
            try:
                await db["problems"].insert_one(doc.dict())
            except Exception as db_error:
                print(f"[WARNING] MongoDB 저장 실패: {db_error}")
                print("[INFO] 문제는 생성되었지만 저장되지 않았습니다.")
        else:
            print("[INFO] MongoDB 연결 없음 - 문제만 생성하여 반환")
        
        return doc

    except HTTPException:
        raise
    except Exception as e:
        msg = str(e)
        if "JSON" in msg or "items" in msg:
            raise HTTPException(status_code=502, detail="AI 응답을 해석하지 못했습니다(JSON 형식 오류). 다시 시도해 주세요.")
        elif "인증" in msg or "Authentication" in msg:
            raise HTTPException(status_code=401, detail="OpenAI 인증 오류(OPENAI_API_KEY 확인).")
        elif "Rate" in msg or "rate" in msg:
            raise HTTPException(status_code=429, detail="요청이 많습니다. 잠시 후 다시 시도해 주세요.")
        else:
            raise HTTPException(status_code=500, detail=f"문제 생성 실패: {msg}")

# -------------------------------
# 2) 문제 목록 조회 (필터/최신순)
# -------------------------------
@router.get("/problems", response_model=List[ProblemResponse], summary="저장된 문제 세트 조회")
async def list_problems(
    db: AsyncIOMotorDatabase = Depends(get_database),
    topic: Optional[str] = Query(None, description="macro | finance | trade | stats"),
    level: Optional[str] = Query(None, description="basic | intermediate | advanced"),
    limit: int = Query(10, ge=1, le=50),
):
    query = {}
    if topic:
        query["topic"] = topic
    if level:
        query["level"] = level

    cursor = db["problems"].find(query).sort("created_at", -1).limit(limit)
    results = await cursor.to_list(length=limit)
    if not results:
        raise HTTPException(status_code=404, detail="저장된 문제가 없습니다.")
    return [ProblemResponse(**r) for r in results]

# -------------------------------
# 3) 답안 채점
# -------------------------------
@router.post("/problems/grade", response_model=GradeResponse, summary="답안 채점")
async def grade_answers(
    req: GradeRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    사용자가 제출한 답안을 채점합니다.
    MongoDB에서 정답을 조회하여 비교하고, 점수를 계산합니다.
    MongoDB가 연결되지 않은 경우 더미 데이터로 채점합니다.
    """
    try:
        # MongoDB 연결 확인
        if db is None:
            raise RuntimeError("MongoDB not connected")
        
        # 문제 ID 목록 추출
        question_ids = [answer.question_id for answer in req.answers]
        
        # MongoDB에서 문제들 조회
        problems_cursor = db["problems"].find(
            {"items.question_id": {"$in": question_ids}},
            {"items": 1}
        )
        problems_docs = await problems_cursor.to_list(length=None)
        
        # 문제 데이터를 딕셔너리로 변환 (question_id -> answer)
        correct_answers = {}
        for doc in problems_docs:
            for item in doc.get("items", []):
                if "question_id" in item:
                    correct_answers[item["question_id"]] = item["answer"]
        
        # 채점 결과 생성
        results = []
        correct_count = 0
        
        for answer in req.answers:
            correct_answer = correct_answers.get(answer.question_id, "정답 없음")
            is_correct = answer.user_answer.strip().upper() == correct_answer.strip().upper()
            
            if is_correct:
                correct_count += 1
            
            results.append(GradeResult(
                question_id=answer.question_id,
                is_correct=is_correct,
                correct_answer=correct_answer
            ))
        
        total = len(req.answers)
        score = int((correct_count / total) * 100) if total > 0 else 0
        
        return GradeResponse(
            total=total,
            correct=correct_count,
            score=score,
            results=results
        )
        
    except RuntimeError as e:
        # MongoDB 연결 실패 시 더미 데이터로 채점
        if "MongoDB not connected" in str(e):
            return await _grade_with_dummy_data(req)
        raise HTTPException(status_code=500, detail=f"채점 실패: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"채점 실패: {str(e)}")


async def _grade_with_dummy_data(req: GradeRequest) -> GradeResponse:
    """
    MongoDB 연결이 실패한 경우 더미 데이터로 채점합니다.
    """
    # 더미 정답 데이터 (실제로는 문제 ID에 따라 다른 정답을 가져와야 함)
    dummy_answers = {
        "1": "A",
        "2": "D", 
        "3": "B",
        "4": "C",
        "5": "A",
        "6": "B",
        "7": "C",
        "8": "D",
        "9": "A",
        "10": "B"
    }
    
    results = []
    correct_count = 0
    
    for answer in req.answers:
        correct_answer = dummy_answers.get(answer.question_id, "A")  # 기본값 A
        is_correct = answer.user_answer.strip().upper() == correct_answer.strip().upper()
        
        if is_correct:
            correct_count += 1
        
        results.append(GradeResult(
            question_id=answer.question_id,
            is_correct=is_correct,
            correct_answer=correct_answer
        ))
    
    total = len(req.answers)
    score = int((correct_count / total) * 100) if total > 0 else 0
    
    return GradeResponse(
        total=total,
        correct=correct_count,
        score=score,
        results=results
    )
