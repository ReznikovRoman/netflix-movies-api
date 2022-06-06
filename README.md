# Netflix API
АПИ для онлайн-кинотеатра _Netflix_.

## Сервисы
- Netflix Admin:
  - Панель администратора для управления онлайн-кинотеатром (редактирование фильмов, жанров, актеров)
  - https://github.com/ReznikovRoman/netflix-admin
- Netflix ETL:
  - ETL пайплайн для синхронизации данных между БД сервиса Netflix Admin и Elasticsearch
  - https://github.com/ReznikovRoman/netflix-etl
- Netflix Movies API:
  - АПИ фильмов
  - https://github.com/ReznikovRoman/netflix-movies-api
- Netflix Auth API:
  - Сервис авторизации - управление пользователями и ролями
  - https://github.com/ReznikovRoman/netflix-auth-api

## Настройка и запуск

Docker конфигурации содержат контейнеры:
 1. redis-sentinel
 2. redis
 3. redis-slave
 4. redis-slave-2
 5. traefik
 6. server
 7. db_admin
 8. server_admin
 9. redis_etl
 10. elasticsearch_etl
 11. kibana_etl
 12. etl

Файлы docker-compose:
 1. `docker-compose.yml` - для локальной разработки

Для запуска контейнеров нужно создать файл `.env` в корне проекта.

**Пример `.env`:**

```dotenv
ENV=.env

# Python
PYTHONUNBUFFERED=1

# Netflix Admin
# Django
DJANGO_SETTINGS_MODULE=netflix.settings
DJANGO_CONFIGURATION=External
DJANGO_ADMIN=django-cadmin
DJANGO_SECRET_KEY=7+k@v^z+j%e^%5a%0zyxb-i897ct)rrb085+3l9f&0z2p8ykdd
ALLOWED_HOSTS=localhost,127.0.0.1
# Project
NA_PROJECT_BASE_URL=http://localhost:8000
# Media
NA_MEDIA_URL=/media/
NA_STATIC_URL=/staticfiles/
# Postgres
NA_DB_HOST=db_admin
NA_DB_PORT=5432
NA_DB_NAME=netflix_admin
NA_DB_USER=yandex
NA_DB_PASSWORD=netflix
# Scripts
NA_DB_POSTGRES_BATCH_SIZE=500

# Netflix ETL
# Redis
NE_REDIS_HOST=redis_etl
NE_REDIS_PORT=6379
NE_REDIS_DECODE_RESPONSES=1
# Elasticsearch
NE_ES_HOST=elasticsearch_etl
NE_ES_PORT=9200

# Netflix Movies API
# Project
NMA_PROJECT_BASE_URL=http://api.localhost:8008
NMA_API_V1_STR=/api/v1
NMA_SERVER_NAME=localhost
NMA_SERVER_HOSTS=http://api.localhost:8008
NMA_PROJECT_NAME=netflix
NMA_DEBUG=1
# Redis
NMA_REDIS_SENTINELS=redis-sentinel
NMA_REDIS_MASTER_SET=redis_cluster
NMA_REDIS_PASSWORD=change_me
NMA_REDIS_DECODE_RESPONSES=1
NMA_REDIS_RETRY_ON_TIMEOUT=1
# Elasticsearch
NMA_ES_RETRY_ON_TIMEOUT=1

# Netflix Auth API
NMA_AUTH_SERVICE_URL=http://traefik-auth:80
FLASK_APP=main.py
# Project
NAA_SECRET_KEY=n_0*we^k^onk9$@2c6nlh)=9hcp71e*b0(t^jn=$!qzybwk-h4
NAA_SQLALCHEMY_ECHO=1
NAA_PROJECT_BASE_URL=http://api-auth.localhost:8009
NAA_API_V1_STR=/api/v1
NAA_SERVER_HOSTS=http://api-auth.localhost:8009
NAA_SERVER_PORT=8002
NAA_PROJECT_NAME=netflix-auth
NAA_THROTTLE_KEY_PREFIX=limiter:
NAA_THROTTLE_DEFAULT_LIMITS=50/hour
NAA_THROTTLE_USER_REGISTRATION_LIMITS=5/minute
NAA_DEBUG=1
# auth0
NAA_AUTH0_DOMAIN=dummy.com
NAA_AUTH0_API_AUDIENCE=https://dummy.com
NAA_AUTH0_ISSUER=https://dummy.com/
NAA_AUTH0_CLIENT_ID=change-me
NAA_AUTH0_CLIENT_SECRET=change-me
NAA_AUTH0_AUTHORIZATION_URL=https://dummy.com/oauth/token
# Postgres
NAA_DB_HOST=db-auth
NAA_DB_PORT=5432
NAA_DB_NAME=netflix_auth
NAA_DB_USER=roman
NAA_DB_PASSWORD=yandex
# Redis
NAA_REDIS_HOST=redis-auth
NAA_REDIS_PORT=6379
NAA_REDIS_THROTTLE_STORAGE_DB=2
NAA_REDIS_DEFAULT_CHARSET=utf-8
NAA_REDIS_DECODE_RESPONSES=1
NAA_REDIS_RETRY_ON_TIMEOUT=1
```

### Запуск проекта:

Локально:
```shell
docker-compose build
docker-compose up
```

**Для заполнения БД тестовыми данными**
```shell
docker-compose run --rm server_admin bash -c "cd /app/scripts/load_db && python load_data.py"
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

### Тесты
Запуск тестов (всех, кроме функциональных) с экспортом переменных окружения из `.env` файла:
```shell
export $(echo $(cat .env | sed 's/#.*//g'| xargs) | envsubst) && make test
```

Для функциональных тестов нужно создать файл `.env` в папке ./tests/functional

**Пример `.env`:**
```dotenv
ENV=.env

# Python
PYTHONUNBUFFERED=1

# Netflix ETL
# Elasticsearch
NE_ES_HOST=elasticsearch
NE_ES_PORT=9200

# Netflix Movies API
# Project
NMA_PROJECT_BASE_URL=http://api.localhost:8008
NMA_API_V1_STR=/api/v1
NMA_SERVER_NAME=localhost
NMA_SERVER_HOSTS=http://api.localhost:8008
NMA_PROJECT_NAME=netflix
NMA_DEBUG=1
# Redis
NMA_REDIS_SENTINELS=redis-sentinel
NMA_REDIS_MASTER_SET=redis_cluster
NMA_REDIS_PASSWORD=change_me
NMA_REDIS_DECODE_RESPONSES=1
NMA_REDIS_RETRY_ON_TIMEOUT=1
# Elasticsearch
NMA_ES_RETRY_ON_TIMEOUT=1

# Netflix Auth API
NMA_AUTH_SERVICE_URL=http://traefik-auth:80
FLASK_APP=main.py
# Project
NAA_SECRET_KEY=n_0*we^k^onk9$@2c6nlh)=9hcp71e*b0(t^jn=$!qzybwk-h4
NAA_SQLALCHEMY_ECHO=1
NAA_PROJECT_BASE_URL=http://api-auth.localhost:8009
NAA_API_V1_STR=/api/v1
NAA_SERVER_HOSTS=http://api-auth.localhost:8009
NAA_SERVER_PORT=8002
NAA_PROJECT_NAME=netflix-auth
NAA_THROTTLE_KEY_PREFIX=limiter:
NAA_THROTTLE_DEFAULT_LIMITS=50/hour
NAA_THROTTLE_USER_REGISTRATION_LIMITS=5/minute
NAA_DEBUG=1
# auth0
NAA_AUTH0_DOMAIN=dummy.com
NAA_AUTH0_API_AUDIENCE=https://dummy.com
NAA_AUTH0_ISSUER=https://dummy.com/
NAA_AUTH0_CLIENT_ID=change-me
NAA_AUTH0_CLIENT_SECRET=change-me
NAA_AUTH0_AUTHORIZATION_URL=https://dummy.com/oauth/token
# Postgres
NAA_DB_HOST=db-auth
NAA_DB_PORT=5432
NAA_DB_NAME=netflix_auth
NAA_DB_USER=yandex
NAA_DB_PASSWORD=netflix
# Redis
NAA_REDIS_HOST=redis-auth
NAA_REDIS_PORT=6379
NAA_REDIS_THROTTLE_STORAGE_DB=2
NAA_REDIS_DEFAULT_CHARSET=utf-8
NAA_REDIS_DECODE_RESPONSES=1
NAA_REDIS_RETRY_ON_TIMEOUT=1

# Tests
TEST_CLIENT_BASE_URL=http://traefik:80
```

Запуск функциональных тестов:
```shell
cd ./tests/functional && docker-compose up test
```

Или через рецепт Makefile:
```shell
make dtf
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
