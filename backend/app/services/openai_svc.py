"""OpenAI API 서비스"""
import json
from typing import List, Dict, Any
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings
from app.core.security import sanitize_input, is_safe_prompt
from app.models.common import ProblemItem, RecommendItem

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
    system_prompt: str = SYSTEM_PROMPT_BASE
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
    
    if context:
        context = sanitize_input(context, max_length=5000)
        messages.append({"role": "user", "content": f"참고 자료:\n{context}"})
    
    messages.append({"role": "user", "content": question})
    
    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=messages,
        max_tokens=settings.OPENAI_MAX_TOKENS,
        temperature=0.7
    )
    
    return response.choices[0].message.content


async def generate_summary(question: str, context: str = None) -> Dict[str, Any]:
    """
    요약 생성 (출처 포함)
    """
    summary_prompt = SYSTEM_PROMPT_BASE + """
    
요청된 주제에 대해 핵심만 간결하게 요약하세요.
- 주요 포인트를 불릿 리스트로 정리
- 숫자나 통계가 있다면 명시
- 가능하면 출처 표기 (예: [출처: 한국은행])
"""
    
    answer = await generate_chat_response(question, context, summary_prompt)
    
    # 간단한 출처 추출 (실제로는 더 정교한 로직 필요)
    citations = []
    if "[출처:" in answer or "(출처:" in answer:
        citations = ["한국은행", "통계청", "금융감독원"]  # mock
    
    return {
        "answer_md": answer,
        "citations": citations
    }


async def generate_problems(
    level: str,
    topic: str,
    count: int,
    style: str
) -> List[ProblemItem]:
    """
    경제 문제 생성
    """
    level_map = {
        "basic": "초급 (기본 개념)",
        "intermediate": "중급 (실전 응용)",
        "advanced": "고급 (심화 분석)"
    }
    
    topic_map = {
        "macro": "거시경제 (GDP, 인플레이션, 실업 등)",
        "finance": "금융 (금리, 환율, 주식, 채권 등)",
        "trade": "국제무역 (수출입, 환율, 관세 등)",
        "stats": "경제통계 (지표 해석, 분석 방법)"
    }
    
    style_desc = "4지선다형 객관식" if style == "mcq" else "서술형"
    
    prompt = f"""다음 조건에 맞는 경제 문제를 {count}개 생성하세요:

- 난이도: {level_map.get(level, level)}
- 주제: {topic_map.get(topic, topic)}
- 형식: {style_desc}

각 문제는 다음 JSON 형식으로 작성:
{{
  "question": "문제 내용",
  "options": ["1번", "2번", "3번", "4번"],  // 객관식인 경우만
  "answer": "정답",
  "explain": "해설 (왜 그런지 설명)"
}}

전체를 JSON 배열로 반환하세요. 반드시 유효한 JSON 형식이어야 합니다."""
    
    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_BASE},
            {"role": "user", "content": prompt}
        ],
        max_tokens=3000,
        temperature=0.8,
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content
    
    try:
        # JSON 파싱
        data = json.loads(content)
        
        # 배열 추출 (키가 다를 수 있음)
        if isinstance(data, list):
            items_data = data
        elif "problems" in data:
            items_data = data["problems"]
        elif "items" in data:
            items_data = data["items"]
        else:
            # 첫 번째 배열 찾기
            items_data = next((v for v in data.values() if isinstance(v, list)), [])
        
        problems = []
        for item in items_data[:count]:
            problems.append(ProblemItem(
                question=item.get("question", ""),
                options=item.get("options") if style == "mcq" else None,
                answer=item.get("answer", ""),
                explain=item.get("explain", "")
            ))
        
        return problems
    
    except json.JSONDecodeError:
        # JSON 파싱 실패 시 더미 데이터 반환
        return [
            ProblemItem(
                question=f"{topic} 관련 문제 {i+1}",
                options=["1번", "2번", "3번", "4번"] if style == "mcq" else None,
                answer="정답 예시",
                explain="해설이 여기에 표시됩니다."
            )
            for i in range(count)
        ]


async def generate_recommendations(
    topic: str,
    level: str,
    purpose: str
) -> List[RecommendItem]:
    """
    경제 자료 추천
    """
    purpose_map = {
        "report": "리포트 작성용 (통계, 보고서)",
        "study": "학습용 (교재, 강의)",
        "data": "데이터 분석용 (CSV, 데이터셋)",
        "api": "API 연동용 (오픈 API)"
    }
    
    prompt = f"""다음 조건에 맞는 경제 자료/리소스를 6개 추천하세요:

- 주제: {topic}
- 수준: {level}
- 목적: {purpose_map.get(purpose, purpose)}

각 추천은 다음 JSON 형식:
{{
  "title": "자료명",
  "summary": "2-3줄 설명",
  "url": "링크 (실제 존재하는 공식 사이트)",
  "tags": ["무료", "공식", "데이터", "API" 등]
}}

전체를 JSON 배열로 반환. 반드시 유효한 JSON."""
    
    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_BASE},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000,
        temperature=0.7,
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content
    
    try:
        data = json.loads(content)
        
        # 배열 추출
        if isinstance(data, list):
            items_data = data
        elif "recommendations" in data:
            items_data = data["recommendations"]
        elif "items" in data:
            items_data = data["items"]
        else:
            items_data = next((v for v in data.values() if isinstance(v, list)), [])
        
        recommendations = []
        for item in items_data[:6]:
            recommendations.append(RecommendItem(
                title=item.get("title", ""),
                summary=item.get("summary", ""),
                url=item.get("url", "https://example.com"),
                tags=item.get("tags", [])
            ))
        
        return recommendations
    
    except json.JSONDecodeError:
        # 기본 추천 데이터
        return [
            RecommendItem(
                title="한국은행 경제통계시스템",
                summary="국내 주요 경제지표와 통계 데이터를 제공하는 공식 시스템",
                url="https://ecos.bok.or.kr",
                tags=["무료", "공식", "데이터", "API"]
            ),
            RecommendItem(
                title="통계청 KOSIS",
                summary="국가통계포털, 국내 모든 공식 통계 제공",
                url="https://kosis.kr",
                tags=["무료", "공식", "데이터"]
            )
        ]

