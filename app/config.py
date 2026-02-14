from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./gosha.db"

    # JWT
    SECRET_KEY: str = "your-super-secret-key-change-in-production-please"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # App
    BASE_URL: str = "http://localhost:8000"
    SHORT_CODE_LENGTH: int = 6

    # Admin (создаётся при первом запуске)
    ADMIN_EMAIL: str = "admin@gosha.link"
    ADMIN_PASSWORD: str = "Admin123!"
    ADMIN_USERNAME: str = "admin"

    class Config:
        env_file = ".env"


settings = Settings()
