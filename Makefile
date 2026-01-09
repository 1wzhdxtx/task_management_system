.PHONY: help install dev test lint format migrate run clean docker-up docker-down docker-build docker-logs

# Default target
help:
	@echo "Task Management System - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install      - Install production dependencies"
	@echo "  make dev          - Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make run          - Start development server"
	@echo "  make lint         - Run code linting"
	@echo "  make format       - Format code with ruff"
	@echo ""
	@echo "Database:"
	@echo "  make migrate      - Run database migrations"
	@echo "  make migrate-new  - Create new migration"
	@echo "  make db-init      - Initialize database"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run all tests with coverage"
	@echo "  make test-unit    - Run unit tests only"
	@echo "  make test-int     - Run integration tests only"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up    - Start all services with Docker Compose"
	@echo "  make docker-down  - Stop all Docker services"
	@echo "  make docker-build - Build Docker images"
	@echo "  make docker-logs  - View Docker container logs"
	@echo "  make docker-shell - Open shell in app container"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean        - Remove cache files"

# Setup
install:
	pip install -r requirements.txt

dev:
	pip install -r requirements-dev.txt

# Development
run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

lint:
	ruff check app/ tests/
	mypy app/ --ignore-missing-imports

format:
	ruff format app/ tests/
	ruff check --fix app/ tests/

# Database
migrate:
	alembic upgrade head

migrate-new:
	@read -p "Migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

migrate-down:
	alembic downgrade -1

db-init:
	python scripts/init_db.py

db-seed:
	python scripts/seed_data.py

# Testing
test:
	pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html

test-unit:
	pytest tests/unit/ -v

test-int:
	pytest tests/integration/ -v

test-fast:
	pytest tests/ -v -x --tb=short

# Docker (supports both docker-compose and docker compose)
DOCKER_COMPOSE := $(shell command -v docker-compose 2> /dev/null || echo "docker compose")

docker-build:
	$(DOCKER_COMPOSE) build

docker-up:
	$(DOCKER_COMPOSE) up -d
	@echo ""
	@echo "Services started!"
	@echo "  App:     http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"
	@echo ""
	@echo "Run 'make docker-logs' to view logs"

docker-down:
	$(DOCKER_COMPOSE) down

docker-logs:
	$(DOCKER_COMPOSE) logs -f

docker-shell:
	$(DOCKER_COMPOSE) exec app /bin/bash

docker-restart:
	$(DOCKER_COMPOSE) restart app

docker-clean:
	$(DOCKER_COMPOSE) down -v --rmi local
	@echo "Removed containers, volumes, and local images"

# Start with database admin UI (Adminer)
docker-up-tools:
	$(DOCKER_COMPOSE) --profile tools up -d
	@echo ""
	@echo "Services started!"
	@echo "  App:     http://localhost:8000"
	@echo "  Adminer: http://localhost:8080"

# Cleanup
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov/ .mypy_cache/ .ruff_cache/ 2>/dev/null || true
