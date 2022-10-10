from typing import ClassVar

from jose import JWTError, jwt

from fastapi import Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from movies.common.constants import DEFAULT_PAGE_SIZE
from movies.common.exceptions import AuthorizationError
from movies.core.config import get_settings

settings = get_settings()

jwt_scheme = HTTPBearer(auto_error=False)


class PageNumberPaginationQueryParams:
    """Pagination query parameters."""

    def __init__(
        self,
        page_number: int | None = Query(default=0, alias="page[number]", description="Page number."),
        page_size: int | None = Query(default=DEFAULT_PAGE_SIZE, alias="page[size]", description="Page size."),
    ) -> None:
        self.page_number = page_number
        self.page_size = page_size


class SortQueryParams:
    """Sort query parameters."""

    API_DESCENDING_CHAR: ClassVar[str] = "-"
    ELASTIC_DESCENDING_CHAR: ClassVar[str] = ":desc"

    def __init__(self, sort: list[str] | None = Query(default=None, description="Sorting field.")) -> None:
        self.sort = None

        if sort is not None:
            self.sort = self._format_sort_params(sort)

    @staticmethod
    def _format_sort_params(sort_params: list[str]) -> list[str]:
        formatted_params = map(SortQueryParams._format_sort_param, sort_params)
        return list(formatted_params)

    @staticmethod
    def _format_sort_param(sort_param: str) -> str:
        formatted_param = sort_param
        if sort_param.startswith(SortQueryParams.API_DESCENDING_CHAR):
            sort_param = sort_param.removeprefix(SortQueryParams.API_DESCENDING_CHAR)
            formatted_param = f"{sort_param}{SortQueryParams.ELASTIC_DESCENDING_CHAR}"
        return formatted_param


def get_user_roles(token: HTTPAuthorizationCredentials | None = Depends(jwt_scheme)) -> list[str]:
    """Get user roles from JWT claim."""
    if token is None:
        return []
    try:
        payload = jwt.decode(token.credentials, settings.JWT_AUTH_SECRET_KEY, algorithms=[settings.JWT_AUTH_ALGORITHM])
        roles: list[str] = payload.get("roles")
    except JWTError:
        raise AuthorizationError
    return roles
