def build_problem_prompt(topic: str, level: str, count: int, style: str):
    """
    난이도별 구체적인 지침이 포함된 경제 문제 생성 프롬프트
    """
    # 난이도별 구체적인 지침
    level_guidelines = {
        "basic": "초급: 기본 개념과 용어 이해 수준. 경제학 입문자도 이해할 수 있는 쉬운 문제",
        "intermediate": "중급: 기본 개념을 바탕으로 한 분석과 응용. 경제학을 어느 정도 학습한 수준",
        "advanced": "고급: 복합적 사고와 심화 분석이 필요한 전문가 수준 문제"
    }
    
    # 주제별 구체적인 설명과 키워드
    topic_descriptions = {
        "macro": {
            "name": "거시경제학",
            "description": "국가 전체의 경제 현상을 다루는 학문",
            "keywords": "GDP, GNP, 인플레이션, 디플레이션, 실업률, 경제성장률, 통화정책, 재정정책, 중앙은행, 기준금리, 물가안정, 완전고용, 국민소득, 소비, 투자, 정부지출, 수출입",
            "examples": "GDP 계산, 인플레이션 원인, 실업률 분석, 통화정책 효과, 재정정책 영향"
        },
        "finance": {
            "name": "금융학",
            "description": "자금의 조달과 운용, 금융시장과 금융기관을 다루는 학문",
            "keywords": "금융시장, 주식시장, 채권시장, 외환시장, 금융기관, 은행, 보험, 증권, 펀드, 파생상품, 옵션, 선물, 위험관리, 자산관리, 투자, 수익률, 리스크",
            "examples": "주식 가격 결정, 채권 수익률, 외환시장 분석, 금융상품 설계, 위험관리 전략"
        },
        "trade": {
            "name": "국제무역",
            "description": "국가 간 상품과 서비스의 교역을 다루는 학문",
            "keywords": "수출, 수입, 무역수지, 환율, 환율정책, 관세, 비관세장벽, FTA, WTO, 국제수지, 경상수지, 자본수지, 외환보유고, 무역정책, 보호무역, 자유무역",
            "examples": "환율 변동 영향, 무역수지 분석, FTA 효과, 관세 정책, 국제수지 구조"
        },
        "stats": {
            "name": "경제통계",
            "description": "경제 현상을 수치로 측정하고 분석하는 학문",
            "keywords": "경제지표, 통계분석, 회귀분석, 상관관계, 시계열분석, 확률분포, 가설검정, 신뢰구간, 표본조사, 인덱스, 계절조정, 추세분석, 예측모델",
            "examples": "경제지표 해석, 통계적 유의성 검정, 시계열 예측, 상관관계 분석, 회귀모델 구축"
        }
    }
    
    level_guide = level_guidelines.get(level, f"{level} 난이도")
    topic_info = topic_descriptions.get(topic, {"name": topic, "description": "", "keywords": "", "examples": ""})
    
    if style == "free":
        # 서술형 문제
        return f"""
{topic_info['name']} ({topic_info['description']}) 주제의 {level_guide} {count}개 서술형 문제를 생성하세요.

주제별 핵심 키워드: {topic_info['keywords']}
주제별 예시 문제: {topic_info['examples']}

난이도별 요구사항:
- 초급: 기본 개념 설명, 용어 정의, 단순한 원리 설명
- 중급: 개념 간 연관성 분석, 실제 사례 적용, 계산 문제
- 고급: 복합적 분석, 정책 효과 평가, 논리적 추론

중요: 반드시 {topic_info['name']} 영역의 내용으로만 문제를 출제하고, 위의 키워드들을 활용하세요.
서술형 문제는 객관식 보기가 없고, 정답은 간단한 키워드나 문장으로 제공하세요.

JSON 형식:
{{
  "items": [
    {{
      "question": "문제 내용 (서술형)",
      "options": null,
      "answer": "정답 키워드 또는 문장",
      "explanation": "상세한 해설",
      "topic": "{topic}",
      "level": "{level}"
    }}
  ]
}}
"""
    else:
        # 객관식 문제
        return f"""
{topic_info['name']} ({topic_info['description']}) 주제의 {level_guide} {count}개 객관식 문제를 생성하세요.

주제별 핵심 키워드: {topic_info['keywords']}
주제별 예시 문제: {topic_info['examples']}

난이도별 요구사항:
- 초급: 기본 개념과 용어, 단순한 사실 확인
- 중급: 개념 이해와 기본적인 계산, 간단한 분석
- 고급: 복합적 사고, 정책 분석, 고급 계산과 추론

중요: 반드시 {topic_info['name']} 영역의 내용으로만 문제를 출제하고, 위의 키워드들을 활용하세요.
각 문제는 4개의 보기를 가지며, 정답은 A, B, C, D 중 하나입니다.

JSON 형식:
{{
  "items": [
    {{
      "question": "문제",
      "options": ["A) 보기1", "B) 보기2", "C) 보기3", "D) 보기4"],
      "answer": "A",
      "explanation": "해설",
      "topic": "{topic}",
      "level": "{level}"
    }}
  ]
}}
"""

def build_retry_problem_prompt(wrong_questions: list, num_questions: int):
    """
    간단한 재시도 문제 생성 프롬프트
    """
    return f"""
틀린 문제들을 바탕으로 {num_questions}개 문제를 생성하세요.

JSON 형식:
{{
  "items": [
    {{
      "question": "문제",
      "options": ["A) 보기1", "B) 보기2", "C) 보기3", "D) 보기4"],
      "answer": "A",
      "explanation": "해설",
      "topic": "macro",
      "level": "basic"
    }}
  ]
}}
"""