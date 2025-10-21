"""PDF 텍스트 추출 서비스"""
import pdfplumber
from pathlib import Path
from typing import List, Dict
import re


class PDFService:
    """PDF 파일 처리 및 텍스트 추출"""

    @staticmethod
    def extract_text_from_pdf(pdf_path: Path) -> str:
        """
        PDF 파일에서 전체 텍스트 추출

        Args:
            pdf_path: PDF 파일 경로

        Returns:
            추출된 텍스트
        """
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    @staticmethod
    def extract_text_by_page(pdf_path: Path) -> List[Dict[str, any]]:
        """
        PDF 파일에서 페이지별로 텍스트 추출

        Args:
            pdf_path: PDF 파일 경로

        Returns:
            페이지별 텍스트 딕셔너리 리스트
            [{"page_num": 1, "text": "..."}, ...]
        """
        pages = []
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    pages.append({
                        "page_num": i,
                        "text": page_text.strip()
                    })
        return pages

    @staticmethod
    def extract_economic_terms(text: str) -> List[Dict[str, str]]:
        """
        텍스트에서 경제 용어와 정의 추출

        패턴: "용어명 [영문] 설명..."

        Args:
            text: 추출할 텍스트

        Returns:
            용어 딕셔너리 리스트
            [{"term": "GDP", "english": "Gross Domestic Product", "definition": "..."}, ...]
        """
        terms = []

        # 줄 단위로 분리
        lines = text.split('\n')

        current_term = None
        current_definition = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 패턴 1: "용어명 [영문]" 형태 감지
            # 예: "국내총생산 [Gross Domestic Product, GDP]"
            term_match = re.match(r'^([가-힣\s]+)\s*\[([A-Za-z\s,]+)\]', line)

            if term_match:
                # 이전 용어 저장
                if current_term:
                    terms.append({
                        "term": current_term["term"],
                        "english": current_term["english"],
                        "definition": ' '.join(current_definition).strip()
                    })

                # 새 용어 시작
                korean_term = term_match.group(1).strip()
                english_term = term_match.group(2).strip()

                current_term = {
                    "term": korean_term,
                    "english": english_term
                }
                current_definition = []

                # 정의가 같은 줄에 있는 경우
                remaining = line[term_match.end():].strip()
                if remaining:
                    current_definition.append(remaining)

            # 패턴 2: 용어만 있는 경우 (영문 없음)
            elif re.match(r'^[가-힣\s]+$', line) and len(line) < 30:
                # 이전 용어 저장
                if current_term:
                    terms.append({
                        "term": current_term["term"],
                        "english": current_term.get("english", ""),
                        "definition": ' '.join(current_definition).strip()
                    })

                current_term = {
                    "term": line.strip(),
                    "english": ""
                }
                current_definition = []

            # 정의 텍스트 추가
            elif current_term:
                current_definition.append(line)

        # 마지막 용어 저장
        if current_term:
            terms.append({
                "term": current_term["term"],
                "english": current_term.get("english", ""),
                "definition": ' '.join(current_definition).strip()
            })

        # 빈 정의 제거
        terms = [t for t in terms if t["definition"]]

        return terms

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        텍스트를 청크로 분할 (임베딩용)

        Args:
            text: 분할할 텍스트
            chunk_size: 청크 크기 (문자 수)
            overlap: 청크 간 겹치는 문자 수

        Returns:
            텍스트 청크 리스트
        """
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]

            # 문장 중간에서 끊기지 않도록 마지막 마침표 찾기
            if end < text_length:
                last_period = chunk.rfind('.')
                if last_period > chunk_size // 2:  # 청크의 절반 이상에서 마침표 발견
                    end = start + last_period + 1
                    chunk = text[start:end]

            chunks.append(chunk.strip())
            start = end - overlap

        return chunks
