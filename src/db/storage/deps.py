from functools import lru_cache

from .elastic import ElasticStorage


@lru_cache()
def get_elastic_storage() -> ElasticStorage:
    return ElasticStorage()
