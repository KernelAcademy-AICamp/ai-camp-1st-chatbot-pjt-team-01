"""경제 용어 벡터 검색 서비스"""
from typing import List, Dict
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.services.embedding_service import EmbeddingService


class TermSearchService:
    """경제 용어 벡터 검색"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["economic_terms"]
        self.embedding_service = EmbeddingService()

    async def search_similar_terms(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        쿼리와 유사한 경제 용어 검색

        Args:
            query: 사용자 질문/검색어
            top_k: 반환할 결과 개수

        Returns:
            유사한 용어 리스트 (유사도 포함)
        """
        # 1. 쿼리 임베딩 생성
        query_embedding = await self.embedding_service.create_embedding(query)

        # 2. 모든 용어 가져오기 (MongoDB Atlas Vector Search 인덱스가 없는 경우)
        all_terms = await self.collection.find({}).to_list(length=1000)

        # 3. 코사인 유사도 계산
        similarities = []
        for term in all_terms:
            if "embedding" in term:
                similarity = self.embedding_service.cosine_similarity(
                    query_embedding, term["embedding"]
                )
                similarities.append({
                    "term": term["term"],
                    "english": term.get("english", ""),
                    "definition": term["definition"],
                    "similarity": similarity,
                    "similarity_percent": round(similarity * 100, 1)
                })

        # 4. 유사도 높은 순으로 정렬
        similarities.sort(key=lambda x: x["similarity"], reverse=True)

        # 5. 상위 k개 반환
        return similarities[:top_k]

    async def search_similar_terms_atlas(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        MongoDB Atlas Vector Search를 사용한 검색 (인덱스 필요)

        Args:
            query: 사용자 질문/검색어
            top_k: 반환할 결과 개수

        Returns:
            유사한 용어 리스트
        """
        # 1. 쿼리 임베딩 생성
        query_embedding = await self.embedding_service.create_embedding(query)

        # 2. MongoDB Atlas Vector Search 쿼리
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "embedding_index",
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": 100,
                    "limit": top_k
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "term": 1,
                    "english": 1,
                    "definition": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]

        try:
            results = await self.collection.aggregate(pipeline).to_list(length=top_k)

            # 스코어를 퍼센트로 변환
            for result in results:
                result["similarity"] = result["score"]
                result["similarity_percent"] = round(result["score"] * 100, 1)

            return results

        except Exception as e:
            # Vector Search 인덱스가 없으면 일반 검색으로 폴백
            print(f"Atlas Vector Search 실패, 일반 검색으로 전환: {e}")
            return await self.search_similar_terms(query, top_k)
