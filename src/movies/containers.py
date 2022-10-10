from dependency_injector import containers, providers

from movies.core.logging import configure_logger
from movies.domain import films, genres, persons, users
from movies.infrastructure.db import cache, elastic, redis, repositories, storage


class Container(containers.DeclarativeContainer):
    """DI container."""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "movies.api.v1.handlers.genres",
            "movies.api.v1.handlers.films",
            "movies.api.v1.handlers.persons",
        ],
    )

    config = providers.Configuration()

    logging = providers.Resource(configure_logger)

    # Infrastructure

    elastic_connection = providers.Resource(
        elastic.init_elastic,
        host=config.ES_HOST,
        port=config.ES_PORT,
        retry_on_timeout=config.ES_RETRY_ON_TIMEOUT,
    )

    redis_sentinel_connection = providers.Resource(
        redis.init_redis_sentinel,
        sentinels=config.REDIS_SENTINELS,
        socket_timeout=config.REDIS_SENTINEL_SOCKET_TIMEOUT,
    )

    elastic_client = providers.Singleton(
        elastic.ElasticClient,
        elastic_client=elastic_connection,
    )

    redis_client = providers.Singleton(
        redis.RedisClient,
        sentinel_client=redis_sentinel_connection,
        service_name=config.REDIS_MASTER_SET,
        connection_options=providers.Dict(
            dict_={
                "password": config.REDIS_PASSWORD,
                "decode_responses": config.REDIS_DECODE_RESPONSES,
                "retry_on_timeout": config.REDIS_RETRY_ON_TIMEOUT,
            },
        ),
    )

    redis_cache = providers.Singleton(
        cache.RedisCache,
        client=redis_client,
        default_ttl=config.CACHE_DEFAULT_TTL,
    )

    cache_repository = providers.Singleton(
        repositories.CacheRepository,
        cache=redis_cache,
    )

    cache_key_builder = providers.Singleton(cache.CacheKeyBuilder)

    elastic_storage = providers.Singleton(
        storage.ElasticStorage,
        client=elastic_client,
    )

    # Domain -> Genres

    genre_repository = providers.Singleton(
        genres.GenreRepository,
        storage_repository=providers.Singleton(
            repositories.ElasticCacheRepository,
            elastic_repository=providers.Singleton(
                repositories.ElasticRepository,
                storage=elastic_storage,
                index_name="genre",
            ),
            cache_repository=cache_repository,
            key_factory=providers.Callable(genres.genre_key_factory).provider,
        ),
    )

    # Domain -> Films

    film_key_factory_ = providers.Callable(
        films.film_key_factory,
        key_builder=cache_key_builder,
        min_length=config.CACHE_HASHED_KEY_LENGTH,
    )

    film_repository = providers.Singleton(
        films.FilmRepository,
        storage_repository=providers.Singleton(
            repositories.ElasticCacheRepository,
            elastic_repository=providers.Singleton(
                repositories.ElasticRepository,
                storage=elastic_storage,
                index_name="movies",
            ),
            cache_repository=cache_repository,
            key_factory=film_key_factory_.provider,
        ),
    )

    # Domain -> Persons

    person_key_factory_ = providers.Callable(
        persons.person_key_factory,
        key_builder=cache_key_builder,
        min_length=config.CACHE_HASHED_KEY_LENGTH,
    )

    person_repository = providers.Singleton(
        persons.PersonRepository,
        storage_repository=providers.Singleton(
            repositories.ElasticCacheRepository,
            elastic_repository=providers.Singleton(
                repositories.ElasticRepository,
                storage=elastic_storage,
                index_name="person",
            ),
            cache_repository=cache_repository,
            key_factory=person_key_factory_.provider,
        ),
        film_repository=film_repository,
    )

    # Domain -> Users

    user_service = providers.Singleton(users.UserService)


def override_providers(container: Container, /) -> Container:
    """Override providers with stubs."""
    return container
