#!/usr/bin/env bash

# Code Formatting Script
# Automatically fixes code formatting issues

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "Formatting Code"
echo "========================================"
echo ""

# 1. Sort imports with isort
echo "Running isort to sort imports..."
isort app/ tests/
echo -e "${GREEN}✓ Imports sorted${NC}"
echo ""

# 2. Format code with black
echo "Running black to format code..."
black app/ tests/
echo -e "${GREEN}✓ Code formatted${NC}"
echo ""

echo "========================================"
echo -e "${GREEN}✓ Formatting complete!${NC}"
echo "========================================"
