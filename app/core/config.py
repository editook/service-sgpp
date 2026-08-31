import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SGPP API"
    VERSION: str = "3.0.0"
    API_V1_STR: str = "/api/v1"
    
    # DATABASE_URL prioriza la variable de entorno para producción
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    # JWT Authentication
    SECRET_KEY: str = "0bb2681a7697468ba0d65c6e98c181a7secretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8 # 8 hours

    class Config:
        case_sensitive = True
        env_file = ".env"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        url = self.DATABASE_URL

        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://")

        return url

settings = Settings()
