from dependency_injector import containers, providers

from clients.elastic import ElasticClient
from clients.redis_cache import RedisCacheClient
from db.cache.base import CacheKeyBuilder, CacheRepository
from db.cache.redis import RedisCache
from db.storage.elastic import ElasticStorage
from repositories.base import ElasticCacheRepository, ElasticRepository
from repositories.films import FilmRepository, film_key_factory
from repositories.genres import GenreRepository, genre_key_factory
from repositories.persons import PersonRepository, person_key_factory
from services.users import UserService


class Container(containers.DeclarativeContainer):
    """Контейнер с зависимостями."""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "api.v1.endpoints.genres",
            "api.v1.endpoints.films",
            "api.v1.endpoints.persons",
        ],
    )

    config = providers.Configuration()

    # Infrastructure

    redis_cache_client = providers.Singleton(
        RedisCacheClient,
        service_name=config.REDIS_MASTER_SET,
        connection_options=providers.Dict(
            dict_={
                "password": config.REDIS_PASSWORD,
                "decode_responses": config.REDIS_DECODE_RESPONSES,
                "retry_on_timeout": config.REDIS_RETRY_ON_TIMEOUT,
            },
        ),
    )

    elastic_client = providers.Singleton(ElasticClient)

    cache_key_builder = providers.Singleton(CacheKeyBuilder)

    redis_cache = providers.Singleton(
        RedisCache,
        client=redis_cache_client,
        default_ttl=config.CACHE_DEFAULT_TTL,
    )

    elastic_storage = providers.Singleton(
        ElasticStorage,
        client=elastic_client,
    )

    cache_repository = providers.Singleton(
        CacheRepository,
        cache=redis_cache,
    )

    # Domain -> Genres
    genre_repository = providers.Singleton(
        GenreRepository,
        storage_repository=providers.Singleton(
            ElasticCacheRepository,
            elastic_repository=providers.Singleton(
                ElasticRepository,
                storage=elastic_storage,
                index_name="genre",
            ),
            cache_repository=cache_repository,
            key_factory=providers.Callable(genre_key_factory).provider,
        ),
    )

    # Domain -> Films
    film_key_factory_ = providers.Callable(
        film_key_factory,
        key_builder=cache_key_builder,
        min_length=config.CACHE_HASHED_KEY_LENGTH,
    )

    film_repository = providers.Singleton(
        FilmRepository,
        storage_repository=providers.Singleton(
            ElasticCacheRepository,
            elastic_repository=providers.Singleton(
                ElasticRepository,
                storage=elastic_storage,
                index_name="movies",
            ),
            cache_repository=cache_repository,
            key_factory=film_key_factory_.provider,
        ),
    )

    # Domain -> Persons
    person_key_factory_ = providers.Callable(
        person_key_factory,
        key_builder=cache_key_builder,
        min_length=config.CACHE_HASHED_KEY_LENGTH,
    )

    person_repository = providers.Singleton(
        PersonRepository,
        storage_repository=providers.Singleton(
            ElasticCacheRepository,
            elastic_repository=providers.Singleton(
                ElasticRepository,
                storage=elastic_storage,
                index_name="person",
            ),
            cache_repository=cache_repository,
            key_factory=person_key_factory_.provider,
        ),
        film_repository=film_repository,
    )

    # Domain -> Users
    user_service = providers.Singleton(UserService)
