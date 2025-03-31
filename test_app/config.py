import os
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    SECRET_KEY: str = "C6eNrLuaBpQ7u0okx-GuKlmM3nLJqOdvxIbaLOVdpb8"
    ALGORITHM: str = "HS256" 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:yogesh@localhost:5432/mydatabase")
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
settings = Settings()