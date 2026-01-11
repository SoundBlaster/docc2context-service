#!/usr/bin/env bash

# Development Environment Setup Script
# Sets up a clean development environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Development Environment Setup${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check Python version
echo -e "${BLUE}Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    echo -e "${YELLOW}Please install Python 3.10 or later${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}\n"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}\n"
else
    echo -e "${YELLOW}⚠ Virtual environment already exists${NC}\n"
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}\n"

# Upgrade pip
echo -e "${BLUE}Upgrading pip...${NC}"
python -m pip install --upgrade pip -q
echo -e "${GREEN}✓ pip upgraded${NC}\n"

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install -r requirements.txt -q
echo -e "${GREEN}✓ Production dependencies installed${NC}\n"

echo -e "${BLUE}Installing development dependencies...${NC}"
pip install -r requirements-dev.txt -q
echo -e "${GREEN}✓ Development dependencies installed${NC}\n"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${BLUE}Creating .env file from template...${NC}"
    cp .env.development .env
    echo -e "${GREEN}✓ .env file created from .env.development${NC}\n"
else
    echo -e "${YELLOW}⚠ .env file already exists (not overwriting)${NC}\n"
fi

# Install pre-commit hooks
echo -e "${BLUE}Installing pre-commit hooks...${NC}"
if command -v pre-commit &> /dev/null; then
    pre-commit install
    echo -e "${GREEN}✓ Pre-commit hooks installed${NC}\n"
else
    echo -e "${YELLOW}⚠ pre-commit not found, skipping hooks installation${NC}\n"
fi

# Validate environment
echo -e "${BLUE}Validating environment...${NC}"
if python scripts/check_env.py --env development; then
    echo -e "${GREEN}✓ Environment validation passed${NC}\n"
else
    echo -e "${YELLOW}⚠ Environment validation found issues${NC}\n"
fi

# Print summary
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Development environment setup complete!${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo -e "Next steps:"
echo -e "  1. Activate the virtual environment:"
echo -e "     ${YELLOW}source venv/bin/activate${NC}"
echo -e ""
echo -e "  2. Review and customize .env file:"
echo -e "     ${YELLOW}nano .env${NC}"
echo -e ""
echo -e "  3. Run the application:"
echo -e "     ${YELLOW}make run${NC}"
echo -e ""
echo -e "  4. Run tests:"
echo -e "     ${YELLOW}make test${NC}"
echo -e ""
echo -e "  5. Check code quality:"
echo -e "     ${YELLOW}make quality-check${NC}"
echo -e ""
