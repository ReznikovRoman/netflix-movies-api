from uuid import UUID

import orjson
from pydantic import BaseModel


def orjson_dumps(value, *, default):
    return orjson.dumps(value, default=default).decode()


class BaseOrjsonSchema(BaseModel):
    """Base Pydantic orjson schema."""

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class BaseIdOrjsonSchema(BaseOrjsonSchema):
    """Base schema with uuid."""

    uuid: UUID
