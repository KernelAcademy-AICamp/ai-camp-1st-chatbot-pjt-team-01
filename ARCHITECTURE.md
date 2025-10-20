# 시스템 아키텍처

Noir Luxe Economy의 전체 아키텍처를 설명합니다.

## 개요

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTP/HTTPS
       ↓
┌──────────────────────┐
│   Frontend (React)   │
│  - Vite + TypeScript │
│  - Tailwind CSS      │
│  - React Query       │
└──────┬───────────────┘
       │ REST API
       ↓
┌──────────────────────┐
│   Backend (FastAPI)  │
│  - Python 3.11       │
│  - Pydantic          │
│  - Motor (async)     │
└──────┬───────────────┘
       │
       ├─────────────────┐
       │                 │
       ↓                 ↓
┌─────────────┐   ┌──────────────┐
│   MongoDB   │   │  OpenAI API  │
│   (NoSQL)   │   │  (GPT-4)     │
└─────────────┘   └──────────────┘
```

---

## 프론트엔드 아키텍처

### 디렉토리 구조

```
frontend/
├── src/
│   ├── components/      # UI 컴포넌트
│   │   ├── ui/         # 기본 UI 요소
│   │   ├── Layout.tsx
│   │   ├── Sidebar.tsx
│   │   └── ...
│   ├── pages/          # 페이지 컴포넌트
│   │   ├── Dashboard.tsx
│   │   ├── QAPage.tsx
│   │   └── ...
│   ├── lib/            # 유틸리티
│   │   ├── api.ts      # API 클라이언트
│   │   ├── types.ts    # TypeScript 타입
│   │   └── utils.ts    # 헬퍼 함수
│   ├── App.tsx
│   └── main.tsx
├── public/
└── package.json
```

### 주요 라이브러리

| 라이브러리 | 용도 | 버전 |
|-----------|------|------|
| React | UI 프레임워크 | 18.2 |
| Vite | 빌드 도구 | 5.0 |
| TypeScript | 타입 시스템 | 5.3 |
| Tailwind CSS | 스타일링 | 3.4 |
| React Router | 라우팅 | 6.21 |
| React Query | 상태 관리 | 5.17 |
| Recharts | 차트 | 2.10 |
| framer-motion | 애니메이션 | 10.18 |
| lucide-react | 아이콘 | 0.303 |

### 상태 관리

**React Query**를 사용한 서버 상태 관리:
- 캐싱
- 자동 재시도
- 백그라운드 업데이트
- Optimistic updates

```typescript
// 예시
const { data, isLoading, error, refetch } = useQuery({
  queryKey: ['kpis'],
  queryFn: async () => (await getKPIs()).data,
  staleTime: 5 * 60 * 1000, // 5분
})
```

### 라우팅

| 경로 | 페이지 | 설명 |
|------|--------|------|
| `/` | Dashboard | 메인 대시보드 |
| `/qa` | QAPage | AI Q&A |
| `/problems` | ProblemsPage | 문제 생성 |
| `/recommend` | RecommendPage | 자료 추천 |
| `*` | NotFound | 404 페이지 |

---

## 백엔드 아키텍처

### 디렉토리 구조

```
backend/
├── app/
│   ├── main.py           # FastAPI 앱
│   ├── core/
│   │   ├── config.py     # 설정
│   │   └── security.py   # 보안
│   ├── routers/          # API 라우터
│   │   ├── health.py
│   │   ├── qa.py
│   │   ├── problems.py
│   │   ├── recommend.py
│   │   └── market.py
│   ├── services/         # 비즈니스 로직
│   │   ├── openai_svc.py
│   │   └── market_adapters.py
│   ├── models/           # 데이터 모델
│   │   └── common.py
│   └── db/
│       └── mongo.py      # DB 연결
├── tests/
└── requirements.txt
```

### 레이어 구조

```
API Layer (routers/)
    ↓
Service Layer (services/)
    ↓
Data Layer (db/, external APIs)
```

**관심사의 분리:**
- 라우터: HTTP 요청/응답 처리
- 서비스: 비즈니스 로직
- 데이터: DB 및 외부 API 연동

### API 엔드포인트

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/api/health` | GET | 헬스 체크 |
| `/api/market/kpis` | GET | 경제 지표 |
| `/api/market/trends` | GET | 시계열 데이터 |
| `/api/market/news` | GET | 뉴스 |
| `/api/qa/summary` | POST | AI 요약 |
| `/api/qa/chat` | POST | AI 채팅 |
| `/api/problems` | POST | 문제 생성 |
| `/api/recommend` | POST | 자료 추천 |
| `/api/recommend/bookmark` | POST | 북마크 추가 |
| `/api/recommend/bookmarks` | GET | 북마크 조회 |

### 비동기 처리

**Motor (async MongoDB driver)**를 사용한 비동기 DB 작업:

```python
@router.get("/bookmarks")
async def get_bookmarks(db: AsyncIOMotorDatabase = Depends(get_database)):
    cursor = db.bookmarks.find().sort("created_at", -1)
    bookmarks = await cursor.to_list(length=50)
    return {"bookmarks": bookmarks}
```

### OpenAI 통합

**Tenacity**를 사용한 재시도 로직:

```python
@retry(stop=stop_after_attempt(3), wait=wait_exponential(...))
async def generate_chat_response(question: str) -> str:
    response = await client.chat.completions.create(...)
    return response.choices[0].message.content
```

---

## 데이터베이스 스키마

### MongoDB Collections

**logs** - 요청 로그
```javascript
{
  _id: ObjectId,
  route: String,
  req: Object,
  res_head: Object,
  duration_ms: Number,
  created_at: ISODate
}
```

**bookmarks** - 사용자 북마크
```javascript
{
  _id: ObjectId,
  title: String,
  url: String,
  tags: [String],
  note: String,
  created_at: ISODate
}
```

**qa_sessions** - Q&A 세션
```javascript
{
  _id: ObjectId,
  history: [
    {
      question: String,
      answer: String,
      created_at: ISODate
    }
  ],
  created_at: ISODate
}
```

**cache** - 응답 캐시
```javascript
{
  _id: ObjectId,
  key: String,
  value: Mixed,
  ttl: Number,
  created_at: ISODate
}
```

---

## 외부 API 통합

### OpenAI API

**사용 모델:**
- 기본: `gpt-4-turbo-preview`
- 대체: `gpt-3.5-turbo`

**사용 엔드포인트:**
- `/v1/chat/completions` (채팅, 요약)
- JSON mode 지원 (문제 생성, 추천)

**Rate Limiting:**
- 앱 레벨: 30 req/min
- OpenAI: 모델별 상이

### 시장 데이터 (Mock)

현재는 Mock 데이터를 사용하며, 다음 API로 교체 가능:

| 데이터 | 추천 API |
|-------|----------|
| 국내 경제지표 | ECOS (한국은행) |
| 미국 경제지표 | FRED (St. Louis Fed) |
| 주가 데이터 | KRX, Yahoo Finance |
| 환율 | 서울외국환중개 |
| 뉴스 | 뉴스 API |

---

## 보안

### 입력 검증

**Pydantic**을 통한 타입 및 제약 검증:

```python
class QARequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    context: Optional[str] = Field(None, max_length=5000)
```

### 프롬프트 인젝션 방지

```python
def is_safe_prompt(text: str) -> bool:
    dangerous_patterns = [
        r"ignore\s+previous\s+instructions",
        r"system\s*:",
    ]
    # 패턴 검사
```

### CORS

환경 변수로 허용 origin 관리:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Rate Limiting

SlowAPI를 사용한 요청 제한:

```python
# 향후 추가 예정
@limiter.limit("30/minute")
async def qa_endpoint():
    ...
```

---

## 배포 아키텍처

### Docker Compose

```
┌───────────────────────┐
│   Nginx Container     │ :80
│   (Frontend Static)   │
└───────┬───────────────┘
        │
┌───────┴───────────────┐
│  FastAPI Container    │ :8000
│  (Backend API)        │
└───────┬───────────────┘
        │
┌───────┴───────────────┐
│  MongoDB Container    │ :27017
│  (Database)           │
└───────────────────────┘
```

**네트워크:** `econlux-network` (bridge)

**볼륨:** `mongodb_data` (데이터 영속성)

---

## 성능 최적화

### 프론트엔드
- Code splitting (React.lazy)
- Vite 빌드 최적화
- 이미지 lazy loading
- React Query 캐싱

### 백엔드
- 비동기 처리 (async/await)
- Connection pooling
- Response 압축
- 적절한 인덱싱

---

## 모니터링 & 로깅

### 현재 구현
- 기본 콘솔 로깅
- MongoDB 요청 로그

### 향후 추가 권장
- Sentry (에러 추적)
- Prometheus + Grafana (메트릭)
- ELK Stack (로그 분석)
- OpenAI usage tracking

---

## 확장성

### 수평 확장
- 백엔드: 여러 인스턴스 + 로드 밸런서
- MongoDB: Replica Set 또는 Sharding

### 수직 확장
- 메모리 증가
- CPU 코어 추가

### 캐싱 레이어
- Redis (응답 캐싱)
- CDN (정적 파일)

---

## 기술적 결정 사항

### 왜 FastAPI?
- 빠른 성능 (Starlette + Pydantic)
- 자동 API 문서
- 비동기 지원
- 타입 힌트

### 왜 React Query?
- 서버 상태 관리에 특화
- 캐싱 및 동기화
- 보일러플레이트 감소

### 왜 MongoDB?
- 스키마 유연성
- 비동기 드라이버 (Motor)
- JSON 친화적
- 빠른 프로토타이핑

---

## 트레이드오프

| 결정 | 장점 | 단점 |
|-----|------|------|
| Tailwind CSS | 빠른 개발, 일관성 | 클래스명 길어짐 |
| Mock 데이터 | 외부 의존성 없음 | 실제 데이터 아님 |
| OpenAI API | 강력한 AI | 비용, 레이턴시 |
| MongoDB | 유연함 | ACID 제약 |

---

더 자세한 내용은 각 디렉토리의 README를 참고하세요.

