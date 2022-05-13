from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from elasticsearch.exceptions import NotFoundError as ElasticNotFoundError

from common.exceptions import NotFoundError
from db import elastic


if TYPE_CHECKING:
    from elasticsearch import AsyncElasticsearch

    from common.types import Id, Query


class ElasticClient:
    """Клиент для работы с Elasticsearch."""

    REQUEST_TIMEOUT: ClassVar[int] = 5

    async def _get_client(self) -> AsyncElasticsearch:
        return elastic.es

    async def get_client(self) -> AsyncElasticsearch:
        await self.pre_init_client()
        client = await self._get_client()
        await self.post_init_client(client)
        return client

    async def get_by_id(self, index: str, document_id: Id) -> dict:
        client = await self.get_client()
        try:
            doc = await client.get(index=index, id=str(document_id), request_timeout=ElasticClient.REQUEST_TIMEOUT)
        except ElasticNotFoundError:
            raise NotFoundError()
        return doc["_source"]

    async def search(self, index: str, query: Query, **options) -> list[dict]:
        client = await self.get_client()
        timeout = options.pop("request_timeout", ElasticClient.REQUEST_TIMEOUT)
        docs = await client.search(index=index, body=query, request_timeout=timeout, **options)
        return self._prepare_documents_list(docs)

    async def pre_init_client(self, *args, **kwargs) -> None:
        """Вызывается до начала инициализации клиента Elasticsearch."""

    async def post_init_client(self, client: AsyncElasticsearch, *args, **kwargs) -> None:
        """Вызывается после инициализации клиента Elasticsearch."""

    @staticmethod
    def _prepare_documents_list(docs: dict) -> list[dict]:
        results = [
            doc["_source"]
            for doc in docs["hits"]["hits"]
        ]
        return results
