.PHONY: help up down logs migrate seed test clean lint format

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## Show logs
	docker-compose logs -f

migrate: ## Run database migrations
	docker-compose exec api alembic upgrade head

migrate-create: ## Create a new migration
	docker-compose exec api alembic revision --autogenerate -m "$(message)"

seed: ## Seed the database with sample data
	docker-compose exec api python scripts/create_tenant_and_apikey.py

test: ## Run tests
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

test-local: ## Run tests locally
	pytest tests/ -v

clean: ## Clean up containers and volumes
	docker-compose down -v
	docker system prune -f

lint: ## Run linting
	ruff check backend/
	mypy backend/

format: ## Format code
	black backend/
	isort backend/
	ruff check --fix backend/

install: ## Install dependencies
	pip install -r requirements.txt

dev: ## Start development environment
	docker-compose up -d db
	sleep 5
	uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
