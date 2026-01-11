#!/usr/bin/env bash

# Code Quality Check Script
# Runs all code quality checks (linting, formatting, type checking)
# Exit code 0 = all checks passed, non-zero = at least one check failed

set -e  # Exit on first error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track overall status
OVERALL_STATUS=0

echo "========================================"
echo "Running Code Quality Checks"
echo "========================================"
echo ""

# Function to run a check and track status
run_check() {
    local check_name="$1"
    shift
    local check_cmd="$@"

    echo "----------------------------------------"
    echo "Running: $check_name"
    echo "Command: $check_cmd"
    echo "----------------------------------------"

    if eval "$check_cmd"; then
        echo -e "${GREEN}✓ $check_name passed${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}✗ $check_name failed${NC}"
        echo ""
        OVERALL_STATUS=1
        return 1
    fi
}

# 1. Check code formatting with black
run_check "Black (Code Formatter)" \
    "black --check --diff app/ tests/" || true

# 2. Check import sorting with isort
run_check "Isort (Import Sorter)" \
    "isort --check-only --diff app/ tests/" || true

# 3. Run ruff linter
run_check "Ruff (Linter)" \
    "ruff check app/ tests/" || true

# 4. Run mypy type checker (warnings only for MVP)
echo "----------------------------------------"
echo "Running: Mypy (Type Checker) [WARNINGS ONLY - NOT BLOCKING]"
echo "Command: mypy app/"
echo "----------------------------------------"

if mypy app/; then
    echo -e "${GREEN}✓ Mypy (Type Checker) passed${NC}"
else
    echo -e "${YELLOW}⚠ Mypy found type issues (not blocking for MVP)${NC}"
fi
echo ""

# Print summary
echo "========================================"
if [ $OVERALL_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ All quality checks passed!${NC}"
else
    echo -e "${RED}✗ Some quality checks failed${NC}"
    echo ""
    echo "To fix formatting issues, run:"
    echo "  make format"
    echo ""
    echo "To see detailed errors, run each tool individually:"
    echo "  black --check --diff app/ tests/"
    echo "  isort --check-only --diff app/ tests/"
    echo "  ruff check app/ tests/"
    echo "  mypy app/"
fi
echo "========================================"

exit $OVERALL_STATUS
