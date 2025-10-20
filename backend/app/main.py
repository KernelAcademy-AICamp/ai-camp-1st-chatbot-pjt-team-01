import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(
    title="Econ Assist Bot API",
    description="""
    경제학 문제 생성 및 채점 시스템 API
    
    ## 주요 기능
    - **문제 생성**: AI를 활용한 경제학 문제 자동 생성
    - **문제 풀이**: 객관식 문제 풀이 및 실시간 채점
    - **채점 결과 저장**: 퀴즈 시도 결과 저장 및 조회
    - **맞춤형 재시도**: 틀린 문제 기반 AI 맞춤형 문제 생성
    - **시장 데이터**: 실시간 경제 지표 및 뉴스 제공
    - **Q&A**: 경제 관련 질문 답변
    
    ## API 엔드포인트
    - `/api/problems`: 문제 생성 및 조회
    - `/api/problems/grade`: 답안 채점
    - `/api/quiz/attempts`: 퀴즈 시도 관리
    - `/api/quiz/retry`: 틀린 문제 기반 맞춤형 문제 생성
    - `/api/market`: 시장 데이터 조회
    - `/api/qa`: 질문 답변
    - `/api/demo/*`: DEMO 모드 전용 관리 기능 (DEMO=true일 때만 활성화)
    
    ## DEMO 모드
    DEMO 모드에서는 실제 OpenAI API 호출 대신 미리 준비된 샘플 데이터를 사용합니다.
    데모용 관리 기능을 통해 데이터베이스를 초기화하고 샘플 데이터를 삽입할 수 있습니다.
    """,
    version="1.0.0",
    contact={
        "name": "Econ Assist Team",
        "email": "support@econassist.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",  # Vite dev server 포트
    "http://localhost:5177",  # 추가된 포트
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5175",
    "http://127.0.0.1:5177",  # 추가된 포트
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
from app.routers import health, qa, problems, recommend, market, quiz, demo
app.include_router(health.router, prefix="/api")
app.include_router(qa.router, prefix="/api")
app.include_router(problems.router, prefix="/api")
app.include_router(recommend.router, prefix="/api")
app.include_router(market.router, prefix="/api")
app.include_router(quiz.router, prefix="/api")
app.include_router(demo.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Econ Assist API running"}
