from functools import lru_cache
from typing import Union

from pydantic import BaseSettings, Field, validator


class EnvConfig(BaseSettings.Config):

    @classmethod
    def prepare_field(cls, field) -> None:
        if "env_names" in field.field_info.extra:
            return
        return super().prepare_field(field)


class Test(BaseSettings):
    """Настройки для функциональных тестов."""

    # Tests
    CLIENT_BASE_URL: str = Field(env="TEST_CLIENT_BASE_URL")

    # Redis
    REDIS_SENTINELS: Union[str, list[str]]
    REDIS_MASTER_SET: str
    REDIS_PASSWORD: str | None = None
    REDIS_DECODE_RESPONSES: bool = True

    # Elastic
    ES_HOST: str = Field(env="NE_ES_HOST")
    ES_PORT: int = Field(env="NE_ES_PORT")

    class Config(EnvConfig):
        env_prefix = "NMA_"
        case_sensitive = True
        env_file = ".env"

    @validator("REDIS_SENTINELS", pre=True)
    def _assemble_redis_sentinels(cls, redis_sentinels):
        if isinstance(redis_sentinels, str):
            return [item.strip() for item in redis_sentinels.split(",")]
        return redis_sentinels


@lru_cache()
def get_settings() -> "Test":
    return Test()
