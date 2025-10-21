"""한국어 임베딩 생성 서비스 (ko-sroberta-multitask)"""
from typing import List, Dict
import asyncio
import os
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """한국어 최적화 임베딩 생성 (jhgan/ko-sroberta-multitask)"""

    def __init__(self):
        # 한국어 특화 오픈소스 모델 사용
        # 로컬 캐시 경로 직접 지정
        model_path = os.path.expanduser("~/.cache/huggingface/hub/models--jhgan--ko-sroberta-multitask")
        self.model = SentenceTransformer(model_path)
        self.embedding_dimension = 768  # ko-sroberta는 768차원

    async def create_embedding(self, text: str) -> List[float]:
        """
        단일 텍스트에 대한 임베딩 생성

        Args:
            text: 임베딩할 텍스트

        Returns:
            임베딩 벡터 (768차원)
        """
        # 빈 텍스트 처리
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        # sentence-transformers는 동기 함수이므로 run_in_executor로 비동기 처리
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            None,
            self.model.encode,
            text
        )

        return embedding.tolist()

    async def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        여러 텍스트에 대한 임베딩 배치 생성

        Args:
            texts: 임베딩할 텍스트 리스트

        Returns:
            임베딩 벡터 리스트
        """
        if not texts:
            return []

        # 빈 텍스트 필터링
        texts = [t for t in texts if t and t.strip()]

        if not texts:
            return []

        # sentence-transformers 배치 인코딩 (동기 → 비동기 변환)
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None,
            self.model.encode,
            texts
        )

        return [emb.tolist() for emb in embeddings]

    async def create_term_embeddings(self, terms: List[Dict[str, str]]) -> List[Dict]:
        """
        경제 용어 리스트에 대한 임베딩 생성

        Args:
            terms: 용어 딕셔너리 리스트
                   [{"term": "GDP", "english": "...", "definition": "..."}, ...]

        Returns:
            임베딩이 추가된 용어 리스트
            [{"term": "...", "embedding": [...], ...}, ...]
        """
        if not terms:
            return []

        # 각 용어에 대해 임베딩할 텍스트 생성
        # 형식: "용어명 (영문명): 정의"
        embedding_texts = []
        for term in terms:
            text_parts = [term["term"]]

            if term.get("english"):
                text_parts.append(f"({term['english']})")

            if term.get("definition"):
                text_parts.append(f": {term['definition']}")

            embedding_text = " ".join(text_parts)
            embedding_texts.append(embedding_text)

        # 배치로 임베딩 생성
        embeddings = await self.create_embeddings_batch(embedding_texts)

        # 용어에 임베딩 추가
        result = []
        for i, term in enumerate(terms):
            term_with_embedding = term.copy()
            term_with_embedding["embedding"] = embeddings[i]
            term_with_embedding["embedding_text"] = embedding_texts[i]  # 디버깅용
            result.append(term_with_embedding)

        return result

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """
        코사인 유사도 계산

        Args:
            vec1: 벡터 1
            vec2: 벡터 2

        Returns:
            유사도 (-1 ~ 1)
        """
        import math

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)
