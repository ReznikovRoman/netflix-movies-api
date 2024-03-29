from functools import lru_cache
from typing import Union

from pydantic import AnyHttpUrl, Field, validator
from pydantic.env_settings import BaseSettings


class EnvConfig(BaseSettings.Config):

    @classmethod
    def prepare_field(cls, field) -> None:
        if "env_names" in field.field_info.extra:
            return
        return super().prepare_field(field)


class Settings(BaseSettings):
    """Project settings."""

    # Project
    API_V1_STR: str = "/api/v1"
    SERVER_NAME: str
    SERVER_HOSTS: Union[str, list[AnyHttpUrl]]
    PROJECT_NAME: str
    DEBUG: bool = False
    PROJECT_BASE_URL: str
    CACHE_DEFAULT_TTL: int = 5 * 60  # 5 minutes
    CACHE_HASHED_KEY_LENGTH: int = 10

    # Redis
    REDIS_SENTINELS: Union[str, list[str]]
    REDIS_SENTINEL_SOCKET_TIMEOUT: float = 0.5
    REDIS_MASTER_SET: str
    REDIS_PASSWORD: str
    REDIS_DECODE_RESPONSES: bool = True
    REDIS_RETRY_ON_TIMEOUT: bool = True

    # Elastic
    ES_HOST: str = Field(env="NE_ES_HOST")
    ES_PORT: int = Field(env="NE_ES_PORT")
    ES_RETRY_ON_TIMEOUT: bool = True

    # Netflix Auth
    AUTH_SERVICE_URL: str
    AUTH0_DOMAIN: str = Field(env="NAA_AUTH0_DOMAIN")
    AUTH0_API_AUDIENCE: str = Field(env="NAA_AUTH0_API_AUDIENCE")
    AUTH0_ISSUER: str = Field(env="NAA_AUTH0_ISSUER")
    AUTH0_CLIENT_ID: str = Field(env="NAA_AUTH0_CLIENT_ID")
    AUTH0_CLIENT_SECRET: str = Field(env="NAA_AUTH0_CLIENT_SECRET")
    AUTH0_AUTHORIZATION_URL: str = Field(env="NAA_AUTH0_AUTHORIZATION_URL")
    JWT_AUTH_SECRET_KEY: str = Field(env="NAA_SECRET_KEY")
    JWT_AUTH_ALGORITHM: str = "HS256"

    class Config(EnvConfig):
        env_prefix = "NMA_"
        case_sensitive = True

    @validator("SERVER_HOSTS", pre=True)
    def _assemble_server_hosts(cls, server_hosts):
        if isinstance(server_hosts, str):
            return [item.strip() for item in server_hosts.split(",")]
        return server_hosts

    @validator("REDIS_SENTINELS", pre=True)
    def _assemble_redis_sentinels(cls, redis_sentinels):
        if isinstance(redis_sentinels, str):
            return [item.strip() for item in redis_sentinels.split(",")]
        return redis_sentinels


@lru_cache()
def get_settings() -> "Settings":
    return Settings()
