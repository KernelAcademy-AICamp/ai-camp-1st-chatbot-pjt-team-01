.PHONY: help install dev build up down logs clean test

help:
	@echo "Noir Luxe Economy - 개발 명령어"
	@echo ""
	@echo "  make install    - 의존성 설치"
	@echo "  make dev        - 개발 서버 실행 (로컬)"
	@echo "  make build      - Docker 이미지 빌드"
	@echo "  make up         - Docker Compose 실행"
	@echo "  make down       - Docker Compose 종료"
	@echo "  make logs       - Docker 로그 확인"
	@echo "  make test       - 테스트 실행"
	@echo "  make clean      - 빌드 파일 정리"

install:
	@echo "📦 의존성 설치 중..."
	cd backend && pip install -r requirements.txt
	cd frontend && pnpm install

dev-backend:
	@echo "🚀 백엔드 개발 서버 시작..."
	cd backend && uvicorn app.main:app --reload --port 8000

dev-frontend:
	@echo "🚀 프론트엔드 개발 서버 시작..."
	cd frontend && pnpm dev

build:
	@echo "🔨 Docker 이미지 빌드 중..."
	docker-compose build

up:
	@echo "🚀 Docker Compose 실행 중..."
	docker-compose up -d
	@echo "✅ 서비스 실행 완료!"
	@echo "   프론트엔드: http://localhost"
	@echo "   백엔드: http://localhost:8000"
	@echo "   API 문서: http://localhost:8000/docs"

down:
	@echo "🛑 Docker Compose 종료 중..."
	docker-compose down

logs:
	docker-compose logs -f

test:
	@echo "🧪 테스트 실행 중..."
	cd backend && pytest
	cd frontend && pnpm test

clean:
	@echo "🧹 빌드 파일 정리 중..."
	rm -rf backend/app/__pycache__
	rm -rf backend/.pytest_cache
	rm -rf frontend/dist
	rm -rf frontend/node_modules
	docker-compose down -v

