# Noir Luxe Economy Dashboard

최신 경제 지표를 한눈에 보여주는 AI 기반 풀스택 웹 애플리케이션

## 기술 스택

### Frontend
- React 18 + Vite + TypeScript
- Tailwind CSS + shadcn/ui
- Recharts (차트)
- framer-motion (애니메이션)
- React Query (상태 관리)

### Backend
- Python 3.11 + FastAPI
- Motor (MongoDB async driver)
- OpenAI API
- httpx (async HTTP client)

### Database
- MongoDB

## 주요 기능

- **메인 대시보드**: 실시간 경제 지표 (CPI, GDP, 실업률, 기준금리, 환율, 주가지수)
- **요약/Q&A**: AI 기반 경제 질문 답변
- **경제문제 생성**: 난이도별/주제별 맞춤 문제 생성
- **자료추천**: 학습 목적에 맞는 경제 자료 추천

## 🚀 빠른 시작

### Docker Compose (추천)

```bash
# 1. 환경 변수 설정
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# 2. 실행
docker-compose up -d

# 3. 접속
# 프론트엔드: http://localhost
# 백엔드: http://localhost:8000
# API 문서: http://localhost:8000/docs
```

### 로컬 개발

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (새 터미널)
cd frontend
pnpm install
pnpm dev
```

자세한 내용은 [빠른 시작 가이드](QUICKSTART.md)를 참고하세요.

## 프로젝트 구조

```
fast_01/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── models/
│   │   └── db/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── lib/
│   │   └── App.tsx
│   ├── public/
│   └── package.json
├── docker-compose.yml
└── README.md
```

## API 엔드포인트

- `GET /api/health` - 헬스 체크
- `POST /api/qa/summary` - 경제 요약 생성
- `POST /api/qa/chat` - Q&A 채팅
- `POST /api/problems` - 경제 문제 생성
- `POST /api/recommend` - 자료 추천
- `GET /api/market/kpis` - 주요 경제 지표
- `GET /api/market/trends` - 경제 트렌드 시계열
- `GET /api/news` - 경제 뉴스

## 라이선스

MIT

