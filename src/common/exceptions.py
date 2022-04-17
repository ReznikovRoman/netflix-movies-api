class NetflixError(Exception):
    """Ошибка Netflix API."""

    message: str
    code: str

    def __init__(self, message: str | None = None):
        if message is not None:
            self.message = message

    def __str__(self) -> str:
        return self.message


class NotFoundError(NetflixError):
    """Ресурс не найден."""

    message = "Resource not found"
    code = "not_found"


class ImproperlyConfiguredError(NetflixError):
    """Неверная конфигурация."""

    message = "Improperly configured service"
    code = "improperly_configured"
