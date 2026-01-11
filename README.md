# DocC2Context Service

Web service for converting Swift DocC archives to Markdown format.

## Overview

DocC2Context Service is a FastAPI-based web application that provides a user-friendly interface for converting Swift DocC archives to Markdown format. The service includes:

- REST API for file upload and conversion
- Web interface with drag-and-drop upload functionality
- Real-time progress tracking
- Comprehensive validation and error handling

## Features

- **File Upload**: Upload DocC archives (ZIP files) through a web interface or API
- **Conversion**: Convert DocC archives to Markdown format
- **Progress Tracking**: Real-time upload and processing progress
- **Validation**: Comprehensive file validation including ZIP structure and size limits
- **Error Handling**: Clear error messages and recovery options

## Project Structure

```
docc2context-service/
├── app/                  # FastAPI application
│   ├── api/              # API endpoints
│   ├── core/             # Core utilities
│   ├── services/         # Business logic
│   └── static/           # Frontend assets
├── DOCS/                 # Documentation
├── scripts/              # Utility scripts
├── tests/                # Test files
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## Installation

### Prerequisites

- Python 3.10+
- Docker (for containerized deployment)
- Node.js (for frontend development)

### Setup

```bash
# Clone the repository
git clone https://github.com/SoundBlaster/docc2context-service.git
cd docc2context-service

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn app.main:app --reload
```

## Usage

### Running the Service

```bash
# Start the FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Access the web interface
open http://localhost:8000
```

### API Endpoints

#### Health Check - `GET /api/v1/health`

Check service health and Swift binary availability.

**Request:**
```bash
curl http://localhost:8000/api/v1/health
```

**Response (200 OK):**
```json
{
  "status": "ready",
  "binary_detected": true
}
```

**With System Checks:**
```bash
curl "http://localhost:8000/api/v1/health?include_system=true"
```

**Response (200 OK):**
```json
{
  "status": "ready",
  "binary_detected": true,
  "system": {
    "disk_space_available": true,
    "memory_available": true
  }
}
```

#### File Conversion - `POST /api/v1/convert`

Upload and convert a DocC archive to Markdown format.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/convert \
  -F "file=@/path/to/your/archive.doccarchive.zip" \
  --output converted.zip
```

**Success Response (200 OK):**
- Returns a ZIP file containing the converted Markdown content
- Content-Type: `application/zip`
- Content-Disposition: `attachment; filename="archive_converted.zip"`

**Error Responses:**

**400 Bad Request** - Invalid file type or corrupted ZIP:
```json
{
  "detail": "Invalid ZIP file: File header validation failed"
}
```

**413 Payload Too Large** - File exceeds 100MB:
```json
{
  "detail": "File size exceeds maximum allowed size of 104857600 bytes"
}
```

**500 Internal Server Error** - Conversion failure:
```json
{
  "detail": "Conversion failed: Swift CLI stderr output here"
}
```

#### Interactive API Documentation

- **Swagger UI**: `GET /docs` - Interactive API documentation with try-it-out functionality
- **ReDoc**: `GET /redoc` - Alternative API documentation format
- **OpenAPI Schema**: `GET /openapi.json` - Raw OpenAPI 3.0 specification

### Makefile Commands

The project includes a Makefile with useful commands:

```bash
# Show available commands
make help

# Install dependencies
make install
make install-dev  # Install development dependencies

# Code quality
make format           # Format code with black and isort
make lint             # Run ruff linter
make type-check       # Run mypy type checker
make quality-check    # Run all quality checks

# Testing and validation
make test             # Run tests
make validate         # Run all validation checks (quality + tests + health)
make validate-project # Run comprehensive project validation

# Development
make run              # Run the application with uvicorn
make build-docker     # Build Docker image
```

### Code Quality

The project enforces code quality through multiple tools:

**Quality Tools:**
- **Black**: Code formatter (line length: 100)
- **isort**: Import sorter (black-compatible profile)
- **Ruff**: Fast Python linter (replaces flake8, pyflakes, etc.)
- **Mypy**: Static type checker (warnings-only for MVP)

**Running Quality Checks:**

```bash
# Run all quality checks
make quality-check

# Or run individually
make format      # Auto-format code
make lint        # Check for linting issues
make type-check  # Check types

# Or use the script directly
./scripts/check_quality.sh
```

**Pre-commit Hooks:**

Install pre-commit hooks to automatically format code on commit:

```bash
# Install development dependencies
make install-dev

# Install pre-commit hooks
pre-commit install

# Run hooks manually on all files
pre-commit run --all-files
```

**Code Quality Standards:**
- Line length: 100 characters
- Import sorting: black-compatible profile
- Type hints: Encouraged but not required (MVP)
- Docstrings: Required for public APIs
- Test coverage: >80% for critical paths

### Environment Validation

The project includes comprehensive environment validation to ensure proper configuration:

**Environment Validation Script:**

```bash
# Check current environment
make env-check

# Or run directly
python scripts/check_env.py

# Check specific environment
python scripts/check_env.py --env production

# Run health checks only
python scripts/check_env.py --health-check

# Check specific component
python scripts/check_env.py --check docker
python scripts/check_env.py --check disk
python scripts/check_env.py --check swift
```

**Environment Setup:**

```bash
# Setup development environment (automated)
make setup-dev

# Or run script directly
./scripts/setup_dev.sh
```

**Production Readiness:**

```bash
# Check if environment is ready for production
make prod-ready

# Or run script directly
./scripts/check_prod_ready.sh
```

**Environment Templates:**

The project includes environment templates for different deployment scenarios:

- `.env.development` - Development environment (relaxed security, verbose logging)
- `.env.staging` - Staging environment (moderate security)
- `.env.production` - Production environment (strict security, optimized performance)

**Environment Validation Features:**
- Validates all environment variables from `app/core/config.py`
- Type checking and value range validation
- Environment-specific security rules (dev/staging/prod)
- Security checks for production (no DEBUG, CORS restrictions, etc.)
- Health checks (Docker daemon, disk space, Swift CLI)
- Clear error messages with fix suggestions

### Validation Script

The project includes a comprehensive validation script with multiple output formats:

```bash
# Run validation (minimal output)
python scripts/validate.py

# Run validation with verbose output
python scripts/validate.py -v

# Save verbose output to file
python scripts/validate.py -v -o /tmp/validation.log

# Get JSON output for programmatic use
python scripts/validate.py --json

# Get pretty-printed JSON output
python scripts/validate.py --json --pretty-json

# Get concise summary by category
python scripts/validate.py --short-summary | grep -A 20 "DOC2CONTEXT SERVICE VALIDATION SUMMARY"

# Get detailed summary of all checks
python scripts/validate.py --summary | grep -A 100 "DOC2CONTEXT SERVICE VALIDATION RESULTS"
```

#### Validation Output Options:

- **Default**: Minimal output showing only critical issues
- **Verbose (`-v`)**: Detailed output with individual validation checks
- **JSON (`--json`)**: Compact JSON format for programmatic use
- **Pretty JSON (`--json --pretty-json`)**: Formatted JSON for human readability
- **Short Summary (`--short-summary`)**: Concise summary by category
- **Full Summary (`--summary`)**: Detailed summary of all validation checks

#### Validation Categories:

The validation script checks the following aspects of the project:
- Python environment and dependencies
- Project structure and required files
- FastAPI application configuration
- API endpoints functionality
- Docker setup and configuration
- Configuration files
- Test files and coverage

## Development

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_file.py
```

### Building Docker Image

```bash
# Build Docker image
make build-docker

# Run Docker container
docker-compose up
```

## Configuration

Environment variables can be configured in `.env` file:

```
# FastAPI configuration
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True

# File upload limits
MAX_FILE_SIZE=104857600  # 100MB
```

## Documentation

- **API Documentation**: Available at `/docs` when the service is running
- **Project Documentation**: See the `DOCS/` directory
- **Work Plan**: `DOCS/Workplan.md`
- **CI/CD Pipeline**: `.github/workflows/ci-cd.yml`

## CI/CD Pipeline

This project includes a comprehensive CI/CD pipeline using GitHub Actions:

### Pipeline Stages

1. **Validation**: Runs project validation script to check structure and configuration
2. **Testing**: Executes automated tests using pytest
3. **Build**: Creates Docker image and pushes to Docker Hub
4. **Deploy**: Deploys to production environment

### Requirements

To use the CI/CD pipeline, configure these GitHub secrets:
- `DOCKER_HUB_USERNAME`: Your Docker Hub username
- `DOCKER_HUB_TOKEN`: Your Docker Hub access token

### Usage

The pipeline runs automatically on:
- Pushes to the `main` branch
- Pull requests targeting the `main` branch

For manual execution:
1. Go to GitHub Actions tab
2. Select "CI/CD Pipeline"
3. Click "Run workflow"

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## Troubleshooting

### Common Issues

#### Installation Issues

**Problem: `pip install` fails with dependency errors**
```bash
# Solution: Upgrade pip and try again
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

**Problem: Docker build fails with Swift compilation errors**
```bash
# Solution: Ensure you have enough memory allocated to Docker (minimum 4GB recommended)
# Check Docker settings and increase memory limit if needed
docker system info | grep -i memory
```

#### Runtime Issues

**Problem: Health check returns `binary_detected: false`**
```bash
# Solution: Verify Swift binary is in the Docker image
docker run --rm docc2context-service which docc2context
# If missing, rebuild the Docker image
make build-docker
```

**Problem: Conversion fails with timeout error**
```bash
# Solution: Large archives may need more time. Check logs for details:
docker logs <container-id>
# Consider increasing timeout in app/core/config.py
```

**Problem: Upload fails with 413 error**
```bash
# Solution: File exceeds 100MB limit. Compress the archive or increase MAX_FILE_SIZE in .env
# Note: Increasing the limit may require more server resources
```

#### Development Issues

**Problem: Tests fail with import errors**
```bash
# Solution: Ensure you're in the project directory and dependencies are installed
cd /path/to/docc2context-service
pip install -r requirements.txt
pytest -v
```

**Problem: Validation script fails**
```bash
# Solution: Run with verbose output to identify the issue
python scripts/validate.py -v
# Check for missing dependencies or configuration issues
```

### Getting Help

If you encounter issues not listed here:

1. Check the application logs for detailed error messages
2. Review the [API Documentation](http://localhost:8000/docs) for endpoint details
3. Consult the [Deployment Guide](DOCS/DEPLOYMENT.md) for production setup
4. Open an issue on GitHub with:
   - Error messages and stack traces
   - Steps to reproduce the issue
   - Your environment details (OS, Python version, Docker version)

## License

This project is licensed under the MIT License.