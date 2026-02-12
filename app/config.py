from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./shortener.db"
    BASE_URL: str = "http://localhost:8000"
    SHORT_CODE_LENGTH: int = 6

    class Config:
        env_file = ".env"


settings = Settings()
