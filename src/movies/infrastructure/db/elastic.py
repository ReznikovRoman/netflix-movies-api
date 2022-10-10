from __future__ import annotations

from typing import AsyncIterator, ClassVar

from elasticsearch import AsyncElasticsearch
from elasticsearch import NotFoundError as ElasticNotFoundError

from movies.common.exceptions import NotFoundError
from movies.common.types import Id, Query


async def init_elastic(host: str, port: int, retry_on_timeout: bool = True) -> AsyncIterator[AsyncElasticsearch]:
    """Init Elasticsearch client."""
    elastic_client = AsyncElasticsearch(
        hosts=[
            {"host": host, "port": port},
        ],
        max_retries=30,
        retry_on_timeout=retry_on_timeout,
        request_timeout=30,
    )
    yield elastic_client
    await elastic_client.close()


class ElasticClient:
    """Elasticsearch client."""

    REQUEST_TIMEOUT: ClassVar[int] = 5  # 5 seconds

    def __init__(self, elastic_client: AsyncElasticsearch) -> None:
        self.elastic_client = elastic_client

    def get_client(self, *, index: str) -> AsyncElasticsearch:
        return self._get_client(index=index)

    async def get_by_id(self, document_id: Id, /, *, index: str) -> dict:
        client = self.get_client(index=index)
        try:
            doc = await client.get(index=index, id=str(document_id), request_timeout=ElasticClient.REQUEST_TIMEOUT)
        except ElasticNotFoundError:
            raise NotFoundError
        return doc["_source"]

    async def search(self, index: str, query: Query, **options) -> list[dict]:
        client = self.get_client(index=index)
        timeout = options.pop("request_timeout", ElasticClient.REQUEST_TIMEOUT)
        docs = await client.search(index=index, body=query, request_timeout=timeout, **options)
        return self._prepare_documents_list(docs)

    def _get_client(self, *, index: str) -> AsyncElasticsearch:
        return self.elastic_client

    @staticmethod
    def _prepare_documents_list(docs: dict, /) -> list[dict]:
        results = [
            doc["_source"]
            for doc in docs["hits"]["hits"]
        ]
        return results
