"""문서 업로드 관련 데이터 모델 (추가 기능)"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId


# ===== 문서 업로드 =====
class TextChunk(BaseModel):
    """텍스트 청크"""
    chunk_id: str
    chunk_index: int
    text: str
    text_length: int


class UploadedFile(BaseModel):
    """업로드된 파일 정보"""
    file_id: str
    filename: str
    file_type: str
    file_size: int
    file_hash: str  # 파일 해시값 (중복 체크용)
    file_path: str
    extracted_text: str  # 전체 텍스트 (검색용, 선택적)
    extracted_text_length: int
    text_preview: str
    chunks: List[TextChunk] = []  # 텍스트 청크들
    is_chunked: bool = False  # 청킹 여부
    processing_status: str = "completed"
    error_message: Optional[str] = None
    processed_at: datetime = Field(default_factory=datetime.utcnow)


class DocumentUpload(BaseModel):
    """MongoDB에 저장될 문서 정보"""
    upload_id: str
    question: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    files: List[UploadedFile] = []
    total_files: int = 0
    total_text_length: int = 0
    total_size_bytes: int = 0
    status: str = "active"
    tags: List[str] = []

    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
