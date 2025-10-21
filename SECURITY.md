# 보안 가이드

## 민감한 정보 보호

이 프로젝트는 OpenAI API 키와 같은 민감한 정보를 사용합니다. 다음 규칙을 **반드시** 준수하세요.

### ✅ 해야 할 것

1. **환경변수 파일 사용**
   - `.env` 파일에 API 키와 민감한 정보 저장
   - `.env.example` 파일을 복사하여 `.env` 생성
   ```bash
   cp .env.example .env
   # 그 다음 .env 파일을 열어 실제 API 키 입력
   ```

2. **Git에 커밋하기 전 확인**
   ```bash
   git status  # .env 파일이 나타나면 안 됩니다!
   ```

3. **환경변수를 코드에서 사용**
   ```python
   # Python (FastAPI)
   from app.core.config import settings
   api_key = settings.OPENAI_API_KEY
   ```

### ❌ 절대 하지 말아야 할 것

1. **API 키를 코드에 직접 작성 금지**
   ```python
   # ❌ 절대 이렇게 하지 마세요!
   OPENAI_API_KEY = "sk-proj-xxxxx"
   ```

2. **`.env` 파일을 Git에 커밋 금지**
   - `.gitignore`에 이미 포함되어 있으나 실수로 추가하지 않도록 주의

3. **민감한 정보를 로그에 출력 금지**
   ```python
   # ❌ 금지
   print(f"API Key: {api_key}")

   # ✅ 허용
   print("API 호출 성공")
   ```

## `.gitignore`에 포함된 민감한 파일

다음 파일/폴더는 자동으로 Git에서 제외됩니다:

### 환경변수 및 설정
- `.env`
- `.env.local`
- `backend/.env`
- **단, `.env.example`은 포함됩니다** (실제 키 없이 템플릿만 제공)

### 업로드된 파일
- `backend/uploads/` - 사용자가 업로드한 문서
- `backend/data/json/` - 업로드 메타데이터
- `*.pdf`, `*.docx`, `*.doc`, `*.txt` - 문서 파일

### 임시 파일
- `backend/app/services/env*.txt`
- `backend/app/services/res/`
- `*.ipynb` (Jupyter 노트북)

## API 키가 노출된 경우

만약 실수로 API 키를 GitHub에 커밋한 경우:

1. **즉시 API 키 무효화**
   - OpenAI 대시보드에서 해당 키 삭제
   - 새 키 발급

2. **Git 히스토리에서 제거**
   ```bash
   # BFG Repo-Cleaner 사용 (권장)
   # 또는 git filter-branch 사용
   # 자세한 방법은 GitHub 문서 참조
   ```

3. **새 키로 `.env` 업데이트**

## 추가 보안 조치

1. **MongoDB 보안**
   - 프로덕션에서는 반드시 인증 활성화
   - `MONGODB_USERNAME`, `MONGODB_PASSWORD` 설정

2. **CORS 설정**
   - `CORS_ORIGINS`를 프로덕션 도메인으로 제한

3. **Rate Limiting**
   - `RATE_LIMIT_PER_MINUTE` 적절히 설정

## 문의

보안 관련 문제를 발견하셨나요? 공개 이슈가 아닌 비공개 채널로 보고해주세요.
