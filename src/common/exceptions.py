from http import HTTPStatus


class NetflixError(Exception):
    """Ошибка Netflix API."""

    message: str
    code: str
    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(self, message: str | None = None, code: str | None = None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __str__(self) -> str:
        return self.message

    def to_dict(self) -> dict:
        dct = {
            "error": {
                "code": self.code,
                "message": self.message,
            },
        }
        return dct


class NotFoundError(NetflixError):
    """Ресурс не найден."""

    message = "Resource not found"
    code = "not_found"
    status_code = HTTPStatus.NOT_FOUND


class ImproperlyConfiguredError(NetflixError):
    """Неверная конфигурация."""

    message = "Improperly configured service"
    code = "improperly_configured"
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR


class AuthorizationError(NetflixError):
    """Ошибка при авторизации."""

    message = "Authorization error"
    code = "authorization_error"
    status_code = HTTPStatus.UNAUTHORIZED
