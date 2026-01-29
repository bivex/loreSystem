.PHONY: help install install-dev test test-unit test-integration test-e2e mutation-test lint format type-check clean db-init db-migrate db-downgrade es-init run-tests

# Colors for output
BLUE=\033[0;34m
GREEN=\033[0;32m
RED=\033[0;31m
NC=\033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)MythWeave System - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(NC)"
	pip install --upgrade pip
	pip install -r requirements.txt
	@echo "$(GREEN)✓ Installation complete$(NC)"

install-dev: install ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	pip install -r requirements-dev.txt
	@echo "$(GREEN)✓ Development setup complete$(NC)"

test: ## Run all tests
	@echo "$(BLUE)Running all tests...$(NC)"
	PYTHONPATH=/Volumes/External/Code/loreSystem/src pytest tests/ -v --cov=src --cov-report=term-missing
	@echo "$(GREEN)✓ Tests complete$(NC)"

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	pytest tests/unit/ -v -m unit
	@echo "$(GREEN)✓ Unit tests complete$(NC)"

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	pytest tests/integration/ -v -m integration
	@echo "$(GREEN)✓ Integration tests complete$(NC)"

test-e2e: ## Run end-to-end tests only
	@echo "$(BLUE)Running E2E tests...$(NC)"
	pytest tests/e2e/ -v -m e2e
	@echo "$(GREEN)✓ E2E tests complete$(NC)"

mutation-test: ## Run mutation testing to find test coverage gaps
	@echo "$(BLUE)Running mutation tests...$(NC)"
	python mutation_tester.py
	@echo "$(GREEN)✓ Mutation testing complete$(NC)"

lint: ## Run linters
	@echo "$(BLUE)Running linters...$(NC)"
	flake8 src/ tests/
	pylint src/
	@echo "$(GREEN)✓ Linting complete$(NC)"

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	black src/ tests/
	isort src/ tests/
	@echo "$(GREEN)✓ Formatting complete$(NC)"

type-check: ## Run type checker
	@echo "$(BLUE)Running type checker...$(NC)"
	mypy src/
	@echo "$(GREEN)✓ Type checking complete$(NC)"

clean: ## Clean up generated files
	@echo "$(BLUE)Cleaning up...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov/ dist/ build/
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

db-init: ## Initialize database
	@echo "$(BLUE)Initializing database...$(NC)"
	createdb lore_system || echo "Database may already exist"
	alembic upgrade head
	@echo "$(GREEN)✓ Database initialized$(NC)"

db-migrate: ## Create new migration
	@echo "$(BLUE)Creating new migration...$(NC)"
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"
	@echo "$(GREEN)✓ Migration created$(NC)"

db-upgrade: ## Upgrade database to latest version
	@echo "$(BLUE)Upgrading database...$(NC)"
	alembic upgrade head
	@echo "$(GREEN)✓ Database upgraded$(NC)"

db-downgrade: ## Downgrade database by one version
	@echo "$(BLUE)Downgrading database...$(NC)"
	alembic downgrade -1
	@echo "$(GREEN)✓ Database downgraded$(NC)"

db-reset: ## Reset database (WARNING: destroys data)
	@echo "$(RED)WARNING: This will destroy all data!$(NC)"
	@read -p "Are you sure? [y/N] " confirm; \
	if [ "$$confirm" = "y" ]; then \
		dropdb lore_system 2>/dev/null || true; \
		createdb lore_system; \
		alembic upgrade head; \
		echo "$(GREEN)✓ Database reset complete$(NC)"; \
	else \
		echo "Cancelled"; \
	fi

es-init: ## Initialize Elasticsearch indices
	@echo "$(BLUE)Initializing Elasticsearch indices...$(NC)"
	python migrations/elasticsearch/init_indices.py
	@echo "$(GREEN)✓ Elasticsearch initialized$(NC)"

es-recreate: ## Recreate Elasticsearch indices (destroys data)
	@echo "$(BLUE)Recreating Elasticsearch indices...$(NC)"
	python migrations/elasticsearch/init_indices.py --recreate
	@echo "$(GREEN)✓ Elasticsearch recreated$(NC)"

check: format lint type-check test ## Run all quality checks

setup: install-dev db-init es-init ## Complete setup for new developers
	@echo "$(GREEN)✓ Setup complete! Ready to develop.$(NC)"

# Docker commands (future)
docker-up: ## Start services with Docker Compose
	docker-compose up -d

docker-down: ## Stop Docker services
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f
