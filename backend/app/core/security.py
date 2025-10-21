"""보안 관련 유틸리티"""
from typing import Optional
import re


def sanitize_input(text: str, max_length: int = 5000) -> str:
    """
    입력 텍스트 검증 및 정제
    - 최대 길이 제한
    - 기본적인 인젝션 패턴 검사
    """
    if not text:
        return ""
    
    # 길이 제한
    text = text[:max_length]
    
    # 기본적인 XSS 방지 (추가 필터링 가능)
    # 실제 환경에서는 더 정교한 검증 필요
    
    return text.strip()


def is_safe_prompt(text: str) -> bool:
    """
    프롬프트 인젝션 기본 체크
    """
    dangerous_patterns = [
        r"ignore\s+previous\s+instructions",
        r"system\s*:",
        r"<\s*script",
    ]
    
    text_lower = text.lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, text_lower):
            return False
    
    return True

