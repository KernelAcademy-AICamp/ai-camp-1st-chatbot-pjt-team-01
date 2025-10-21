"""RAG (Retrieval-Augmented Generation) 서비스"""
import os
import pickle
from typing import List, Optional
from langchain.text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
from app.core.config import settings

# 벡터 스토어 저장 디렉토리
VECTOR_STORE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "vector_stores")
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)


class RAGService:
    """RAG 서비스 클래스"""

    def __init__(self):
        """초기화"""
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            openai_api_key=settings.OPENAI_API_KEY
        )

    def create_vector_store(self, upload_id: str, texts: List[str]) -> FAISS:
        """
        텍스트 리스트로부터 벡터 스토어 생성

        Args:
            upload_id: 문서 업로드 ID
            texts: 텍스트 청크 리스트

        Returns:
            FAISS 벡터 스토어
        """
        # 벡터 스토어 생성
        knowledge_base = FAISS.from_texts(texts, self.embeddings)

        # 벡터 스토어 저장
        vector_store_path = os.path.join(VECTOR_STORE_DIR, f"{upload_id}.faiss")
        knowledge_base.save_local(vector_store_path)

        return knowledge_base

    def load_vector_store(self, upload_id: str) -> Optional[FAISS]:
        """
        저장된 벡터 스토어 로드

        Args:
            upload_id: 문서 업로드 ID

        Returns:
            FAISS 벡터 스토어 또는 None
        """
        try:
            vector_store_path = os.path.join(VECTOR_STORE_DIR, f"{upload_id}.faiss")

            if not os.path.exists(vector_store_path):
                return None

            knowledge_base = FAISS.load_local(
                vector_store_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )

            return knowledge_base
        except Exception as e:
            print(f"벡터 스토어 로드 실패: {e}")
            return None

    def search_similar_documents(self, upload_id: str, question: str, k: int = 4) -> List[str]:
        """
        질문과 유사한 문서 청크 검색

        Args:
            upload_id: 문서 업로드 ID
            question: 검색 질문
            k: 반환할 문서 개수

        Returns:
            유사한 문서 청크 리스트
        """
        knowledge_base = self.load_vector_store(upload_id)

        if not knowledge_base:
            return []

        # 유사도 검색
        docs = knowledge_base.similarity_search(question, k=k)

        return [doc.page_content for doc in docs]

    def generate_answer(self, question: str, upload_id: str) -> dict:
        """
        RAG 기반 답변 생성

        Args:
            question: 사용자 질문
            upload_id: 문서 업로드 ID

        Returns:
            답변 및 메타데이터
        """
        # 벡터 스토어 로드
        knowledge_base = self.load_vector_store(upload_id)

        if not knowledge_base:
            raise ValueError(f"벡터 스토어를 찾을 수 없습니다: {upload_id}")

        # 관련 문서 검색
        references = knowledge_base.similarity_search(question, k=4)

        if not references:
            return {
                "answer": "관련 문서를 찾을 수 없습니다.",
                "references": [],
                "tokens_used": 0
            }

        # QA 체인 생성
        chain = load_qa_chain(self.llm, chain_type="stuff")

        # 답변 생성 (토큰 사용량 추적)
        with get_openai_callback() as cb:
            response = chain.run(input_documents=references, question=question)
            tokens_used = cb.total_tokens

        return {
            "answer": response,
            "references": [doc.page_content[:200] + "..." for doc in references],
            "tokens_used": tokens_used,
            "reference_count": len(references)
        }


# 싱글톤 인스턴스
rag_service = RAGService()
