import asyncio

import backoff
import elasticsearch

from src.movies.core.config import get_settings

settings = get_settings()


@backoff.on_exception(
    wait_gen=backoff.expo,
    exception=elasticsearch.exceptions.ElasticsearchException,
    max_tries=5,
    max_time=2 * 60,
)
async def wait_for_elasticsearch() -> None:
    """Ожидает полноценного подключения к Elasticsearch."""
    client = elasticsearch.AsyncElasticsearch(
        hosts=[
            {"host": settings.ES_HOST, "port": settings.ES_PORT},
        ],
        max_retries=30,
        retry_on_timeout=settings.ES_RETRY_ON_TIMEOUT,
        request_timeout=30,
    )
    await client.ping()


if __name__ == "__main__":
    loop = asyncio.get_event_loop_policy().new_event_loop()
    loop.run_until_complete(wait_for_elasticsearch())
    loop.close()
