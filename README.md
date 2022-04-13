# Netflix API
API for online streaming service _Netflix_.

## Technologies:
- FastAPI
- Elasticsearch
- Redis


## Configuration
Docker containers:
 1. redis
 2. api

docker-compose files:
 1. `docker-compose.yml` - for local development

To run docker containers you have to create a `.env` file in the root directory.

**Example of `.env` file:**

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

# ETL
DB_POSTGRES_BATCH_SIZE=500
ES_TIMEOUT=3s
```

### Start project:

Local:
```shell
docker-compose build
docker-compose up
```

## Development
Sync environment with requirements.*.txt (install missing dependencies, remove redundant ones, update existing).
```shell
make sync-requirements
```

Generate requirements.\*.txt files (need to re-generate after making changes in requirements.\*.in files):
```shell
make compile-requirements
```

Use `requirements.local.in` for local requirements. You have to specify constraints files (-c ...)

Example:
```shell
# requirements.local.txt

-c requirements.txt

ipython
```

### Code style:

Before pushing a commit run all linters:

```shell
make lint
```


### pre-commit:

To configure pre-commit on your local machine:
```shell
pre-commit install
```

## Documentation
OpenAPI 3 documentation can be found at:
- `${PROJECT_BASE_URL}/docs` - Swagger schema
- `${PROJECT_BASE_URL}/redoc` - ReDoc schema
- `${PROJECT_BASE_URL}/openapi.json` - OpenAPI json schema
