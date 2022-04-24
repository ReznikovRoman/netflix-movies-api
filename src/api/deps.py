from typing import ClassVar

from fastapi import Query

from common.constants import DEFAULT_PAGE_SIZE


class PageNumberPaginationQueryParams:
    """Стандартные query параметры для запроса с пагинацией."""

    def __init__(
        self,
        page_number: int | None = Query(default=0, alias="page[number]", description="Номер страницы."),
        page_size: int | None = Query(default=DEFAULT_PAGE_SIZE, alias="page[size]", description="Размер страницы."),
    ):
        self.page_number = page_number
        self.page_size = page_size


class SortQueryParams:
    """Стандартные query параметры для запроса с сортировкой."""

    API_DESCENDING_CHAR: ClassVar[str] = "-"
    ELASTIC_DESCENDING_CHAR: ClassVar[str] = ":desc"

    def __init__(
        self,
        sort: list[str] | None = Query(default=None, description="Сортировка по полю."),
    ):
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
