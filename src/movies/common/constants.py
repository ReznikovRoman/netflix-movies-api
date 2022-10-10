from enum import Enum
from typing import Final

# Default page size for pagination
DEFAULT_PAGE_SIZE: Final[int] = 50


class DefaultRoles(str, Enum):
    """Default roles."""

    VIEWERS = "viewers"
    SUBSCRIBERS = "subscribers"
