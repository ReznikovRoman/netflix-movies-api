from .base import BaseOrjsonSchema


class Message(BaseOrjsonSchema):
    """Сообщение."""

    message: str
