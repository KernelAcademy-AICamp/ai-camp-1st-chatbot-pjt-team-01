# 기여 가이드

Noir Luxe Economy 프로젝트에 기여해주셔서 감사합니다!

## 개발 환경 설정

1. **저장소 클론**
```bash
git clone <repository-url>
cd fast_01
```

2. **의존성 설치**
```bash
# 백엔드
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 프론트엔드
cd frontend
pnpm install
```

3. **환경 변수 설정**
```bash
cp .env.example .env
# OpenAI API 키 등을 설정
```

4. **개발 서버 실행**
```bash
# 터미널 1: 백엔드
cd backend
uvicorn app.main:app --reload

# 터미널 2: 프론트엔드
cd frontend
pnpm dev
```

---

## 코드 스타일

### Python (Backend)
- PEP 8 스타일 가이드 준수
- Type hints 사용
- Docstring 작성 (함수, 클래스)
- Black 포매터 사용 권장

```python
def example_function(param: str) -> dict:
    """
    함수 설명
    
    Args:
        param: 파라미터 설명
        
    Returns:
        결과 설명
    """
    return {"result": param}
```

### TypeScript (Frontend)
- ESLint 규칙 준수
- 함수형 컴포넌트 사용
- Props에 타입 지정
- 의미 있는 변수명 사용

```tsx
interface ButtonProps {
  text: string
  onClick: () => void
}

export default function Button({ text, onClick }: ButtonProps) {
  return <button onClick={onClick}>{text}</button>
}
```

---

## 커밋 메시지

커밋 메시지는 다음 형식을 따릅니다:

```
<type>: <subject>

<body>
```

### Type
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `docs`: 문서 수정
- `style`: 코드 포맷팅
- `refactor`: 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 빌드, 설정 변경

### 예시
```
feat: Add KPI card hover animation

- KpiCard 컴포넌트에 hover 시 scale 애니메이션 추가
- framer-motion 활용
```

---

## 브랜치 전략

- `main`: 프로덕션 배포 브랜치
- `develop`: 개발 브랜치
- `feature/*`: 기능 개발
- `fix/*`: 버그 수정
- `docs/*`: 문서 작업

### 워크플로우
1. `develop`에서 새 브랜치 생성
```bash
git checkout develop
git pull
git checkout -b feature/new-feature
```

2. 작업 후 커밋
```bash
git add .
git commit -m "feat: Add new feature"
```

3. Push 및 PR 생성
```bash
git push origin feature/new-feature
```

4. PR 리뷰 후 `develop`에 머지

---

## 테스트

### Backend
```bash
cd backend
pytest
```

### Frontend
```bash
cd frontend
pnpm test
```

**모든 PR은 테스트를 통과해야 합니다.**

---

## Pull Request 체크리스트

- [ ] 코드가 스타일 가이드를 따름
- [ ] 테스트가 통과함
- [ ] 새로운 기능은 테스트 추가
- [ ] 문서 업데이트 (필요 시)
- [ ] 커밋 메시지가 컨벤션을 따름
- [ ] 변경 사항이 README에 반영됨 (필요 시)

---

## 버그 리포트

버그를 발견했다면 다음 정보를 포함하여 이슈를 등록해주세요:

1. **환경**
   - OS
   - Node.js 버전
   - Python 버전
   - 브라우저 (프론트엔드 버그)

2. **재현 방법**
   - 단계별 재현 과정

3. **예상 동작**

4. **실제 동작**

5. **스크린샷** (해당되는 경우)

---

## 기능 제안

새로운 기능을 제안하고 싶다면:

1. 기존 이슈 검색 (중복 방지)
2. 이슈 등록
   - 기능 설명
   - 사용 사례
   - 예상 구현 방법

---

## 리뷰 프로세스

1. PR 생성 후 자동 CI 테스트 실행
2. 코드 리뷰어 지정
3. 리뷰어의 승인 후 머지

---

## 질문이 있나요?

- 이슈 등록
- 디스커션 참여
- 메인테이너에게 연락

---

감사합니다! 🎉

