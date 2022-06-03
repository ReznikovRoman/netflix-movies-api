from enum import Enum
from typing import Final


# Размер страницы по умолчанию
DEFAULT_PAGE_SIZE: Final[int] = 50


class DefaultRoles(str, Enum):
    """Роли в сервисе по умолчанию."""

    VIEWERS = "viewers"
    SUBSCRIBERS = "subscribers"
