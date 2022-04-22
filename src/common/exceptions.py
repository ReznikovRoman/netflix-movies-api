class NetflixError(Exception):
    """Ошибка АПИ сервиса."""

    message: str
    code: str


class NotFoundError(NetflixError):
    """Ресурс не найден."""

    message = "Resource not found"
    code = "not_found"

    def __init__(self, message: str | None = None):
        if message is not None:
            self.message = message

    def __str__(self) -> str:
        return self.message
