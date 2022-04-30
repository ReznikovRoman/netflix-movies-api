from typing import Any


ES_DSNS: list[dict[str, Any]] = [
    {"host": "localhost", "port": "9200"},
]

ES_INDEX_SETTINGS = {
    "refresh_interval": "1s",
    "analysis": {
        "filter": {
            "english_stop": {
                "type": "stop",
                "stopwords": "_english_",
            },
            "english_stemmer": {
                "type": "stemmer",
                "language": "english",
            },
            "english_possessive_stemmer": {
                "type": "stemmer",
                "language": "possessive_english",
            },
            "russian_stop": {
                "type": "stop",
                "stopwords": "_russian_",
            },
            "russian_stemmer": {
                "type": "stemmer",
                "language": "russian",
            },
        },
        "analyzer": {
            "ru_en": {
                "tokenizer": "standard",
                "filter": [
                    "lowercase",
                    "english_stop",
                    "english_stemmer",
                    "english_possessive_stemmer",
                    "russian_stop",
                    "russian_stemmer",
                ],
            },
        },
    },
}

ES_MOVIES_MAPPING = {
    "dynamic": "strict",
    "properties": {
        "uuid": {
            "type": "keyword",
        },
        "imdb_rating": {
            "type": "float",
        },
        "age_rating": {
            "type": "text",
        },
        "release_date": {
            "type": "date",
        },
        "genre": {
            "type": "nested",
            "dynamic": "strict",
            "properties": {
                "uuid": {
                    "type": "keyword",
                },
                "name": {
                    "type": "text",
                    "analyzer": "ru_en",
                    "fields": {
                        "raw": {
                            "type": "keyword",
                        },
                    },
                },
            },
        },
        "title": {
            "type": "text",
            "analyzer": "ru_en",
            "fields": {
                "raw": {
                    "type": "keyword",
                },
            },
        },
        "description": {
            "type": "text",
            "analyzer": "ru_en",
        },
        "genres_names": {
            "type": "text",
            "analyzer": "ru_en",
        },
        "actors_names": {
            "type": "text",
            "analyzer": "ru_en",
        },
        "writers_names": {
            "type": "text",
            "analyzer": "ru_en",
        },
        "directors_names": {
            "type": "text",
            "analyzer": "ru_en",
        },
        "actors": {
            "type": "nested",
            "dynamic": "strict",
            "properties": {
                "uuid": {
                    "type": "keyword",
                },
                "full_name": {
                    "type": "text",
                    "analyzer": "ru_en",
                },
            },
        },
        "writers": {
            "type": "nested",
            "dynamic": "strict",
            "properties": {
                "uuid": {
                    "type": "keyword",
                },
                "full_name": {
                    "type": "text",
                    "analyzer": "ru_en",
                },
            },
        },
        "directors": {
            "type": "nested",
            "dynamic": "strict",
            "properties": {
                "uuid": {
                    "type": "keyword",
                },
                "full_name": {
                    "type": "text",
                    "analyzer": "ru_en",
                },
            },
        },
    },
}

ES_GENRE_MAPPING = {
    "dynamic": "strict",
    "properties": {
        "uuid": {
            "type": "keyword",
        },
        "name": {
            "type": "text",
            "analyzer": "ru_en",
            "fields": {
                "raw": {
                    "type": "keyword",
                },
            },
        },
    },
}

ES_PERSON_MAPPING = {
    "dynamic": "strict",
    "properties": {
        "uuid": {
            "type": "keyword",
        },
        "full_name": {
            "type": "text",
            "analyzer": "ru_en",
            "fields": {
                "raw": {
                    "type": "keyword",
                },
            },
        },
        "films_ids": {
            "type": "keyword",
        },
        "roles": {
            "type": "nested",
            "properties": {
                "role": {
                    "type": "text",
                    "analyzer": "ru_en",
                    "fields": {
                        "raw": {
                            "type": "keyword",
                        },
                    },
                },
                "films": {
                    "type": "nested",
                    "properties": {
                        "uuid": {
                            "type": "keyword",
                        },
                        "title": {
                            "type": "text",
                            "analyzer": "ru_en",
                            "fields": {
                                "raw": {
                                    "type": "keyword",
                                },
                            },
                        },
                        "imdb_rating": {
                            "type": "float",
                        },
                        "age_rating": {
                            "type": "text",
                        },
                        "release_date": {
                            "type": "date",
                        },
                    },
                },
            },
        },
    },
}
