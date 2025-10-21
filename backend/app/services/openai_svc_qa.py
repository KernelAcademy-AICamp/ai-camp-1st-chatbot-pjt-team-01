"""OpenAI API 서비스"""
import json
import os       
from typing import List, Dict, Any
from openai import AsyncOpenAI, OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings
from app.core.security import sanitize_input, is_safe_prompt
from app.models.common import ProblemItem, RecommendItem
from dotenv import load_dotenv

load_dotenv('env.txt')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


# ===== 시스템 프롬프트 =====
SYSTEM_PROMPT_BASE = """당신은 경제 전문가이자 교육자입니다.
- 정확하고 근거 있는 답변을 제공합니다.
- 불확실한 내용은 명확히 표시하고, 모르는 것은 솔직히 인정합니다.
- 마크다운 형식으로 응답하며, 필요시 출처를 표기합니다.
- 한국어로 명확하고 전문적인 톤을 유지합니다."""


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def generate_chat_response(
    question: str,
    context: str = None,
    system_prompt: str = SYSTEM_PROMPT_BASE,
    temperature: float = 0.7
) -> str:
    """
    일반 Q&A 응답 생성
    """
    # 입력 검증
    question = sanitize_input(question, max_length=2000)
    if not is_safe_prompt(question):
        raise ValueError("안전하지 않은 입력이 감지되었습니다.")

    messages = [
        {"role": "system", "content": system_prompt}
    ]

    print(f"[OpenAI Service] context 수신: {len(context) if context else 0}자")

    if context:
        context = sanitize_input(context, max_length=5000)
        print(f"[OpenAI Service] sanitize 후 context: {len(context)}자")
        print(f"[OpenAI Service] context 미리보기: {context[:300]}...")
        messages.append({"role": "user", "content": f"참고 자료:\n{context}"})
        print(f"[OpenAI Service] [OK] context를 messages에 추가함")
    else:
        print(f"[OpenAI Service] [WARN] context가 없음!")

    messages.append({"role": "user", "content": question})

    print(f"[OpenAI Service] 총 메시지 개수: {len(messages)}")
    print(f"[OpenAI Service] OpenAI API 호출 시작...")

    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=messages,
        max_tokens=settings.OPENAI_MAX_TOKENS,
        temperature=temperature
    )

    print(f"[OpenAI Service] OpenAI API 응답 받음")
    return response.choices[0].message.content


async def generate_summary(question: str, context: str = None) -> Dict[str, Any]:
    """
    요약 생성 (출처 포함)
    """
    summary_prompt = SYSTEM_PROMPT_BASE + """
    
요청된 주제에 대해 핵심만 간결하게 5~10 문장으로 요약해주세요.
- 가능하면 출처 표기 (예: [출처: 한국은행])
"""
    answer = await generate_chat_response(question, context, summary_prompt, temperature=1.0)
    
    # 간단한 출처 추출 (실제로는 더 정교한 로직 필요)
    citations = []
    if "[출처:" in answer or "(출처:" in answer:
        citations = ["한국은행", "통계청", "금융감독원"]  # mock
    
    return {
        "answer_md": answer,
        "citations": citations
    }

