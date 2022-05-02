from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError as ElasticNotFoundError

from common.exceptions import NotFoundError
from db import elastic


if TYPE_CHECKING:
    from common.types import Id, Query


class ElasticClient:
    """Клиент для работы с Elasticsearch."""

    REQUEST_TIMEOUT: ClassVar[int] = 5

    async def _get_client(self) -> AsyncElasticsearch:
        return elastic.es

    async def get_client(self) -> AsyncElasticsearch:
        client = await self._get_client()
        # TODO: отрефакторить:
        #  1. Добавить методы pre_init_client, post_init_client
        #  2. Добавить backoff на ConnectionTimeout, ConnectionError
        return client

    async def get_by_id(self, document_id: Id, index: str) -> dict:
        client = await self.get_client()
        try:
            doc = await client.get(index=index, id=str(document_id), request_timeout=ElasticClient.REQUEST_TIMEOUT)
        except ElasticNotFoundError:
            raise NotFoundError()
        return doc["_source"]

    async def search(self, query: Query, index: str, **options) -> list[dict]:
        client = await self.get_client()
        timeout = options.pop("request_timeout", ElasticClient.REQUEST_TIMEOUT)
        docs = await client.search(index=index, body=query, request_timeout=timeout, **options)
        return self._prepare_documents_list(docs)

    @staticmethod
    def _prepare_documents_list(docs: dict) -> list[dict]:
        results = [
            doc["_source"]
            for doc in docs["hits"]["hits"]
        ]
        return results
