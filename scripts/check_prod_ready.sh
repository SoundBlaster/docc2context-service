#!/usr/bin/env bash

# Production Readiness Check Script
# Validates that the environment is ready for production deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

OVERALL_STATUS=0

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Production Readiness Checks${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Function to run a check
run_check() {
    local check_name="$1"
    local check_cmd="$2"

    echo -e "${BLUE}Checking: $check_name${NC}"

    if eval "$check_cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $check_name${NC}\n"
        return 0
    else
        echo -e "${RED}✗ $check_name${NC}"
        echo -e "${YELLOW}Command: $check_cmd${NC}\n"
        OVERALL_STATUS=1
        return 1
    fi
}

# 1. Check environment is set to production
echo -e "${BLUE}=== Environment Configuration ===${NC}\n"

ENV_VAR=$(grep "^ENVIRONMENT=" .env 2>/dev/null | cut -d'=' -f2 || echo "")
if [ "$ENV_VAR" == "production" ]; then
    echo -e "${GREEN}✓ ENVIRONMENT=production${NC}\n"
else
    echo -e "${RED}✗ ENVIRONMENT is not set to 'production' (current: $ENV_VAR)${NC}\n"
    OVERALL_STATUS=1
fi

# 2. Run environment validation
echo -e "${BLUE}=== Environment Validation ===${NC}\n"
if python scripts/check_env.py --env production; then
    echo -e "${GREEN}✓ Environment validation passed${NC}\n"
else
    echo -e "${RED}✗ Environment validation failed${NC}\n"
    OVERALL_STATUS=1
fi

# 3. Check security settings
echo -e "${BLUE}=== Security Settings ===${NC}\n"

# Check CORS_ORIGINS
CORS=$(grep "^CORS_ORIGINS=" .env 2>/dev/null | cut -d'=' -f2 || echo "")
if [ "$CORS" == "*" ]; then
    echo -e "${RED}✗ CORS_ORIGINS=* is not allowed in production${NC}\n"
    OVERALL_STATUS=1
else
    echo -e "${GREEN}✓ CORS_ORIGINS is configured (not *)${NC}\n"
fi

# Check ALLOWED_HOSTS
HOSTS=$(grep "^ALLOWED_HOSTS=" .env 2>/dev/null | cut -d'=' -f2 || echo "")
if [ "$HOSTS" == "*" ]; then
    echo -e "${RED}✗ ALLOWED_HOSTS=* is not allowed in production${NC}\n"
    OVERALL_STATUS=1
else
    echo -e "${GREEN}✓ ALLOWED_HOSTS is configured (not *)${NC}\n"
fi

# Check LOG_LEVEL
LOG_LEVEL=$(grep "^LOG_LEVEL=" .env 2>/dev/null | cut -d'=' -f2 || echo "")
if [ "$LOG_LEVEL" == "DEBUG" ]; then
    echo -e "${YELLOW}⚠ LOG_LEVEL=DEBUG in production (performance impact)${NC}\n"
else
    echo -e "${GREEN}✓ LOG_LEVEL is not DEBUG${NC}\n"
fi

# 4. Check code quality
echo -e "${BLUE}=== Code Quality ===${NC}\n"
if ./scripts/check_quality.sh > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Code quality checks passed${NC}\n"
else
    echo -e "${RED}✗ Code quality checks failed${NC}\n"
    echo -e "${YELLOW}Run: make quality-check${NC}\n"
    OVERALL_STATUS=1
fi

# 5. Check tests
echo -e "${BLUE}=== Tests ===${NC}\n"
if python -m pytest -v --tb=short > /dev/null 2>&1; then
    echo -e "${GREEN}✓ All tests passed${NC}\n"
else
    echo -e "${RED}✗ Tests failed${NC}\n"
    echo -e "${YELLOW}Run: make test${NC}\n"
    OVERALL_STATUS=1
fi

# 6. Check Docker build
echo -e "${BLUE}=== Docker ===${NC}\n"
if command -v docker &> /dev/null; then
    if docker build -t docc2context-service:prod-test . > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Docker image builds successfully${NC}\n"
    else
        echo -e "${RED}✗ Docker build failed${NC}\n"
        echo -e "${YELLOW}Run: docker build -t docc2context-service .${NC}\n"
        OVERALL_STATUS=1
    fi
else
    echo -e "${YELLOW}⚠ Docker not found (skipping Docker checks)${NC}\n"
fi

# 7. Check workspace directory
echo -e "${BLUE}=== Workspace Directory ===${NC}\n"
WORKSPACE_PATH=$(grep "^WORKSPACE_BASE_PATH=" .env 2>/dev/null | cut -d'=' -f2 || echo "/tmp")
if [ -d "$WORKSPACE_PATH" ]; then
    echo -e "${GREEN}✓ Workspace directory exists: $WORKSPACE_PATH${NC}\n"
else
    echo -e "${RED}✗ Workspace directory does not exist: $WORKSPACE_PATH${NC}\n"
    echo -e "${YELLOW}Create it with: sudo mkdir -p $WORKSPACE_PATH && sudo chown \$USER:\$USER $WORKSPACE_PATH${NC}\n"
    OVERALL_STATUS=1
fi

# 8. Check Swift CLI
echo -e "${BLUE}=== Swift CLI ===${NC}\n"
SWIFT_CLI=$(grep "^SWIFT_CLI_PATH=" .env 2>/dev/null | cut -d'=' -f2 || echo "docc2context")
if command -v "$SWIFT_CLI" &> /dev/null; then
    echo -e "${GREEN}✓ Swift CLI found: $(which $SWIFT_CLI)${NC}\n"
else
    echo -e "${RED}✗ Swift CLI not found: $SWIFT_CLI${NC}\n"
    echo -e "${YELLOW}Install docc2context or update SWIFT_CLI_PATH${NC}\n"
    OVERALL_STATUS=1
fi

# Print summary
echo -e "${BLUE}========================================${NC}"
if [ $OVERALL_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ Production readiness checks passed!${NC}"
    echo -e "${BLUE}========================================${NC}\n"
    echo -e "${GREEN}The application is ready for production deployment.${NC}\n"
    echo -e "Next steps:"
    echo -e "  1. Review DOCS/DEPLOYMENT.md for deployment instructions"
    echo -e "  2. Build Docker image: ${YELLOW}make build-docker${NC}"
    echo -e "  3. Deploy using your preferred method"
    echo -e ""
else
    echo -e "${RED}✗ Production readiness checks failed${NC}"
    echo -e "${BLUE}========================================${NC}\n"
    echo -e "${RED}The application is NOT ready for production deployment.${NC}\n"
    echo -e "Please fix the issues above before deploying to production.\n"
fi

exit $OVERALL_STATUS
