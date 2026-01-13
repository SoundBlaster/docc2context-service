# DocC2Context Service

Web service for converting Swift DocC archives to Markdown format.

## ⚠️ Security Notice

This service processes **untrusted file uploads** and should be deployed with appropriate security measures. See:
- **[DOCS/SECURITY/SECURITY_AUDIT.md](DOCS/SECURITY/SECURITY_AUDIT.md)** - Comprehensive security audit and vulnerability analysis
- **[DOCS/SECURITY/SECURITY_CHECKLIST.md](DOCS/SECURITY/SECURITY_CHECKLIST.md)** - Production deployment security checklist
- **[DOCS/SECURITY/SECURITY_QUICKSTART.md](DOCS/SECURITY/SECURITY_QUICKSTART.md)** - Quick security guide for developers and operators

**Key Security Features Implemented:**
- ✅ Zip Slip / Path Traversal protection
- ✅ Symlink attack prevention
- ✅ Command injection prevention
- ✅ Decompression bomb protection
- ✅ Container security hardening (non-root user, resource limits)
- ✅ Input validation (file size, type, structure)
- ✅ Rate limiting support

## Overview

DocC2Context Service is a FastAPI-based web application that provides a user-friendly interface for converting Swift DocC archives to Markdown format. The service includes:

- REST API for file upload and conversion
- Web interface with drag-and-drop upload functionality
- Real-time progress tracking
- Comprehensive validation and error handling
- **Production-ready security hardening**

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

## Security

### Security Features

This service implements comprehensive security hardening to protect against common attacks:

**Input Validation:**
- File size limits (100MB default)
- ZIP structure validation
- Magic number verification
- Filename sanitization (null bytes, control characters, path traversal)
- Decompression bomb protection (5:1 ratio limit, 500MB max uncompressed)
- File count limits (5000 files max)
- Directory depth limits (10 levels max)

**ZIP Security:**
- **Zip Slip Protection**: All paths validated with `resolve()` to prevent path traversal
- **Symlink Prevention**: Symlinks detected in metadata and blocked during extraction
- **Nested ZIP Detection**: Nested archives detected and blocked
- **Safe Extraction**: Files extracted with restrictive permissions (0o600)

**Command Injection Prevention:**
- Whitelist-based command validation
- Argument sanitization (dangerous characters blocked)
- Environment variable filtering
- Null byte detection
- Always uses `shell=False` for subprocess execution

**Container Security:**
- Non-root user (appuser, UID 1000)
- Security options: `no-new-privileges:true`, capability dropping
- Resource limits: 2 CPU cores, 2GB memory
- Temporary filesystem mounted with `noexec`, `nosuid`, `nodev`
- Health checks configured

**API Security:**
- HTTPS redirect in production
- Security headers (HSTS, CSP, X-Frame-Options, X-Content-Type-Options, etc.)
- CORS configuration
- Rate limiting support (requires Redis)
- Request timeouts (30s default)
- Request size limits

### Security Documentation

- **[DOCS/SECURITY/SECURITY_AUDIT.md](DOCS/SECURITY/SECURITY_AUDIT.md)** - Comprehensive 900+ line security audit
  - Threat model and attack surface analysis
  - Detailed vulnerability analysis (5 critical, 2 high severity fixed)
  - Secure design patterns and mitigations
  - Deployment hardening advice
  - Red team notes and attack scenarios

- **[DOCS/SECURITY/SECURITY_CHECKLIST.md](DOCS/SECURITY/SECURITY_CHECKLIST.md)** - Production deployment checklist
  - Pre-deployment security configuration
  - Environment variables and secrets
  - Docker and network security
  - Monitoring and logging setup
  - Post-deployment verification

- **[DOCS/SECURITY/SECURITY_QUICKSTART.md](DOCS/SECURITY/SECURITY_QUICKSTART.md)** - Quick reference guide
  - Security testing commands
  - Common attack scenarios
  - Incident response procedures
  - Security FAQ

- **[DOCS/SECURITY/SECURITY_IMPLEMENTATION_SUMMARY.md](DOCS/SECURITY/SECURITY_IMPLEMENTATION_SUMMARY.md)** - Implementation summary of all security fixes
- **[DOCS/SECURITY/SECURITY_REVIEW_PHASE_6.md](DOCS/SECURITY/SECURITY_REVIEW_PHASE_6.md)** - Phase 6 security review results

### Running Security Tests

```bash
# Run comprehensive security test suite
python -m pytest tests/test_security.py -v

# Run all tests (includes security)
make test

# Static security analysis
pip install bandit
bandit -r app/ -ll

# Dependency vulnerability scan
pip install safety
safety check --file requirements.txt

# Container vulnerability scan
docker run --rm -v $(pwd):/app aquasec/trivy filesystem /app
```

### Security Best Practices for Deployment

1. **Never disable security features** in production
2. **Configure specific CORS origins** (remove `["*"]`)
3. **Disable API documentation** in production (`/docs`, `/redoc`)
4. **Set up Redis** for proper rate limiting
5. **Use HTTPS** with valid TLS certificates
6. **Monitor security logs** for suspicious activity
7. **Keep dependencies updated** with security patches
8. **Review SECURITY_CHECKLIST.md** before each deployment

### Reporting Security Issues

If you discover a security vulnerability:
1. **DO NOT** open a public GitHub issue
2. Contact your organization's security team using your standard incident-reporting channel (for example, a monitored security email address or incident hotline)
3. Include details of the vulnerability and steps to reproduce
4. Allow time for patching before public disclosure

> **TODO:** Configure the specific security contact information for your deployment before going to production.

## Documentation

### Main Documentation Index

- **API Documentation**: Available at `/docs` when the service is running
- **Project Documentation**: See the `DOCS/` directory
- **Work Plan**: `DOCS/Workplan.md`
- **CI/CD Pipeline**: `.github/workflows/ci-cd.yml`

### Deployment Documentation

See `DOCS/DEPLOYMENT/` for comprehensive deployment guides:
- **[DOCS/DEPLOYMENT/DEPLOYMENT_RUNBOOK.md](DOCS/DEPLOYMENT/DEPLOYMENT_RUNBOOK.md)** - Complete deployment guide
- **[DOCS/DEPLOYMENT/DEPLOYMENT_CHECKLIST.md](DOCS/DEPLOYMENT/DEPLOYMENT_CHECKLIST.md)** - Pre-deployment checklist
- **[DOCS/DEPLOYMENT/DEPLOYMENT_APPROVAL_CHECKLIST.md](DOCS/DEPLOYMENT/DEPLOYMENT_APPROVAL_CHECKLIST.md)** - Approval requirements
- **[DOCS/DEPLOYMENT/ROLLBACK_RUNBOOK.md](DOCS/DEPLOYMENT/ROLLBACK_RUNBOOK.md)** - Rollback procedures
- **[DOCS/DEPLOYMENT/PHASE5_SMOKE_TEST_SUMMARY.md](DOCS/DEPLOYMENT/PHASE5_SMOKE_TEST_SUMMARY.md)** - Smoke test results
- **[DOCS/DEPLOYMENT/TESTING_RESULTS_PHASE_5.6.md](DOCS/DEPLOYMENT/TESTING_RESULTS_PHASE_5.6.md)** - Phase 5.6 testing results

### Operations Documentation

See `DOCS/OPERATIONS/` for operational procedures:
- **[DOCS/OPERATIONS/OPERATIONS_GUIDE.md](DOCS/OPERATIONS/OPERATIONS_GUIDE.md)** - Daily operations guide
- **[DOCS/OPERATIONS/TEAM_TRAINING_MATERIALS.md](DOCS/OPERATIONS/TEAM_TRAINING_MATERIALS.md)** - Team training resources

### Incident Response

See `DOCS/PLAYBOOKS/` for incident response procedures:
- Service outage playbook
- High error rate playbook
- Resource exhaustion playbooks
- Incident response checklist

### Security Documentation

See Security section above and `DOCS/SECURITY/` directory

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
3. Consult the [Deployment Guide](DOCS/DEPLOYMENT/DEPLOYMENT_RUNBOOK.md) for production setup
4. Check the [Operations Guide](DOCS/OPERATIONS/OPERATIONS_GUIDE.md) for operational procedures
5. Review [Incident Response Playbooks](DOCS/PLAYBOOKS/) for known issues
6. Open an issue on GitHub with:
   - Error messages and stack traces
   - Steps to reproduce the issue
   - Your environment details (OS, Python version, Docker version)

## License

This project is licensed under the MIT License.