from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # MongoDB
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "econlux"
    
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_MAX_TOKENS: int = 2000
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"
    
    # API
    API_PREFIX: str = "/api"
    APP_NAME: str = "Noir Luxe Economy"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 30
    
    # Demo Mode
    DEMO: bool = True  # 기본값을 True로 설정
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # BOM 및 추가 필드 무시
    
    @property
    def cors_origins_list(self) -> List[str]:
        """CORS origins를 리스트로 반환"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()

