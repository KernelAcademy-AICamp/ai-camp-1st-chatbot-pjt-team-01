# API 문서

Noir Luxe Economy 백엔드 API 문서입니다.

**Base URL**: `http://localhost:8000/api`

**Interactive Docs**: `http://localhost:8000/docs` (Swagger UI)

---

## 헬스 체크

### GET /health

서비스 상태를 확인합니다.

**Response**
```json
{
  "status": "ok",
  "app_name": "Noir Luxe Economy",
  "timestamp": "2024-01-20T10:30:00Z"
}
```

---

## 시장 데이터

### GET /market/kpis

주요 경제 지표를 조회합니다.

**Response**
```json
{
  "cpi": 110.5,
  "cpi_change": 2.3,
  "gdp_qoq": 0.6,
  "gdp_yoy": 2.2,
  "unemployment": 3.4,
  "unemployment_change": -0.1,
  "base_rate": 3.50,
  "base_rate_change": 0.0,
  "usdkrw": 1335.50,
  "usdkrw_change": 5.20,
  "spx": 4783.45,
  "spx_change": 0.85,
  "kospi": 2655.20,
  "kospi_change": 1.12,
  "updated_at": "2024-01-20T10:30:00Z"
}
```

### GET /market/trends

경제 지표 시계열 데이터를 조회합니다.

**Response**
```json
{
  "cpi_series": [
    { "date": "2021-01", "value": 100.5 },
    { "date": "2021-02", "value": 101.2 }
  ],
  "unemployment_series": [...],
  "rate_series": [...],
  "gdp_series": [...]
}
```

### GET /market/news

경제 뉴스를 조회합니다.

**Response**
```json
{
  "items": [
    {
      "title": "한국은행, 기준금리 3.50% 동결",
      "summary": "한국은행 금융통화위원회가...",
      "url": "https://example.com/news/1",
      "source": "한국은행",
      "published_at": "2024-01-15"
    }
  ]
}
```

---

## Q&A

### POST /qa/summary

경제 주제 요약을 생성합니다.

**Request**
```json
{
  "question": "이번 달 CPI 핵심 요약",
  "context": "선택적 추가 컨텍스트"
}
```

**Response**
```json
{
  "answer_md": "## CPI 요약\n\n- 전월 대비 0.3% 상승\n- ...",
  "citations": ["한국은행", "통계청"],
  "created_at": "2024-01-20T10:30:00Z"
}
```

**Error Responses**
- `400`: 입력 검증 실패 또는 안전하지 않은 프롬프트
- `500`: AI 응답 생성 실패

### POST /qa/chat

Q&A 채팅 응답을 생성합니다.

**Request**
```json
{
  "question": "기준금리 인상이 경제에 미치는 영향은?",
  "context": null
}
```

**Response**
```json
{
  "answer_md": "기준금리 인상은 다음과 같은 영향을...",
  "citations": [],
  "created_at": "2024-01-20T10:30:00Z"
}
```

---

## 문제 생성

### POST /problems

경제 문제를 생성합니다.

**Request**
```json
{
  "level": "basic",
  "topic": "macro",
  "count": 5,
  "style": "mcq"
}
```

**Parameters**
- `level`: "basic" | "intermediate" | "advanced"
- `topic`: "macro" | "finance" | "trade" | "stats"
- `count`: 1-20
- `style`: "mcq" | "free"

**Response**
```json
{
  "items": [
    {
      "question": "GDP는 무엇을 의미하나요?",
      "options": ["1번", "2번", "3번", "4번"],
      "answer": "국내총생산",
      "explain": "GDP(Gross Domestic Product)는..."
    }
  ],
  "level": "basic",
  "topic": "macro"
}
```

---

## 자료 추천

### POST /recommend

경제 학습 자료를 추천합니다.

**Request**
```json
{
  "topic": "인플레이션",
  "level": "intermediate",
  "purpose": "study"
}
```

**Parameters**
- `level`: "beginner" | "intermediate" | "advanced"
- `purpose`: "report" | "study" | "data" | "api"

**Response**
```json
{
  "items": [
    {
      "title": "한국은행 경제통계시스템",
      "summary": "국내 주요 경제지표와 통계 데이터를 제공...",
      "url": "https://ecos.bok.or.kr",
      "tags": ["무료", "공식", "데이터", "API"]
    }
  ]
}
```

### POST /recommend/bookmark

자료를 북마크에 추가합니다.

**Request**
```json
{
  "title": "한국은행 경제통계시스템",
  "url": "https://ecos.bok.or.kr",
  "tags": ["무료", "공식"],
  "note": "자주 사용하는 데이터 소스"
}
```

**Response**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "message": "북마크가 저장되었습니다."
}
```

### GET /recommend/bookmarks

저장된 북마크 목록을 조회합니다.

**Response**
```json
{
  "bookmarks": [
    {
      "id": "507f1f77bcf86cd799439011",
      "title": "한국은행 경제통계시스템",
      "url": "https://ecos.bok.or.kr",
      "tags": ["무료", "공식"],
      "note": "자주 사용하는 데이터 소스",
      "created_at": "2024-01-20T10:30:00Z"
    }
  ]
}
```

---

## 에러 코드

| 코드 | 설명 |
|------|------|
| 400 | 잘못된 요청 (입력 검증 실패) |
| 404 | 리소스를 찾을 수 없음 |
| 429 | Rate limit 초과 |
| 500 | 서버 내부 오류 |

**Error Response 형식**
```json
{
  "detail": "오류 메시지"
}
```

---

## Rate Limiting

- `/api/qa/*` 엔드포인트: 30 요청/분
- 기타 엔드포인트: 제한 없음

Rate limit 초과 시 `429 Too Many Requests` 응답이 반환됩니다.

---

## 인증

현재 버전에서는 인증이 필요하지 않습니다.
프로덕션 환경에서는 API 키 또는 JWT 인증을 추가하는 것을 권장합니다.

---

## CORS

다음 origin에서의 요청이 허용됩니다:
- `http://localhost:5173` (개발 환경)
- 환경 변수 `CORS_ORIGINS`에 설정된 origin

---

## OpenAI 사용량

이 API는 OpenAI API를 사용합니다. 다음 엔드포인트가 OpenAI를 호출합니다:
- `/api/qa/summary`
- `/api/qa/chat`
- `/api/problems`
- `/api/recommend`

OpenAI API 사용량과 비용을 모니터링하세요.

---

## 추가 리소스

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **GitHub**: [프로젝트 저장소]

