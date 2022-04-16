from uuid import UUID

from pydantic import BaseModel

import orjson


def orjson_dumps(value, *, default):
    return orjson.dumps(value, default=default).decode()


class BaseOrjsonSchema(BaseModel):
    """Базовая схема ответа с orjson."""

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class BaseIdOrjsonSchema(BaseOrjsonSchema):
    """Базовая схема с uuid."""

    uuid: UUID
