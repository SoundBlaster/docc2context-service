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

- **Health Check**: `GET /api/v1/health`
- **File Upload**: `POST /api/v1/convert`
- **Documentation**: `GET /docs` (Swagger UI)

### Makefile Commands

The project includes a Makefile with useful commands:

```bash
# Show available commands
make help

# Install dependencies
make install

# Run tests
make test

# Validate project
make validate-project

# Run comprehensive validation with verbose output
python scripts/validate.py -v -o /tmp/validation.log
```

### Validation Script

The project includes a comprehensive validation script:

```bash
# Run validation (minimal output)
python scripts/validate.py

# Run validation with verbose output
python scripts/validate.py -v

# Save verbose output to file
python scripts/validate.py -v -o /tmp/validation.log

# Get JSON output for programmatic use
python scripts/validate.py --json
```

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

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## License

This project is licensed under the MIT License.
```

Now you can use the updated README.md with comprehensive project information and usage instructions. The document includes sections on installation, usage, development, configuration, and contributing guidelines.