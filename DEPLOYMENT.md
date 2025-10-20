# 배포 가이드

## 로컬 개발 환경

### 필수 요구사항
- Node.js 18+
- Python 3.11+
- MongoDB 6+
- OpenAI API Key

### 설치 및 실행

1. **환경 변수 설정**
```bash
# 루트에 .env 파일 생성
cp .env.example .env

# OpenAI API Key 입력
OPENAI_API_KEY=sk-your-key-here
```

2. **백엔드 실행**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

3. **프론트엔드 실행**
```bash
cd frontend
npm install -g pnpm
pnpm install
pnpm dev
```

4. **MongoDB 실행** (로컬)
```bash
# Docker 사용
docker run -d -p 27017:27017 --name econlux-mongo mongo:6

# 또는 로컬 MongoDB 서비스 시작
mongod
```

5. **접속**
- 프론트엔드: http://localhost:5173
- 백엔드 API: http://localhost:8000
- API 문서: http://localhost:8000/docs

---

## Docker Compose 배포

가장 간단한 배포 방법입니다.

### 실행 방법

1. **환경 변수 설정**
```bash
# docker-compose.yml과 같은 위치에 .env 파일 생성
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

2. **빌드 및 실행**
```bash
# 빌드
docker-compose build

# 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

3. **종료**
```bash
docker-compose down

# 볼륨까지 삭제 (데이터 초기화)
docker-compose down -v
```

4. **접속**
- 프론트엔드: http://localhost
- 백엔드 API: http://localhost:8000
- API 문서: http://localhost:8000/docs

---

## 프로덕션 배포

### AWS EC2 배포 예시

1. **EC2 인스턴스 설정**
```bash
# Ubuntu 22.04 기준
sudo apt update
sudo apt install -y docker.io docker-compose git

# Docker 권한 설정
sudo usermod -aG docker $USER
```

2. **프로젝트 클론**
```bash
git clone <repository-url>
cd fast_01
```

3. **환경 변수 설정**
```bash
# .env 파일 생성
cat > .env << EOF
OPENAI_API_KEY=sk-your-key-here
EOF

# docker-compose.yml 수정 (CORS_ORIGINS를 실제 도메인으로)
```

4. **실행**
```bash
docker-compose up -d
```

5. **Nginx 리버스 프록시 설정** (선택사항)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 환경 변수 설명

### Backend (.env)
```env
MONGO_URI=mongodb://localhost:27017  # MongoDB 연결 URI
MONGO_DB=econlux                     # 데이터베이스 이름
OPENAI_API_KEY=sk-xxx                # OpenAI API 키 (필수)
OPENAI_MODEL=gpt-4-turbo-preview     # 사용할 모델
CORS_ORIGINS=http://localhost:5173   # CORS 허용 출처
```

### Frontend (.env)
```env
VITE_API_BASE=http://localhost:8000/api  # API 베이스 URL
VITE_APP_NAME=Noir Luxe Economy          # 앱 이름
```

---

## 헬스 체크

서비스가 정상 작동하는지 확인:

```bash
# 백엔드
curl http://localhost:8000/api/health

# 프론트엔드
curl http://localhost/

# MongoDB
docker exec econlux-mongodb mongosh --eval "db.adminCommand('ping')"
```

---

## 트러블슈팅

### 1. 백엔드가 시작되지 않음
```bash
# 로그 확인
docker-compose logs backend

# MongoDB 연결 확인
docker exec econlux-mongodb mongosh --eval "db.stats()"
```

### 2. OpenAI API 오류
- API 키가 유효한지 확인
- API 사용량 한도 확인
- 환경 변수가 올바르게 설정되었는지 확인

### 3. CORS 오류
- `docker-compose.yml`의 `CORS_ORIGINS` 설정 확인
- 프론트엔드 URL이 정확히 포함되어 있는지 확인

### 4. 프론트엔드 빌드 실패
```bash
# 의존성 재설치
cd frontend
rm -rf node_modules pnpm-lock.yaml
pnpm install
pnpm build
```

---

## 모니터링

### 로그 수집
```bash
# 전체 로그
docker-compose logs -f

# 특정 서비스
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 리소스 사용량
```bash
docker stats
```

---

## 백업 및 복원

### MongoDB 백업
```bash
docker exec econlux-mongodb mongodump --db econlux --out /backup
docker cp econlux-mongodb:/backup ./backup
```

### MongoDB 복원
```bash
docker cp ./backup econlux-mongodb:/backup
docker exec econlux-mongodb mongorestore --db econlux /backup/econlux
```

---

## 성능 최적화

### 프론트엔드
- Vite 빌드 최적화 (이미 적용됨)
- Nginx gzip 압축 (이미 적용됨)
- 이미지 최적화
- 코드 스플리팅

### 백엔드
- MongoDB 인덱스 추가
- 응답 캐싱
- Rate limiting (이미 적용됨)
- Connection pooling

---

## 보안 체크리스트

- [ ] OpenAI API 키를 환경 변수로 관리
- [ ] CORS 설정 확인
- [ ] MongoDB 인증 설정 (프로덕션)
- [ ] HTTPS 적용 (프로덕션)
- [ ] Rate limiting 설정
- [ ] 입력 검증 (이미 적용됨)
- [ ] 에러 메시지에 민감 정보 노출 방지

---

## 업데이트

```bash
# 코드 업데이트
git pull

# 재빌드 및 재시작
docker-compose down
docker-compose build
docker-compose up -d
```

