"""Q&A 라우터"""
from fastapi import APIRouter, HTTPException
from app.models.common import QARequest, QAResponse
from app.services.openai_svc import generate_summary, generate_chat_response
from datetime import datetime

router = APIRouter(tags=["qa"])


@router.post("/qa/summary", response_model=QAResponse)
async def create_summary(request: QARequest):
    """
    경제 요약 생성
    """
    try:
        result = await generate_summary(request.question, request.context)
        return QAResponse(
            answer_md=result["answer_md"],
            citations=result["citations"],
            created_at=datetime.utcnow()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"요약 생성 실패: {str(e)}")


@router.post("/qa/chat", response_model=QAResponse)
async def chat(request: QARequest):
    """
    Q&A 채팅
    """
    try:
        answer = await generate_chat_response(request.question, request.context)
        return QAResponse(
            answer_md=answer,
            citations=[],
            created_at=datetime.utcnow()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"응답 생성 실패: {str(e)}")

