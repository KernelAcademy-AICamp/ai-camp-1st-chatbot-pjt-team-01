# 빠른 시작 가이드

5분 안에 Noir Luxe Economy를 실행해보세요!

## 🚀 가장 빠른 방법: Docker Compose

### 필요한 것
- Docker
- Docker Compose
- OpenAI API Key

### 실행 단계

1. **저장소 클론**
```bash
git clone <repository-url>
cd fast_01
```

2. **환경 변수 설정**
```bash
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

3. **실행**
```bash
docker-compose up -d
```

4. **접속**
- 🌐 프론트엔드: http://localhost
- 🔌 백엔드 API: http://localhost:8000
- 📚 API 문서: http://localhost:8000/docs

5. **종료**
```bash
docker-compose down
```

---

## 💻 로컬 개발 (Docker 없이)

### 필요한 것
- Node.js 18+
- Python 3.11+
- MongoDB
- OpenAI API Key

### 실행 단계

**1단계: MongoDB 실행**
```bash
# Docker 사용
docker run -d -p 27017:27017 --name mongo mongo:6

# 또는 로컬 MongoDB
mongod
```

**2단계: 백엔드 실행**
```bash
cd backend

# 가상 환경 생성
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cat > .env << EOF
MONGO_URI=mongodb://localhost:27017
MONGO_DB=econlux
OPENAI_API_KEY=sk-your-key-here
CORS_ORIGINS=http://localhost:5173
EOF

# 서버 실행
uvicorn app.main:app --reload --port 8000
```

**3단계: 프론트엔드 실행** (새 터미널)
```bash
cd frontend

# pnpm 설치 (없는 경우)
npm install -g pnpm

# 의존성 설치
pnpm install

# 서버 실행
pnpm dev
```

**4단계: 접속**
- http://localhost:5173

---

## 🧪 테스트 실행

```bash
# 백엔드 테스트
cd backend
pytest

# 프론트엔드 테스트
cd frontend
pnpm test
```

---

## 📖 주요 기능

### 1. 대시보드 (/)
- 8개 주요 경제 지표 (CPI, GDP, 실업률, 금리, 환율, 증시)
- 인터랙티브 차트 2개
- 경제 뉴스 6개

### 2. 요약/Q&A (/qa)
- AI 기반 경제 질문 답변
- 샘플 프롬프트 제공
- Markdown 응답 렌더링

### 3. 문제 생성 (/problems)
- 난이도별 (초/중/고)
- 주제별 (거시/금융/무역/통계)
- 객관식/서술형
- CSV 내보내기

### 4. 자료 추천 (/recommend)
- 주제별 맞춤 추천
- 북마크 기능
- 태그 분류

---

## 🎨 디자인 테마

**Noir Luxe** - 다크 기반의 럭셔리 테마
- 배경: `#0B0D0E`
- 카드: `#121416`
- 하이라이트: `#C8A96A` (골드)
- 폰트: Inter Tight (헤드라인), Inter (본문)

---

## 🔧 트러블슈팅

### 포트가 이미 사용 중
```bash
# 포트 확인
lsof -i :8000  # 백엔드
lsof -i :5173  # 프론트엔드

# 프로세스 종료
kill -9 <PID>
```

### OpenAI API 오류
- API 키 확인: https://platform.openai.com/api-keys
- 사용량 확인: https://platform.openai.com/usage
- `.env` 파일에 올바르게 설정되었는지 확인

### MongoDB 연결 실패
```bash
# MongoDB 상태 확인
docker ps | grep mongo

# 재시작
docker restart mongo
```

---

## 📚 더 알아보기

- [배포 가이드](DEPLOYMENT.md)
- [API 문서](API_DOCS.md)
- [기여 가이드](CONTRIBUTING.md)

---

## 🆘 도움이 필요한가요?

- 이슈 등록: [GitHub Issues]
- 문서 확인: `/docs` 디렉토리
- 커뮤니티: [Discord/Slack]

---

즐거운 개발 되세요! 🎉

