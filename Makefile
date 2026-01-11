# Makefile for DocC2Context Service

.PHONY: help
help:
	@echo "Available commands:"
	@echo "  help              - Show this help message"
	@echo "  install           - Install project dependencies"
	@echo "  test              - Run tests"
	@echo "  lint              - Run linting"
	@echo "  format            - Format code"
	@echo "  type-check        - Run type checking"
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

.PHONY: test
test:
	@echo "Running tests..."
	python -m pytest -v --tb=short

.PHONY: lint
lint:
	@echo "Running linting..."
	python -m ruff check . --fix

.PHONY: format
format:
	@echo "Formatting code..."
	python -m black . --check

.PHONY: type-check
type-check:
	@echo "Running type checking..."
	python -m mypy . --ignore-missing-imports

.PHONY: validate
validate:
	@echo "Running all validation checks..."
	$(MAKE) lint
	$(MAKE) format
	$(MAKE) type-check
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