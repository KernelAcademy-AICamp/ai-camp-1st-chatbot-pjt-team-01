import os
import re
import json
import logging
from typing import Any, Dict

from tenacity import retry, stop_after_attempt, wait_exponential
from openai import OpenAI

from app.services.prompts.problem_prompt import build_problem_prompt, build_retry_problem_prompt
from app.services.demo_service import generate_demo_problems, generate_demo_retry_problems
from app.core.config import settings

# 로거
logger = logging.getLogger("econ.llm")

# OpenAI 클라이언트 (main.py에서 load_dotenv()가 먼저 실행되어야 함)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")  # 더 빠른 모델로 변경
REQ_TIMEOUT = int(os.getenv("OPENAI_TIMEOUT_SEC", "120"))  # 2분으로 증가

def _extract_json(text: str) -> Dict[str, Any]:
    """
    모델이 코드블록/여분 텍스트를 섞어도 JSON만 뽑아내는 유틸.
    """
    s = (text or "").strip()

    # ```json ... ``` 우선 추출
    m = re.search(r"```json\s*(\{.*?\})\s*```", s, flags=re.S)
    if m:
        s = m.group(1)

    # 맨 처음 '{' ~ 마지막 '}' 스팬만 살림
    if not s.startswith("{"):
        first = s.find("{")
        last = s.rfind("}")
        if first != -1 and last != -1 and last > first:
            s = s[first:last + 1]

    return json.loads(s)

@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=4), reraise=True)
def _chat_complete(prompt: str) -> str:
    """
    OpenAI Chat Completions 호출 (지수 백오프 2회 재시도)
    """
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "경제학 문제 출제 전문가. JSON만 출력."},
            {"role": "user",   "content": prompt},
        ],
        temperature=0.5,  # 더 일관된 결과
        max_tokens=800,   # 토큰 수 줄임
        timeout=REQ_TIMEOUT,
    )
    return (resp.choices[0].message.content or "").strip()

def generate_econ_problems_payload(topic: str, level: str, count: int, style: str) -> Dict[str, Any]:
    """
    OpenAI에 문제 생성을 요청해 JSON payload(dict)를 반환.
    DEMO 모드일 때는 더미 데이터를 반환합니다.
    """
    # DEMO 모드 확인
    if settings.DEMO:
        logger.info(f"[DEMO] 더미 문제 생성: {topic}, {level}, {count}문제, {style}")
        return generate_demo_problems(topic, level, count, style)
    
    # 실제 OpenAI 호출
    logger.info(f"[REAL] OpenAI 문제 생성: {topic}, {level}, {count}문제, {style}")
    prompt = build_problem_prompt(topic, level, count, style)
    raw = _chat_complete(prompt)

    try:
        data = _extract_json(raw)
    except Exception as e:
        logger.error(f"[LLM JSON 파싱 실패] {e}\n=== RAW START ===\n{raw}\n=== RAW END ===")
        raise

    if "items" not in data or not isinstance(data["items"], list) or len(data["items"]) == 0:
        raise ValueError("AI 응답에 'items' 배열이 없거나 비어 있습니다.")

    return data

def generate_retry_problems_payload(wrong_questions: list, num_questions: int, model: str = "gpt-3.5-turbo") -> Dict[str, Any]:
    """
    틀린 문제들을 분석하여 재시도 문제를 생성하는 함수
    DEMO 모드일 때는 더미 데이터를 반환합니다.
    """
    # DEMO 모드 확인
    if settings.DEMO:
        logger.info(f"[DEMO] 더미 재시도 문제 생성: {len(wrong_questions)}개 틀린 문제 분석, {num_questions}문제")
        return generate_demo_retry_problems(wrong_questions, num_questions)
    
    # 실제 OpenAI 호출
    logger.info(f"[REAL] OpenAI 재시도 문제 생성: {len(wrong_questions)}개 틀린 문제 분석, {num_questions}문제")
    prompt = build_retry_problem_prompt(wrong_questions, num_questions)
    
    # 모델별 클라이언트 설정
    global MODEL
    if model != MODEL:
        # 다른 모델 사용 시 임시로 클라이언트 설정 변경
        original_model = MODEL
        MODEL = model
    
    try:
        raw = _chat_complete(prompt)
        
        try:
            data = _extract_json(raw)
        except Exception as e:
            logger.error(f"[LLM JSON 파싱 실패] {e}\n=== RAW START ===\n{raw}\n=== RAW END ===")
            raise
        
        if "items" not in data or not isinstance(data["items"], list) or len(data["items"]) == 0:
            raise ValueError("AI 응답에 'items' 배열이 없거나 비어 있습니다.")
        
        return data
        
    finally:
        # 원래 모델로 복원
        if model != original_model:
            MODEL = original_model
