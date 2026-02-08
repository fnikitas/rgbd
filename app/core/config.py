from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Конфигурация приложения из переменных окружения."""

    DATABASE_URL: str = "postgresql+asyncpg://taskuser:taskpass@localhost:5432/taskdb"
    DATABASE_ECHO: bool = False

    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    PROJECT_NAME: str = "Task Tracker"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
