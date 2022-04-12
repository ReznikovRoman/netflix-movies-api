# Netflix API
API for online streaming service _Netflix_.

## Technologies:
- FastAPI
- Elasticsearch
- Redis


## Configuration
Docker containers:
 1. redis
 2. server

docker-compose files:
 1. `docker-compose.yml` - for local development

To run docker containers you have to create a `.env` file in the root directory.

**Example of `.env` file:**

```dotenv
ENV=.env

# Python
PYTHONUNBUFFERED=1

# Project
PROJECT_BASE_URL=http://localhost:8001
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

Generate requirements.*.txt files (need to re-generate after making changes in requirements.*.in files):
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
