# Netflix API
АПИ для онлайн-кинотеатра _Netflix_.

## Сервисы
- ETL + Admin panel: https://github.com/ReznikovRoman/yandex-etl
- Movies API: https://github.com/ReznikovRoman/netflix_movies_api

## Конфигурация
Докер контейнеры:
 1. redis-api
 2. api
 3. db
 4. redis
 5. elasticsearch
 6. kibana
 7. server
 8. etl

Файлы docker-compose:
 1. `docker-compose.yml` - для локальной разработки

Для запуска контейнеров нужно создать файл `.env` в корне проекта.

**Пример `.env`:**

```dotenv
ENV=.env

# Python
PYTHONUNBUFFERED=1

# Project
NETFLIX_PROJECT_BASE_URL=http://localhost:8001
NETFLIX_API_V1_STR=/api/v1
NETFLIX_SERVER_NAME=localhost
NETFLIX_SERVER_HOST=http://0.0.0.0:8001
NETFLIX_PROJECT_NAME=netflix
NETFLIX_DEBUG=1

# Admin
# Django
DJANGO_SETTINGS_MODULE=netflix.settings
DJANGO_CONFIGURATION=External
DJANGO_ADMIN=django-cadmin
DJANGO_SECRET_KEY=
ALLOWED_HOSTS=localhost,127.0.0.1

# Project
PROJECT_BASE_URL=http://localhost:8000
PROJECT_LOG_SQL=0

# Media
MEDIA_URL=/media/
STATIC_URL=/staticfiles/

# Postgres
DB_HOST=db
DB_PORT=5432
DB_NAME=
DB_USER=
DB_PASSWORD=

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DECODE_RESPONSES=1

# Elasticsearch
ES_HOST=elasticsearch
ES_PORT=9200
```

### Запуск проекта:

Локально:
```shell
docker-compose build
docker-compose up
```

## Разработка
Синхронизировать окружение с `requirements.txt` / `requirements.dev.txt` (установит отсутствующие пакеты, удалит лишние, обновит несоответствующие версии):
```shell
make sync-requirements
```

Сгенерировать requirements.\*.txt files (нужно пере-генерировать после изменений в файлах requirements.\*.in):
```shell
make compile-requirements
```

Используем `requirements.local.in` для пакетов, которые нужно только разработчику. Обязательно нужно указывать _constraints files_ (-c ...)

Пример:
```shell
# requirements.local.txt

-c requirements.txt

ipython
```

### Code style:

Перед коммитом проверяем, что код соответствует всем требованиям:

```shell
make lint
```


### pre-commit:

Для настройки pre-commit:
```shell
pre-commit install
```

## Документация
Документация в формате OpenAPI 3 доступна по адресам:
- `${PROJECT_BASE_URL}/docs` - Swagger
- `${PROJECT_BASE_URL}/redoc` - ReDoc
- `${PROJECT_BASE_URL}/openapi.json` - OpenAPI json
