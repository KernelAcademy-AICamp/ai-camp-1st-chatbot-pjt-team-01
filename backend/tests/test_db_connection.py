"""MongoDB 연결 테스트"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

# .env 파일 로드 (프로젝트 루트에서)
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
TEST_DB_NAME = 'test_db'
TEST_COLLECTION_NAME = 'test_collection'


async def test_connection():
    """MongoDB 연결 테스트"""
    print(f"🔌 Connecting to MongoDB...")
    print(f"📍 URI: {MONGODB_URI}")

    try:
        # MongoDB 클라이언트 생성 (SSL 검증 비활성화)
        client = AsyncIOMotorClient(
            MONGODB_URI,
            tlsAllowInvalidCertificates=True
        )

        # 연결 테스트
        await client.admin.command('ping')
        print("✅ MongoDB connection successful!")

        # 테스트 데이터베이스 선택
        db = client[TEST_DB_NAME]
        collection = db[TEST_COLLECTION_NAME]

        # 기존 데이터 삭제 (테스트 초기화)
        await collection.delete_many({})
        print(f"🧹 Cleaned up existing test data")

        # 테스트 데이터 삽입
        test_documents = [
            {"name": "Alice", "age": 25, "city": "Seoul"},
            {"name": "Bob", "age": 30, "city": "Busan"},
            {"name": "Charlie", "age": 35, "city": "Incheon"}
        ]

        result = await collection.insert_many(test_documents)
        print(f"📝 Inserted {len(result.inserted_ids)} documents")
        print(f"   IDs: {result.inserted_ids}")

        # 데이터 조회
        print(f"\n📖 Reading data from collection...")
        cursor = collection.find({})
        documents = await cursor.to_list(length=100)

        print(f"✅ Found {len(documents)} documents:")
        for doc in documents:
            print(f"   - {doc['name']}: {doc['age']} years old, lives in {doc['city']}")

        # 특정 조건으로 조회
        print(f"\n🔍 Querying documents where age > 28...")
        cursor = collection.find({"age": {"$gt": 28}})
        filtered_docs = await cursor.to_list(length=100)

        print(f"✅ Found {len(filtered_docs)} documents:")
        for doc in filtered_docs:
            print(f"   - {doc['name']}: {doc['age']} years old")

        # 데이터 업데이트
        print(f"\n✏️  Updating Alice's age...")
        update_result = await collection.update_one(
            {"name": "Alice"},
            {"$set": {"age": 26}}
        )
        print(f"✅ Updated {update_result.modified_count} document(s)")

        # 업데이트 확인
        alice = await collection.find_one({"name": "Alice"})
        print(f"   Alice's new age: {alice['age']}")

        # 데이터 삭제 (주석 처리하여 데이터 유지)
        # print(f"\n🗑️  Deleting test data...")
        # delete_result = await collection.delete_many({})
        # print(f"✅ Deleted {delete_result.deleted_count} document(s)")
        print(f"\n💾 Test data preserved in database")

        # 연결 종료
        client.close()
        print(f"\n🔌 MongoDB connection closed")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def check_collections():
    """데이터베이스의 컬렉션 목록 확인"""
    print(f"\n📚 Checking available collections...")

    try:
        client = AsyncIOMotorClient(
            MONGODB_URI,
            tlsAllowInvalidCertificates=True
        )
        db = client[TEST_DB_NAME]

        collections = await db.list_collection_names()
        print(f"✅ Found {len(collections)} collection(s):")
        for coll in collections:
            print(f"   - {coll}")

        client.close()

    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("🧪 MongoDB Connection Test")
    print("=" * 60)

    # 연결 및 CRUD 테스트
    success = await test_connection()

    # 컬렉션 목록 확인
    await check_collections()

    print("=" * 60)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Tests failed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
