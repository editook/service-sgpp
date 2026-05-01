import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SGPP API"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    
    # DATABASE (Modificado a SQLite para facilidad de demostración del usuario)
    SQLALCHEMY_DATABASE_URI: str = "sqlite:////data/sgpp_test.db" #"sqlite:///./sgpp_test.db"

    # JWT Authentication
    SECRET_KEY: str = "0bb2681a7697468ba0d65c6e98c181a7secretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8 # 8 hours

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
