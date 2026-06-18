DOCKER_COMPOSE ?= docker compose

.PHONY: up test lint format migrate bootstrap shell down

up:
	$(DOCKER_COMPOSE) up --build

test:
	$(DOCKER_COMPOSE) run --rm api pytest

lint:
	$(DOCKER_COMPOSE) run --rm api sh -c "ruff check . && mypy ."

format:
	$(DOCKER_COMPOSE) run --rm api ruff format .

migrate:
	$(DOCKER_COMPOSE) run --rm api python manage.py migrate --noinput

bootstrap:
	$(DOCKER_COMPOSE) run --rm api python manage.py bootstrap_users

shell:
	$(DOCKER_COMPOSE) run --rm api python manage.py shell

down:
	$(DOCKER_COMPOSE) down
