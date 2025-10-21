"""PDF를 처리하여 임베딩을 생성하고 MongoDB에 저장하는 스크립트"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# .env 파일 먼저 로드 (settings 임포트 전에)
from dotenv import load_dotenv
env_path = project_root.parent / ".env"
load_dotenv(env_path)

from motor.motor_asyncio import AsyncIOMotorClient
import os

from app.services.pdf_service import PDFService
from app.services.embedding_service import EmbeddingService
from app.core.config import settings


async def process_pdf_to_mongodb():
    """PDF 파일을 처리하여 MongoDB에 임베딩 저장"""

    print("=" * 60)
    print("📄 PDF 임베딩 처리 시작")
    print("=" * 60)

    # 1. PDF 파일 경로
    pdf_path = project_root / "data" / "pdfs" / "2024_경제금융용어_700선.pdf"

    if not pdf_path.exists():
        print(f"❌ PDF 파일을 찾을 수 없습니다: {pdf_path}")
        return

    print(f"✅ PDF 파일 찾음: {pdf_path}")
    print(f"   크기: {pdf_path.stat().st_size / 1024 / 1024:.2f} MB")

    # 2. PDF 텍스트 추출
    print("\n📖 PDF 텍스트 추출 중...")
    pdf_service = PDFService()

    full_text = pdf_service.extract_text_from_pdf(pdf_path)
    print(f"✅ 전체 텍스트 추출 완료: {len(full_text)} 문자")

    # 3. 경제 용어 추출
    print("\n🔍 경제 용어 추출 중...")
    terms = pdf_service.extract_economic_terms(full_text)
    print(f"✅ {len(terms)}개 용어 추출 완료")

    if len(terms) > 0:
        print(f"\n📝 샘플 용어 (처음 3개):")
        for i, term in enumerate(terms[:3], 1):
            print(f"   {i}. {term['term']}")
            if term.get('english'):
                print(f"      영문: {term['english']}")
            print(f"      정의: {term['definition'][:100]}...")

    # 4. 임베딩 생성
    print(f"\n🤖 임베딩 생성 중 (모델: text-embedding-3-small)...")
    embedding_service = EmbeddingService()

    try:
        terms_with_embeddings = await embedding_service.create_term_embeddings(terms)
        print(f"✅ {len(terms_with_embeddings)}개 용어 임베딩 생성 완료")

        if len(terms_with_embeddings) > 0:
            print(f"   임베딩 차원: {len(terms_with_embeddings[0]['embedding'])}")

    except Exception as e:
        print(f"❌ 임베딩 생성 실패: {e}")
        return

    # 5. MongoDB 연결
    print(f"\n🔌 MongoDB 연결 중...")
    client = AsyncIOMotorClient(settings.MONGO_URI, tlsAllowInvalidCertificates=True)
    db = client[settings.MONGO_DB]
    collection = db["economic_terms"]

    try:
        await client.admin.command('ping')
        print(f"✅ MongoDB 연결 성공")
    except Exception as e:
        print(f"❌ MongoDB 연결 실패: {e}")
        client.close()
        return

    # 6. 기존 데이터 삭제 (선택사항)
    existing_count = await collection.count_documents({})
    if existing_count > 0:
        print(f"\n⚠️  기존 데이터 {existing_count}개 발견")
        print("   기존 데이터를 삭제하고 새로 저장합니다...")
        await collection.delete_many({})
        print("✅ 기존 데이터 삭제 완료")

    # 7. MongoDB에 저장
    print(f"\n💾 MongoDB에 저장 중...")

    documents = []
    for term_data in terms_with_embeddings:
        doc = {
            "term": term_data["term"],
            "english": term_data.get("english", ""),
            "definition": term_data["definition"],
            "embedding": term_data["embedding"],
            "embedding_text": term_data["embedding_text"],
            "source": "2024_경제금융용어_700선.pdf",
            "created_at": datetime.utcnow()
        }
        documents.append(doc)

    if documents:
        result = await collection.insert_many(documents)
        print(f"✅ {len(result.inserted_ids)}개 문서 저장 완료")

    # 8. 벡터 검색 인덱스 생성 (MongoDB Atlas Vector Search용)
    print(f"\n📊 벡터 검색 인덱스 확인 중...")

    # 인덱스 확인
    indexes = await collection.list_indexes().to_list(length=100)
    index_names = [idx["name"] for idx in indexes]

    if "embedding_index" in index_names:
        print(f"✅ 벡터 검색 인덱스가 이미 존재합니다")
    else:
        print(f"⚠️  벡터 검색 인덱스가 없습니다")
        print(f"   MongoDB Atlas Console에서 다음 인덱스를 생성하세요:")
        index_json = """
   {
     "mappings": {
       "dynamic": true,
       "fields": {
         "embedding": {
           "type": "knnVector",
           "dimensions": 1536,
           "similarity": "cosine"
         }
       }
     }
   }
        """
        print(index_json)

    # 9. 통계 출력
    print("\n" + "=" * 60)
    print("📊 처리 완료 통계")
    print("=" * 60)
    print(f"총 용어 수: {len(terms_with_embeddings)}")
    print(f"MongoDB 컬렉션: {settings.MONGO_DB}.economic_terms")
    print(f"임베딩 모델: text-embedding-3-small")
    print(f"임베딩 차원: 1536")
    print("=" * 60)

    # 10. 샘플 검색 테스트
    print("\n🔍 샘플 검색 테스트...")
    test_query = "인플레이션이란?"
    query_embedding = await embedding_service.create_embedding(test_query)

    # 간단한 코사인 유사도 검색
    all_docs = await collection.find({}).to_list(length=1000)

    similarities = []
    for doc in all_docs:
        similarity = embedding_service.cosine_similarity(query_embedding, doc["embedding"])
        similarities.append((doc["term"], similarity))

    # 상위 3개
    similarities.sort(key=lambda x: x[1], reverse=True)
    print(f"쿼리: '{test_query}'")
    print(f"상위 3개 유사 용어:")
    for i, (term, score) in enumerate(similarities[:3], 1):
        print(f"   {i}. {term} (유사도: {score:.4f})")

    client.close()
    print("\n✅ 모든 처리 완료!")


if __name__ == "__main__":
    asyncio.run(process_pdf_to_mongodb())
