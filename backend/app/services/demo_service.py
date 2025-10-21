import json
import os
from typing import Dict, Any, List
from pathlib import Path

def load_sample_problems() -> Dict[str, Any]:
    """샘플 문제 데이터를 로드합니다."""
    fixtures_path = Path(__file__).parent.parent / "fixtures" / "problems.sample.json"
    
    try:
        with open(fixtures_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # 샘플 파일이 없으면 기본 더미 데이터 반환
        return {
            "items": [
                # 초급 문제들
                {
                    "question": "거시경제학의 주요 목표는 무엇인가요?",
                    "options": ["A) 경제성장", "B) 완전고용", "C) 물가안정", "D) 모두 해당"],
                    "answer": "D",
                    "explanation": "거시경제학의 주요 목표는 경제성장, 완전고용, 물가안정, 국제수지 균형입니다.",
                    "topic": "macro",
                    "level": "basic"
                },
                {
                    "question": "GDP를 계산하는 방법은?",
                    "options": ["A) 생산법", "B) 소득법", "C) 지출법", "D) 모두 해당"],
                    "answer": "D",
                    "explanation": "GDP는 생산법, 소득법, 지출법 세 가지 방법으로 계산할 수 있습니다.",
                    "topic": "macro",
                    "level": "basic"
                },
                {
                    "question": "금융시장의 기능에 대해 설명하세요.",
                    "options": None,
                    "answer": "금융시장은 자금의 중개, 가격 발견, 위험 분산, 유동성 제공 등의 기능을 수행합니다.",
                    "explanation": "금융시장은 자금이 필요한 자와 여유 자금을 가진 자를 연결하여 자원을 효율적으로 배분하는 역할을 합니다.",
                    "topic": "finance",
                    "level": "basic"
                },
                {
                    "question": "인플레이션이란 무엇인가요?",
                    "options": ["A) 물가 상승", "B) 물가 하락", "C) 실업률 증가", "D) 경제성장"],
                    "answer": "A",
                    "explanation": "인플레이션은 일반적인 물가 수준이 지속적으로 상승하는 현상입니다.",
                    "topic": "macro",
                    "level": "basic"
                },
                
                # 중급 문제들
                {
                    "question": "중앙은행의 역할은?",
                    "options": ["A) 통화정책", "B) 금융안정", "C) 지급결제", "D) 모두 해당"],
                    "answer": "D",
                    "explanation": "중앙은행은 통화정책, 금융안정, 지급결제 시스템 관리 등의 역할을 담당합니다.",
                    "topic": "finance",
                    "level": "intermediate"
                },
                {
                    "question": "인플레이션이 경제에 미치는 영향을 서술하세요.",
                    "options": None,
                    "answer": "인플레이션은 구매력 감소, 소비자 신뢰 하락, 투자 감소, 소득 재분배 등의 영향을 미칩니다.",
                    "explanation": "인플레이션은 화폐의 가치를 하락시켜 구매력을 감소시키고, 경제 주체들의 기대를 불안정하게 만들어 투자를 위축시킵니다.",
                    "topic": "macro",
                    "level": "intermediate"
                },
                {
                    "question": "통화정책의 도구 중 정책금리는?",
                    "options": ["A) 지급준비율", "B) 공개시장조작", "C) 기준금리", "D) 환율정책"],
                    "answer": "C",
                    "explanation": "정책금리는 중앙은행이 금융기관에 자금을 공급할 때 적용하는 기준금리입니다.",
                    "topic": "finance",
                    "level": "intermediate"
                },
                {
                    "question": "환율이 수출입에 미치는 영향을 분석하세요.",
                    "options": None,
                    "answer": "원화 약세는 수출 증가와 수입 감소를, 원화 강세는 수출 감소와 수입 증가를 가져옵니다.",
                    "explanation": "환율 변동은 상대적 가격 경쟁력을 변화시켜 무역수지에 직접적인 영향을 미칩니다.",
                    "topic": "trade",
                    "level": "intermediate"
                },
                
                # 고급 문제들
                {
                    "question": "무역수지가 경제에 미치는 영향을 분석하세요.",
                    "options": None,
                    "answer": "무역수지는 국내 생산, 고용, 환율, 외환보유고 등에 영향을 미치며, 경제 성장과 안정성에 중요한 역할을 합니다.",
                    "explanation": "무역수지는 한 나라의 대외경제 상황을 나타내는 중요한 지표로, 경제정책 수립에 중요한 근거가 됩니다.",
                    "topic": "trade",
                    "level": "advanced"
                },
                {
                    "question": "IS-LM 모델에서 재정정책의 효과는?",
                    "options": ["A) IS곡선 우측이동", "B) LM곡선 우측이동", "C) 두 곡선 모두 이동", "D) 효과 없음"],
                    "answer": "A",
                    "explanation": "재정정책(정부지출 증가 등)은 IS곡선을 우측으로 이동시켜 소득과 이자율을 상승시킵니다.",
                    "topic": "macro",
                    "level": "advanced"
                },
                {
                    "question": "금융시장의 효율성 가설에 대해 설명하세요.",
                    "options": None,
                    "answer": "시장 효율성 가설은 금융시장의 가격이 모든 공개정보를 반영하여 형성되므로 예측 불가능하다는 이론입니다.",
                    "explanation": "이 가설에 따르면 과거 정보나 공개된 정보로는 미래 가격을 예측할 수 없으며, 시장은 정보적으로 효율적입니다.",
                    "topic": "finance",
                    "level": "advanced"
                },
                {
                    "question": "베이지안 통계를 이용한 경제예측의 장단점은?",
                    "options": ["A) 정확도 높음", "B) 불확실성 고려", "C) 계산 복잡", "D) 모두 해당"],
                    "answer": "D",
                    "explanation": "베이지안 통계는 사전 정보를 활용하여 불확실성을 고려하지만, 계산이 복잡하고 정확도가 높습니다.",
                    "topic": "stats",
                    "level": "advanced"
                },
                
                # 추가 통계 문제들
                {
                    "question": "상관계수와 회귀분석의 차이점은?",
                    "options": ["A) 상관계수는 관계의 강도, 회귀분석은 인과관계", "B) 상관계수는 인과관계, 회귀분석은 관계의 강도", "C) 동일한 개념", "D) 모두 틀림"],
                    "answer": "A",
                    "explanation": "상관계수는 두 변수 간 선형관계의 강도를 측정하고, 회귀분석은 한 변수가 다른 변수에 미치는 영향을 분석합니다.",
                    "topic": "stats",
                    "level": "intermediate"
                },
                {
                    "question": "경제지표의 계절조정이 필요한 이유는?",
                    "options": None,
                    "answer": "계절적 요인을 제거하여 경제의 근본적인 추세를 파악하기 위해서입니다.",
                    "explanation": "계절조정을 통해 계절적 변동을 제거하면 경제의 실제 성장 추세를 더 정확하게 분석할 수 있습니다.",
                    "topic": "stats",
                    "level": "basic"
                },
                
                # 추가 무역 문제들
                {
                    "question": "FTA의 주요 효과는?",
                    "options": ["A) 관세 철폐", "B) 무역 증대", "C) 경제 통합", "D) 모두 해당"],
                    "answer": "D",
                    "explanation": "FTA는 관세를 철폐하고 무역을 증대시키며, 경제 통합을 촉진하는 효과가 있습니다.",
                    "topic": "trade",
                    "level": "basic"
                },
                {
                    "question": "J커브 효과에 대해 설명하세요.",
                    "options": None,
                    "answer": "환율 하락 초기에는 무역수지가 악화되다가 시간이 지나면서 개선되는 현상입니다.",
                    "explanation": "환율 변동의 효과가 완전히 나타나기까지는 시간이 걸리기 때문에 단기적으로는 역효과가 나타날 수 있습니다.",
                    "topic": "trade",
                    "level": "intermediate"
                },
                
                # 추가 금융 문제들
                {
                    "question": "금융시장의 효율성 가설의 세 가지 형태는?",
                    "options": ["A) 약형, 준강형, 강형", "B) 단기형, 중기형, 장기형", "C) 개별형, 집단형, 전체형", "D) 모두 틀림"],
                    "answer": "A",
                    "explanation": "약형 효율성(과거 정보), 준강형 효율성(공개 정보), 강형 효율성(모든 정보)으로 구분됩니다.",
                    "topic": "finance",
                    "level": "advanced"
                },
                {
                    "question": "채권의 듀레이션이란?",
                    "options": ["A) 채권의 만기", "B) 이자 지급 주기", "C) 가격 변동 민감도", "D) 신용 등급"],
                    "answer": "C",
                    "explanation": "듀레이션은 금리 변동에 대한 채권 가격의 민감도를 나타내는 지표입니다.",
                    "topic": "finance",
                    "level": "intermediate"
                },
                {
                    "question": "주식과 채권의 차이점은?",
                    "options": ["A) 주식은 소유권, 채권은 채무", "B) 주식은 변동수익, 채권은 고정수익", "C) 주식은 위험높음, 채권은 안전", "D) 모두 해당"],
                    "answer": "D",
                    "explanation": "주식은 기업의 소유권을 나타내며 변동수익과 높은 위험을, 채권은 채무를 나타내며 고정수익과 상대적으로 안전합니다.",
                    "topic": "finance",
                    "level": "basic"
                },
                {
                    "question": "포트폴리오 이론에 대해 설명하세요.",
                    "options": None,
                    "answer": "여러 자산을 조합하여 위험을 분산시키고 수익을 극대화하는 투자 전략입니다.",
                    "explanation": "포트폴리오 이론은 분산투자를 통해 위험을 줄이면서도 수익을 극대화할 수 있다는 이론입니다.",
                    "topic": "finance",
                    "level": "intermediate"
                },
                {
                    "question": "옵션과 선물의 차이점은?",
                    "options": ["A) 옵션은 권리, 선물은 의무", "B) 옵션은 선택권, 선물은 반드시 이행", "C) 옵션은 프리미엄, 선물은 마진", "D) 모두 해당"],
                    "answer": "D",
                    "explanation": "옵션은 권리(선택권)이고 프리미엄을 지불하며, 선물은 의무(반드시 이행)이고 마진을 지불합니다.",
                    "topic": "finance",
                    "level": "advanced"
                },
                
                # 추가 통계 문제들
                {
                    "question": "표준편차의 의미는?",
                    "options": ["A) 평균에서 얼마나 떨어져 있는지", "B) 데이터의 분산 정도", "C) 최대값과 최소값의 차이", "D) 모두 해당"],
                    "answer": "B",
                    "explanation": "표준편차는 데이터가 평균에서 얼마나 흩어져 있는지를 나타내는 분산의 정도를 측정합니다.",
                    "topic": "stats",
                    "level": "basic"
                },
                {
                    "question": "회귀분석에서 R²의 의미는?",
                    "options": ["A) 결정계수", "B) 설명력", "C) 모델의 적합도", "D) 모두 해당"],
                    "answer": "D",
                    "explanation": "R²는 결정계수로 모델이 데이터를 얼마나 잘 설명하는지(설명력)를 나타내는 적합도 지표입니다.",
                    "topic": "stats",
                    "level": "intermediate"
                },
                {
                    "question": "시계열 분석에서 트렌드와 계절성을 구분하는 이유는?",
                    "options": None,
                    "answer": "경제의 근본적인 변화(트렌드)와 일시적인 계절적 변동을 구분하여 정확한 예측을 하기 위해서입니다.",
                    "explanation": "트렌드는 장기적 변화를, 계절성은 반복적인 단기 변동을 나타내므로 이를 구분해야 정확한 분석이 가능합니다.",
                    "topic": "stats",
                    "level": "advanced"
                },
                {
                    "question": "가설검정에서 1종 오류는?",
                    "options": ["A) 귀무가설이 참인데 기각", "B) 귀무가설이 거짓인데 채택", "C) 대립가설이 참인데 기각", "D) 모두 틀림"],
                    "answer": "A",
                    "explanation": "1종 오류는 귀무가설이 실제로 참인데도 불구하고 이를 기각하는 오류입니다.",
                    "topic": "stats",
                    "level": "intermediate"
                }
            ]
        }

def generate_demo_problems(topic: str, level: str, count: int, style: str) -> Dict[str, Any]:
    """DEMO 모드에서 사용할 더미 문제를 생성합니다."""
    sample_data = load_sample_problems()
    
    # 요청된 개수만큼 샘플 데이터에서 선택
    available_items = sample_data.get("items", [])
    
    # 디버깅을 위한 로그
    print(f"[DEMO] 요청: {topic}, {level}, {count}문제, {style}")
    print(f"[DEMO] 전체 문제 수: {len(available_items)}")
    
    # 주제별 문제 수 확인
    topic_counts = {}
    for item in available_items:
        item_topic = item.get("topic", "unknown")
        topic_counts[item_topic] = topic_counts.get(item_topic, 0) + 1
    print(f"[DEMO] 주제별 문제 수: {topic_counts}")
    
    # 난이도별 문제 매핑
    level_mapping = {
        "basic": ["basic"],
        "intermediate": ["intermediate"], 
        "advanced": ["advanced"]
    }
    
    # 주제별 문제 매핑
    topic_mapping = {
        "macro": ["macro"],
        "finance": ["finance"],
        "trade": ["trade"],
        "stats": ["stats"]
    }
    
    # 서술형 문제인 경우 서술형 문제만 필터링
    if style == "free":
        free_items = [item for item in available_items if item.get("options") is None]
        # 주제별로 필터링
        topic_items = [item for item in free_items if item.get("topic") in topic_mapping.get(topic, ["macro"])]
        # 난이도별로 필터링
        level_items = [item for item in topic_items if item.get("level") in level_mapping.get(level, ["basic"])]
        
        print(f"[DEMO] 서술형 문제: 주제+난이도 매칭 {len(level_items)}개")
        
        # 필터링된 문제가 부족하면 주제만 맞춰서 추가
        if len(level_items) < count:
            remaining_needed = count - len(level_items)
            topic_only_items = [item for item in free_items if item.get("topic") in topic_mapping.get(topic, ["macro"])]
            level_items.extend(topic_only_items[:remaining_needed])
            print(f"[DEMO] 서술형 문제: 주제만 매칭 추가 {len(topic_only_items[:remaining_needed])}개")
        
        # 여전히 부족하면 난이도만 맞춰서 추가
        if len(level_items) < count:
            remaining_needed = count - len(level_items)
            level_only_items = [item for item in free_items if item.get("level") in level_mapping.get(level, ["basic"])]
            level_items.extend(level_only_items[:remaining_needed])
            print(f"[DEMO] 서술형 문제: 난이도만 매칭 추가 {len(level_only_items[:remaining_needed])}개")
        
        selected_items = level_items[:count] if len(level_items) >= count else level_items
        print(f"[DEMO] 서술형 최종 선택: {len(selected_items)}개")
    else:
        # 객관식 문제인 경우 객관식 문제만 필터링
        mcq_items = [item for item in available_items if item.get("options") is not None]
        # 주제별로 필터링
        topic_items = [item for item in mcq_items if item.get("topic") in topic_mapping.get(topic, ["macro"])]
        # 난이도별로 필터링
        level_items = [item for item in topic_items if item.get("level") in level_mapping.get(level, ["basic"])]
        
        print(f"[DEMO] 객관식 문제: 주제+난이도 매칭 {len(level_items)}개")
        
        # 필터링된 문제가 부족하면 주제만 맞춰서 추가
        if len(level_items) < count:
            remaining_needed = count - len(level_items)
            topic_only_items = [item for item in mcq_items if item.get("topic") in topic_mapping.get(topic, ["macro"])]
            level_items.extend(topic_only_items[:remaining_needed])
            print(f"[DEMO] 객관식 문제: 주제만 매칭 추가 {len(topic_only_items[:remaining_needed])}개")
        
        # 여전히 부족하면 난이도만 맞춰서 추가
        if len(level_items) < count:
            remaining_needed = count - len(level_items)
            level_only_items = [item for item in mcq_items if item.get("level") in level_mapping.get(level, ["basic"])]
            level_items.extend(level_only_items[:remaining_needed])
            print(f"[DEMO] 객관식 문제: 난이도만 매칭 추가 {len(level_only_items[:remaining_needed])}개")
        
        selected_items = level_items[:count] if len(level_items) >= count else level_items
        
        # 여전히 부족하면 모든 객관식 문제에서 선택
        if len(selected_items) < count:
            remaining_needed = count - len(selected_items)
            all_mcq_items = [item for item in available_items if item.get("options") is not None]
            selected_items.extend(all_mcq_items[:remaining_needed])
            print(f"[DEMO] 객관식 문제: 전체에서 추가 선택 {len(all_mcq_items[:remaining_needed])}개")
        
        selected_items = selected_items[:count] if len(selected_items) >= count else selected_items
        print(f"[DEMO] 객관식 최종 선택: {len(selected_items)}개")
    
    # 요청된 주제와 난이도에 맞게 조정
    for item in selected_items:
        item["topic"] = topic
        item["level"] = level
    
    return {
        "items": selected_items
    }

def generate_demo_retry_problems(wrong_questions: List[Dict], num_questions: int) -> Dict[str, Any]:
    """DEMO 모드에서 사용할 더미 재시도 문제를 생성합니다."""
    sample_data = load_sample_problems()
    
    # 틀린 문제의 주제와 난이도를 분석
    topics = [q.get("topic", "macro") for q in wrong_questions]
    levels = [q.get("level", "basic") for q in wrong_questions]
    
    # 가장 많이 틀린 주제와 난이도 선택
    main_topic = max(set(topics), key=topics.count) if topics else "macro"
    main_level = max(set(levels), key=levels.count) if levels else "basic"
    
    # 샘플 데이터에서 해당 주제/난이도 문제 선택
    available_items = sample_data.get("items", [])
    retry_items = []
    
    for item in available_items[:num_questions]:
        retry_item = item.copy()
        retry_item["topic"] = main_topic
        retry_item["level"] = main_level
        retry_items.append(retry_item)
    
    return {
        "items": retry_items
    }
