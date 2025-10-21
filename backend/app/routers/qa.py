"""Q&A 라우터"""
from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from typing import List, Optional
from app.models.common import QARequest, QAResponse
from app.services.openai_svc_qa import generate_summary, generate_chat_response
from datetime import datetime
import os
import json
import io
import PyPDF2
from docx import Document
from app.db.mongo import get_database

router = APIRouter(prefix="/qa", tags=["qa"])

# 파일 저장 디렉토리 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
JSON_DIR = os.path.join(BASE_DIR, "data", "json")

# 디렉토리 생성
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(JSON_DIR, exist_ok=True)


# ============================================
# 파일 처리 유틸리티 함수들
# ============================================

def extract_text_from_pdf(file_content: bytes) -> str:
    """PDF 파일에서 텍스트 추출"""
    try:
        pdf_file = io.BytesIO(file_content)
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"PDF 추출 오류: {e}")
        return ""


def extract_text_from_docx(file_content: bytes) -> str:
    """DOCX 파일에서 텍스트 추출"""
    try:
        docx_file = io.BytesIO(file_content)
        doc = Document(docx_file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        print(f"DOCX 추출 오류: {e}")
        return ""


def extract_text_from_txt(file_content: bytes) -> str:
    """TXT 파일에서 텍스트 추출"""
    try:
        return file_content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            return file_content.decode('cp949')  # 한글 인코딩
        except Exception as e:
            print(f"TXT 추출 오류: {e}")
            return ""


def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """파일 타입에 따라 텍스트 추출"""
    file_ext = filename.split('.')[-1].lower()
    
    if file_ext == 'pdf':
        return extract_text_from_pdf(file_content)
    elif file_ext in ['doc', 'docx']:
        return extract_text_from_docx(file_content)
    elif file_ext == 'txt':
        return extract_text_from_txt(file_content)
    else:
        return ""


def load_document_context(document_filename: str) -> Optional[str]:
    """저장된 문서의 텍스트 컨텍스트 로드"""
    try:
        # storage_id 추출 (.json 제거)
        storage_id = document_filename.replace('.json', '')

        # 1. MongoDB에서 먼저 시도 (전체 텍스트 있음)
        try:
            db = get_database()
            collection = db["uploaded_documents"]
            # MongoDB는 async이므로 동기 방식으로는 접근 불가
            # 대신 JSON 파일에서 전체 텍스트를 로드하도록 변경 필요
        except Exception as mongo_error:
            print(f"MongoDB 로드 시도 실패: {mongo_error}")

        # 2. JSON 파일에서 로드
        json_path = os.path.join(JSON_DIR, document_filename if document_filename.endswith('.json') else f"{document_filename}.json")
        if not os.path.exists(json_path):
            print(f"JSON 파일 없음: {json_path}")
            return None

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # full_text가 있으면 사용, 없으면 파일에서 직접 읽기
        if "full_text" in data:
            return data["full_text"]

        # full_text가 없으면 원본 파일에서 다시 읽기
        full_text = ""
        for file_info in data.get("files", []):
            file_path = file_info.get("file_path")
            if file_path and os.path.exists(file_path):
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    filename = file_info.get("filename", "")
                    extracted = extract_text_from_file(content, filename)
                    full_text += extracted + "\n\n"
                except Exception as e:
                    print(f"파일 읽기 오류 ({file_path}): {e}")
                    # 미리보기라도 사용
                    full_text += file_info.get("extracted_text_preview", "") + "\n\n"
            else:
                # 파일이 없으면 미리보기 사용
                full_text += file_info.get("extracted_text_preview", "") + "\n\n"

        return full_text.strip() if full_text else None
    except Exception as e:
        print(f"문서 컨텍스트 로드 오류: {e}")
        return None


# ============================================
# 기존 엔드포인트 (문서 컨텍스트 지원 추가)
# ============================================

@router.post("/summary", response_model=QAResponse)
async def create_summary(request: QARequest):
    """
    경제 요약 생성 (문서 컨텍스트 지원)
    """
    try:
        # context가 문서 파일명이면 해당 문서 로드
        context = request.context
        print(f"[DEBUG] 원본 context: {context[:100] if context else 'None'}...")

        if context and context.endswith('.json'):
            loaded_context = load_document_context(context)
            print(f"[DEBUG] 로드된 문서 길이: {len(loaded_context) if loaded_context else 0}자")
            print(f"[DEBUG] 로드된 문서 미리보기: {loaded_context[:200] if loaded_context else 'None'}...")
            if loaded_context:
                context = loaded_context

        print(f"[DEBUG] OpenAI에 전달할 context 길이: {len(context) if context else 0}자")

        result = await generate_summary(request.question, context)
        return QAResponse(
            answer_md=result["answer_md"],
            citations=result["citations"],
            created_at=datetime.utcnow()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"요약 생성 실패: {str(e)}")


@router.post("/chat", response_model=QAResponse)
async def chat(request: QARequest):
    """
    Q&A 채팅 (문서 컨텍스트 지원)
    """
    try:
        # context가 문서 파일명이면 해당 문서 로드
        context = request.context
        print(f"[DEBUG] 원본 context: {context[:100] if context else 'None'}...")

        if context and context.endswith('.json'):
            loaded_context = load_document_context(context)
            print(f"[DEBUG] 로드된 문서 길이: {len(loaded_context) if loaded_context else 0}자")
            print(f"[DEBUG] 로드된 문서 미리보기: {loaded_context[:200] if loaded_context else 'None'}...")
            if loaded_context:
                context = loaded_context

        print(f"[DEBUG] OpenAI에 전달할 context 길이: {len(context) if context else 0}자")

        answer = await generate_chat_response(request.question, context)
        return QAResponse(
            answer_md=answer,
            citations=[],
            created_at=datetime.utcnow()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"응답 생성 실패: {str(e)}")


# ============================================
# 새로 추가: 파일 업로드 엔드포인트
# ============================================

@router.post("/upload")
async def upload_files(
    question: str = Form(...),
    files: List[UploadFile] = File(...)
):
    """
    파일 업로드 및 JSON/MongoDB 저장
    - 여러 파일 동시 업로드 가능
    - PDF, DOCX, TXT 파일에서 텍스트 추출
    - 첫 번째 파일명을 저장 ID로 사용
    - JSON 파일과 MongoDB에 동시 저장
    - 중복 파일 감지 및 기존 데이터 재사용
    """

    if not files:
        raise HTTPException(status_code=400, detail="파일이 없습니다.")

    # 첫 번째 파일명을 저장 ID로 사용 (확장자 제외)
    first_filename = files[0].filename
    storage_id = '.'.join(first_filename.split('.')[:-1])  # 확장자 제거

    # JSON 파일명 설정
    json_filename = f"{storage_id}.json"
    json_path = os.path.join(JSON_DIR, json_filename)

    uploaded_data = {
        "storage_id": storage_id,
        "question": question,
        "timestamp": datetime.utcnow().isoformat(),
        "upload_count": len(files),
        "files": []
    }

    total_text_length = 0
    all_extracted_texts = []  # MongoDB 저장용 전체 텍스트

    for file in files:
        try:
            # 파일 읽기
            content = await file.read()

            # 파일 크기 검증 (10MB)
            if len(content) > 10 * 1024 * 1024:
                continue

            # 원본 파일명 사용 (타임스탬프/해시 없이)
            original_filename = file.filename
            file_path = os.path.join(UPLOAD_DIR, original_filename)

            # 중복 파일 확인
            file_exists = os.path.exists(file_path)

            # 기존 파일이 있으면 재처리 스킵
            if file_exists:
                print(f"중복 파일 감지: {original_filename} - 재사용")
                # 기존 파일의 텍스트 추출
                with open(file_path, 'rb') as existing_file:
                    existing_content = existing_file.read()
                    extracted_text = extract_text_from_file(existing_content, original_filename)
            else:
                # 새 파일인 경우 저장
                with open(file_path, "wb") as f:
                    f.write(content)
                # 텍스트 추출
                extracted_text = extract_text_from_file(content, original_filename)

            total_text_length += len(extracted_text)
            all_extracted_texts.append(extracted_text)

            # 파일 정보
            file_data = {
                "filename": original_filename,
                "file_type": original_filename.split('.')[-1].lower(),
                "file_size_kb": round(len(content) / 1024, 2),
                "file_path": file_path,
                "extracted_text_preview": extracted_text[:500],  # 미리보기 500자
                "extracted_text_length": len(extracted_text),
                "extracted_at": datetime.utcnow().isoformat()
            }

            uploaded_data["files"].append(file_data)

        except Exception as e:
            print(f"파일 처리 오류 ({file.filename}): {e}")
            continue

    # JSON에 전체 텍스트 추가
    uploaded_data["full_text"] = "\n\n".join(all_extracted_texts)
    uploaded_data["total_text_length"] = total_text_length

    # 1. JSON 파일로 저장 (storage_id를 파일명으로 사용)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(uploaded_data, f, ensure_ascii=False, indent=2)

    # 2. MongoDB에 저장
    try:
        db = get_database()  # await 제거 (일반 함수)
        collection = db["uploaded_documents"]

        # MongoDB 문서 생성
        mongo_document = {
            "storage_id": storage_id,
            "question": question,
            "uploaded_at": datetime.utcnow(),
            "files": uploaded_data["files"],
            "total_files": len(uploaded_data["files"]),
            "total_text_length": total_text_length,
            "full_text": "\n\n".join(all_extracted_texts),  # 전체 텍스트 저장
            "status": "active"
        }

        # storage_id로 기존 문서 확인 후 업데이트 또는 삽입
        await collection.update_one(
            {"storage_id": storage_id},
            {"$set": mongo_document},
            upsert=True
        )
        print(f"MongoDB 저장 완료: {storage_id}")
    except Exception as e:
        print(f"MongoDB 저장 오류 (JSON은 정상 저장됨): {e}")

    # 응답 생성
    response_md = f"""## 📁 파일 업로드 완료

✅ **{len(uploaded_data['files'])}개** 파일이 성공적으로 처리되었습니다.

### 업로드된 파일 목록:
"""

    for idx, file_info in enumerate(uploaded_data['files'], 1):
        response_md += f"\n{idx}. **{file_info['filename']}** ({file_info['file_size_kb']} KB)\n"
        response_md += f"   - 추출된 텍스트: {file_info['extracted_text_length']:,}자\n"

    response_md += f"\n📊 총 추출 텍스트: **{total_text_length:,}자**"
    response_md += f"\n💾 저장 ID: `{storage_id}`"
    response_md += f"\n💾 JSON 저장: `{json_filename}`"
    response_md += f"\n💾 MongoDB 저장: `uploaded_documents` 컬렉션"

    return {
        "success": True,
        "storage_id": storage_id,
        "message": f"{len(uploaded_data['files'])}개 파일 업로드 완료",
        "json_path": json_path,
        "json_filename": json_filename,
        "total_files": len(uploaded_data["files"]),
        "total_text_length": total_text_length,
        "answer_md": response_md,
        "citations": [f["filename"] for f in uploaded_data["files"]]
    }


# ============================================
# 새로 추가: 업로드 목록 조회
# ============================================

@router.get("/uploads")
async def get_uploads():
    """저장된 JSON 파일 목록 조회"""
    try:
        json_files = [f for f in os.listdir(JSON_DIR) if f.endswith('.json')]
        json_files.sort(reverse=True)  # 최신순

        uploads = []
        for filename in json_files[:20]:  # 최근 20개만
            file_path = os.path.join(JSON_DIR, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # 원본 파일명 목록 추출
                original_filenames = [
                    f.get("filename", "")
                    for f in data.get("files", [])
                ]

                uploads.append({
                    "storage_id": data.get("storage_id", filename.replace('.json', '')),  # storage_id 사용
                    "filename": filename,
                    "timestamp": data.get("timestamp"),
                    "question": data.get("question"),
                    "file_count": len(data.get("files", [])),
                    "original_filenames": original_filenames  # 원본 파일명 추가
                })

        return {"uploads": uploads}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))