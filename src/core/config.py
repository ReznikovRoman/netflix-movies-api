from functools import lru_cache

from pydantic import AnyHttpUrl, BaseSettings


class Settings(BaseSettings):
    """Настройки проекта."""

    # Project
    API_V1_STR: str = "/api/v1"
    SERVER_NAME: str
    SERVER_HOST: AnyHttpUrl
    PROJECT_NAME: str
    DEBUG: bool = False
    PROJECT_BASE_URL: str

    class Config:
        case_sensitive = True


@lru_cache()
def get_settings() -> "Settings":
    return Settings()
