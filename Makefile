# Makefile for DocC2Context Service

.PHONY: help
help:
	@echo "Available commands:"
	@echo "  help              - Show this help message"
	@echo "  install           - Install project dependencies"
	@echo "  install-dev       - Install development dependencies"
	@echo "  setup-dev         - Setup development environment"
	@echo "  test              - Run tests"
	@echo "  lint              - Run linting"
	@echo "  format            - Format code (black + isort)"
	@echo "  type-check        - Run type checking"
	@echo "  quality-check     - Run all quality checks (lint, format, type)"
	@echo "  env-check         - Check environment configuration"
	@echo "  prod-ready        - Check production readiness"
	@echo "  validate          - Run all validation checks"
	@echo "  run               - Run the FastAPI application"
	@echo "  build-docker      - Build Docker image"
	@echo "  clean             - Clean build artifacts"
	@echo "  health-check      - Check application health"
	@echo "  api-test          - Test API endpoints"
	@echo "  validate-project  - Run comprehensive project validation"

.PHONY: install
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

.PHONY: install-dev
install-dev:
	@echo "Installing development dependencies..."
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

.PHONY: setup-dev
setup-dev:
	@echo "Setting up development environment..."
	./scripts/setup_dev.sh

.PHONY: test
test:
	@echo "Running tests..."
	python -m pytest -v --tb=short

.PHONY: lint
lint:
	@echo "Running linting..."
	ruff check app/ tests/

.PHONY: format
format:
	@echo "Formatting code..."
	./scripts/format.sh

.PHONY: type-check
type-check:
	@echo "Running type checking..."
	mypy app/

.PHONY: quality-check
quality-check:
	@echo "Running code quality checks..."
	./scripts/check_quality.sh

.PHONY: env-check
env-check:
	@echo "Checking environment configuration..."
	python scripts/check_env.py

.PHONY: prod-ready
prod-ready:
	@echo "Checking production readiness..."
	./scripts/check_prod_ready.sh

.PHONY: validate
validate:
	@echo "Running all validation checks..."
	$(MAKE) quality-check
	$(MAKE) test
	$(MAKE) health-check

.PHONY: run
run:
	@echo "Running FastAPI application..."
	uvicorn app.main:app --reload

.PHONY: build-docker
build-docker:
	@echo "Building Docker image..."
	docker build -t docc2context-service .

.PHONY: clean
clean:
	@echo "Cleaning build artifacts..."
	rm -rf .pytest_cache
	rm -rf __pycache__
	rm -rf app/__pycache__
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf .dockerignore

.PHONY: health-check
health-check:
	@echo "Checking application health..."
	python -c "from fastapi.testclient import TestClient; from app.main import app; client = TestClient(app); response = client.get('/api/v1/health'); print(f'Health check status: {response.status_code}, response: {response.json()}')"

.PHONY: api-test
api-test:
	@echo "Testing API endpoints..."
	python -c "from fastapi.testclient import TestClient; from app.main import app; client = TestClient(app); print('Testing /api/v1/health...'); response = client.get('/api/v1/health'); print(f'Status: {response.status_code}'); print('Testing /api/v1/convert...'); response = client.post('/api/v1/convert'); print(f'Status: {response.status_code}'); print('Testing static files...'); response = client.get('/static/index.html'); print(f'Status: {response.status_code}'); print('Testing /api/v1/convert with file...'); response = client.post('/api/v1/convert', files={'file': ('test.zip', open('test.zip', 'rb'), 'application/zip')}); print(f'Status: {response.status_code}')"

.PHONY: validate-project
validate-project:
	@echo "Running comprehensive project validation..."
	python scripts/validate.py