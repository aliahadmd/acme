# Single command surface for humans AND AI agents.
# Every workflow starts here — never guess commands, `make help` lists them all.

.DEFAULT_GOAL := help

PROJECT := acme

.PHONY: help install dev up down logs ps test lint format typecheck build client \
        migrate migration docker-build-api docker-build-web check

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

install: ## Install everything + create local .env files from examples (never overwrites)
	@cp -n .env.example .env 2>/dev/null; true
	@cp -n apps/api/.env.example apps/api/.env 2>/dev/null; true
	@cp -n apps/web/.env.example apps/web/.env 2>/dev/null; true
	pnpm install
	cd apps/api && uv sync

dev: ## Start dev infra (postgres/redis) + api + web with hot reload
	docker compose up -d postgres redis
	pnpm dev

up: ## Start local dev infra containers (postgres, redis, mailpit)
	docker compose up -d

down: ## Stop local dev infra containers
	docker compose down

logs: ## Follow dev infra logs
	docker compose logs -f

ps: ## Show dev infra container status
	docker compose ps

check: lint typecheck test ## Run everything CI runs, locally

test: ## Run all tests (api: pytest, web: vitest)
	pnpm test

lint: ## Lint everything (biome + ruff)
	pnpm lint

format: ## Auto-format everything (biome)
	pnpm format

typecheck: ## Type-check everything (tsc + ty)
	pnpm typecheck

build: ## Build all packages/apps
	pnpm build

client: ## Regenerate the typed API client from the FastAPI OpenAPI schema
	pnpm client

migrate: ## Apply database migrations (alembic upgrade head)
	cd apps/api && uv run alembic upgrade head

migration: ## Create a new migration: make migration m="add orders table"
	cd apps/api && uv run alembic revision --autogenerate -m "$(m)"

docker-build-api: ## Build the api Docker image locally
	docker build -t $(PROJECT)-api:dev apps/api

docker-build-web: ## Build the web Docker image locally (uses repo root as context)
	docker build -t $(PROJECT)-web:dev -f apps/web/Dockerfile .
