# Configuration Guide - DocC2Context Service

**Version:** 1.0.0
**Last Updated:** 2026-01-11

## Table of Contents

1. [Overview](#overview)
2. [Configuration File](#configuration-file)
3. [Configuration Parameters](#configuration-parameters)
4. [Environment-Specific Configuration](#environment-specific-configuration)
5. [Security Best Practices](#security-best-practices)
6. [Advanced Configuration](#advanced-configuration)
7. [Troubleshooting](#troubleshooting)

## Overview

The DocC2Context Service uses environment variables for configuration, managed through Pydantic Settings. This approach provides:

- Type-safe configuration with validation
- Environment variable support
- `.env` file support for local development
- Clear defaults with override capability

## Configuration File

### Creating Configuration

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit configuration:**
   ```bash
   nano .env  # or your preferred editor
   ```

3. **Verify configuration:**
   ```bash
   # Check that configuration loads without errors
   python -c "from app.core.config import settings; print(settings.model_dump_json(indent=2))"
   ```

### Configuration Priority

Configuration values are loaded in this order (highest priority first):

1. Environment variables set in the shell
2. Values from `.env` file
3. Default values in `app/core/config.py`

**Example:**
```bash
# .env file has: API_PORT=8000
# Shell environment has: export API_PORT=9000
# Result: Service runs on port 9000 (shell environment wins)
```

## Configuration Parameters

### API Configuration

#### `API_HOST`
- **Type:** String
- **Default:** `0.0.0.0`
- **Description:** Host to bind the API server to
- **Valid Values:**
  - `0.0.0.0` - Accept connections from any network interface
  - `127.0.0.1` - Localhost only (for development)
  - Specific IP address - Bind to specific interface

**Example:**
```bash
# Development (all interfaces)
API_HOST=0.0.0.0

# Production behind reverse proxy (localhost only)
API_HOST=127.0.0.1
```

#### `API_PORT`
- **Type:** Integer
- **Default:** `8000`
- **Description:** Port for the API server
- **Valid Values:** 1-65535 (unprivileged ports: 1024-65535)

**Example:**
```bash
# Default FastAPI port
API_PORT=8000

# Alternative port
API_PORT=8080
```

### File Upload Configuration

#### `MAX_UPLOAD_SIZE_MB`
- **Type:** Integer
- **Default:** `100`
- **Description:** Maximum upload file size in megabytes
- **Valid Values:** 1-1000 (practical limit depends on infrastructure)

**Example:**
```bash
# Default 100MB limit
MAX_UPLOAD_SIZE_MB=100

# Increase for larger archives
MAX_UPLOAD_SIZE_MB=200
```

**Considerations:**
- Larger limits require more memory and disk space
- Each conversion uses up to 5x the upload size for workspace
- Concurrent requests multiply resource requirements

#### `MAX_DECOMPRESSED_SIZE_MB`
- **Type:** Integer
- **Default:** `500`
- **Description:** Maximum decompressed size to prevent zip bombs
- **Valid Values:** Should be 5-10x `MAX_UPLOAD_SIZE_MB`

**Example:**
```bash
# Default (5x upload limit)
MAX_DECOMPRESSED_SIZE_MB=500

# If MAX_UPLOAD_SIZE_MB=200
MAX_DECOMPRESSED_SIZE_MB=1000
```

**Security Note:** This prevents malicious zip bombs that expand to enormous sizes.

### Workspace Configuration

#### `WORKSPACE_BASE_PATH`
- **Type:** String
- **Default:** `/tmp`
- **Description:** Base path for temporary workspace directories
- **Valid Values:** Any writable directory path

**Example:**
```bash
# Default temporary directory
WORKSPACE_BASE_PATH=/tmp

# Custom workspace location
WORKSPACE_BASE_PATH=/var/docc2context/workspaces
```

**Requirements:**
- Directory must be writable by the application user
- Sufficient disk space (5x MAX_UPLOAD_SIZE_MB per concurrent conversion)
- Fast storage recommended (SSD preferred)

#### `WORKSPACE_PREFIX`
- **Type:** String
- **Default:** `swift-conv`
- **Description:** Prefix for workspace directories
- **Valid Values:** Any valid directory name (no special characters)

**Example:**
```bash
# Default prefix
WORKSPACE_PREFIX=swift-conv
# Creates: /tmp/swift-conv-{uuid}

# Custom prefix
WORKSPACE_PREFIX=docc-workspace
# Creates: /tmp/docc-workspace-{uuid}
```

#### `WORKSPACE_PERMISSIONS`
- **Type:** String (octal notation)
- **Default:** `0o700`
- **Description:** Unix file permissions for workspace directories
- **Valid Values:** Octal notation (e.g., `0o700`, `0o750`, `0o755`)

**Permission Guide:**
- `0o700` - Owner only (read/write/execute) - **Recommended**
- `0o750` - Owner + group (group read/execute)
- `0o755` - Owner + group + others (all read/execute)

**Security Note:** Use `0o700` to ensure only the application can access workspaces.

### Swift CLI Configuration

#### `SWIFT_CLI_PATH`
- **Type:** String
- **Default:** `docc2context`
- **Description:** Path to the Swift CLI binary
- **Valid Values:**
  - Binary name if in PATH: `docc2context`
  - Absolute path: `/usr/local/bin/docc2context`

**Example:**
```bash
# Binary in PATH
SWIFT_CLI_PATH=docc2context

# Absolute path
SWIFT_CLI_PATH=/usr/local/bin/docc2context

# Custom installation
SWIFT_CLI_PATH=/opt/swift/bin/docc2context
```

#### `SUBPROCESS_TIMEOUT`
- **Type:** Integer
- **Default:** `60`
- **Description:** Maximum time allowed for Swift CLI execution (seconds)
- **Valid Values:** 10-600 (10 seconds to 10 minutes)

**Example:**
```bash
# Default timeout
SUBPROCESS_TIMEOUT=60

# Longer timeout for large archives
SUBPROCESS_TIMEOUT=120
```

**Tuning Guide:**
- Small archives (<10MB): 30 seconds
- Medium archives (10-50MB): 60 seconds
- Large archives (50-100MB): 120 seconds

#### `MAX_SUBPROCESS_RETRIES`
- **Type:** Integer
- **Default:** `3`
- **Description:** Maximum retry attempts for subprocess execution
- **Valid Values:** 0-10

**Example:**
```bash
# Default retries
MAX_SUBPROCESS_RETRIES=3

# No retries (fail fast)
MAX_SUBPROCESS_RETRIES=0

# More retries for unreliable environments
MAX_SUBPROCESS_RETRIES=5
```

### Logging Configuration

#### `LOG_LEVEL`
- **Type:** String
- **Default:** `INFO`
- **Description:** Logging level for application logs
- **Valid Values:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

**Log Level Guide:**
- `DEBUG` - Verbose logging (development/troubleshooting only)
- `INFO` - Normal operations (recommended for production)
- `WARNING` - Important events only
- `ERROR` - Errors only
- `CRITICAL` - Critical errors only

**Example:**
```bash
# Production
LOG_LEVEL=INFO

# Development/Debugging
LOG_LEVEL=DEBUG

# Minimal logging
LOG_LEVEL=WARNING
```

**Performance Note:** `DEBUG` level generates significant log volume and may impact performance.

### CORS Configuration

#### `CORS_ORIGINS`
- **Type:** String (comma-separated list)
- **Default:** `*`
- **Description:** Allowed CORS origins for cross-origin requests
- **Valid Values:**
  - `*` - Allow all origins (development only)
  - Comma-separated URLs: `https://example.com,https://app.example.com`

**Example:**
```bash
# Development (allow all)
CORS_ORIGINS=*

# Production (specific origins)
CORS_ORIGINS=https://example.com,https://app.example.com

# Multiple environments
CORS_ORIGINS=https://example.com,https://staging.example.com,http://localhost:3000
```

**Security Warning:** Never use `*` in production. Specify exact origins.

### Application Metadata

#### `APP_NAME`
- **Type:** String
- **Default:** `DocC2Context Service`
- **Description:** Application name (displayed in API docs)

#### `APP_VERSION`
- **Type:** String
- **Default:** `0.1.0`
- **Description:** Application version (displayed in API docs)

#### `APP_DESCRIPTION`
- **Type:** String
- **Default:** `Swift DocC to Markdown Web Converter (MVP)`
- **Description:** Application description (displayed in API docs)

### Security Configuration

#### `ENVIRONMENT`
- **Type:** String
- **Default:** `development`
- **Description:** Current environment
- **Valid Values:** `development`, `staging`, `production`

**Example:**
```bash
# Development
ENVIRONMENT=development

# Production
ENVIRONMENT=production
```

**Behavior Changes:**
- `production`: Stricter validation, detailed errors hidden from users
- `development`: Relaxed validation, detailed error messages

#### `ALLOWED_HOSTS`
- **Type:** String (comma-separated list)
- **Default:** `*`
- **Description:** Allowed hosts for TrustedHostMiddleware
- **Valid Values:**
  - `*` - Allow all hosts (development only)
  - Comma-separated hostnames: `example.com,api.example.com`

**Example:**
```bash
# Development
ALLOWED_HOSTS=*

# Production
ALLOWED_HOSTS=example.com,api.example.com,www.example.com
```

#### `RATE_LIMIT`
- **Type:** Integer
- **Default:** `100`
- **Description:** Maximum requests per minute per IP
- **Valid Values:** 1-10000

**Example:**
```bash
# Default rate limit
RATE_LIMIT=100

# Stricter limit for public API
RATE_LIMIT=50

# Relaxed limit for internal API
RATE_LIMIT=500
```

**Tuning Guide:**
- Public API: 10-50 requests/minute
- Internal API: 100-500 requests/minute
- Development: 1000+ requests/minute

## Environment-Specific Configuration

### Development Environment

**File: `.env.development`**
```bash
ENVIRONMENT=development
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=DEBUG
CORS_ORIGINS=*
ALLOWED_HOSTS=*
MAX_UPLOAD_SIZE_MB=50
SUBPROCESS_TIMEOUT=30
```

**Usage:**
```bash
cp .env.development .env
uvicorn app.main:app --reload
```

### Staging Environment

**File: `.env.staging`**
```bash
ENVIRONMENT=staging
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
CORS_ORIGINS=https://staging.example.com
ALLOWED_HOSTS=staging.example.com,api.staging.example.com
MAX_UPLOAD_SIZE_MB=100
SUBPROCESS_TIMEOUT=60
RATE_LIMIT=100
```

### Production Environment

**File: `.env.production`**
```bash
ENVIRONMENT=production
API_HOST=127.0.0.1  # Behind reverse proxy
API_PORT=8000
LOG_LEVEL=INFO
CORS_ORIGINS=https://example.com,https://www.example.com
ALLOWED_HOSTS=example.com,www.example.com,api.example.com
MAX_UPLOAD_SIZE_MB=100
MAX_DECOMPRESSED_SIZE_MB=500
SUBPROCESS_TIMEOUT=60
RATE_LIMIT=50
WORKSPACE_BASE_PATH=/var/docc2context/workspaces
```

**Additional Production Setup:**
```bash
# Create workspace directory
sudo mkdir -p /var/docc2context/workspaces
sudo chown app-user:app-group /var/docc2context/workspaces
sudo chmod 700 /var/docc2context/workspaces
```

## Security Best Practices

### Configuration File Security

1. **Never commit `.env` files to version control:**
   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   echo ".env.*" >> .gitignore
   echo "!.env.example" >> .gitignore
   ```

2. **Restrict file permissions:**
   ```bash
   chmod 600 .env
   ```

3. **Use environment-specific files:**
   ```bash
   # Development
   ln -s .env.development .env

   # Production
   ln -s .env.production .env
   ```

### Production Security Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Configure specific `CORS_ORIGINS` (not `*`)
- [ ] Configure specific `ALLOWED_HOSTS` (not `*`)
- [ ] Set appropriate `RATE_LIMIT`
- [ ] Use `LOG_LEVEL=INFO` (not `DEBUG`)
- [ ] Restrict `API_HOST` to `127.0.0.1` if behind reverse proxy
- [ ] Set file permissions to `600` on `.env`
- [ ] Ensure `.env` is not in version control
- [ ] Use HTTPS/TLS for all connections
- [ ] Regularly review and rotate configuration

### Sensitive Data Handling

**DO NOT store in configuration:**
- API keys or secrets
- Database credentials
- Private keys or certificates
- User data

**If you must store secrets:**
- Use environment variables (not `.env` files in production)
- Use secrets management tools (HashiCorp Vault, AWS Secrets Manager, etc.)
- Rotate regularly
- Audit access

## Advanced Configuration

### Custom Workspace Cleanup

Create a cron job to clean orphaned workspaces:

```bash
# /etc/cron.hourly/cleanup-docc-workspaces
#!/bin/bash
find /tmp -maxdepth 1 -name "swift-conv-*" -type d -mmin +60 -exec rm -rf {} \;
```

### Load Balancer Configuration

When behind a load balancer, configure proxy headers:

```bash
# In .env
API_HOST=127.0.0.1
API_PORT=8000

# Nginx configuration
# proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
# proxy_set_header X-Forwarded-Proto $scheme;
# proxy_set_header Host $host;
```

### Resource Limits

Set Docker resource limits to prevent resource exhaustion:

```yaml
# docker-compose.yml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

## Troubleshooting

### Configuration Not Loading

**Problem:** Changes to `.env` not taking effect

**Solution:**
```bash
# Verify .env file exists
ls -la .env

# Check file permissions
chmod 644 .env

# Restart application
docker-compose restart
```

### Invalid Configuration Values

**Problem:** Application fails to start with validation error

**Solution:**
```bash
# Validate configuration
python -c "from app.core.config import settings; print(settings.model_dump_json(indent=2))"

# Check for typos in .env
cat .env | grep -v "^#" | grep "="
```

### Environment Variable Override Issues

**Problem:** Shell environment variables not overriding `.env`

**Solution:**
```bash
# Check current environment
env | grep -i api

# Clear conflicting variables
unset API_PORT

# Set explicitly
export API_PORT=9000

# Verify
python -c "from app.core.config import settings; print(settings.api_port)"
```

## Configuration Examples

### Example 1: High-Volume Production API

```bash
ENVIRONMENT=production
API_HOST=127.0.0.1
API_PORT=8000
LOG_LEVEL=WARNING
MAX_UPLOAD_SIZE_MB=200
MAX_DECOMPRESSED_SIZE_MB=1000
SUBPROCESS_TIMEOUT=120
RATE_LIMIT=500
WORKSPACE_BASE_PATH=/mnt/fast-ssd/workspaces
```

### Example 2: Restricted Internal API

```bash
ENVIRONMENT=production
API_HOST=10.0.1.100
API_PORT=8000
LOG_LEVEL=INFO
CORS_ORIGINS=https://internal.company.com
ALLOWED_HOSTS=internal.company.com
MAX_UPLOAD_SIZE_MB=50
SUBPROCESS_TIMEOUT=30
RATE_LIMIT=1000
```

### Example 3: Development with Debugging

```bash
ENVIRONMENT=development
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=DEBUG
CORS_ORIGINS=*
ALLOWED_HOSTS=*
MAX_UPLOAD_SIZE_MB=10
SUBPROCESS_TIMEOUT=300
RATE_LIMIT=10000
```

## Support

For configuration issues:

1. Review this guide
2. Check application logs for validation errors
3. Verify environment variable values
4. Consult [DEPLOYMENT.md](DEPLOYMENT.md) for deployment-specific configuration
5. Open a GitHub issue with configuration details (redact sensitive values)

## Version History

- **1.0.0** (2026-01-11): Initial configuration guide
