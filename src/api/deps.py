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

    def __init__(
        self,
        sort: str | None = Query(default=None, description="Сортировка по полю."),
    ):
        if sort and sort[0] == "-":
            sort = sort[1:] + ":desc"
        self.sort = sort
