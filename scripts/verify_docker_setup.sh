#!/bin/bash

# Quick verification script for AIConexus Docker deployment setup

echo "Checking Docker deployment files..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
    else
        echo -e "${RED}✗${NC} $1 (missing)"
    fi
}

# Check gateway Docker files
echo "Gateway Docker Files:"
check_file "Dockerfile.gateway"
check_file "docker-compose.gateway.yml"
check_file "gateway-docker.sh"
check_file "test_docker_gateway.sh"
check_file ".dockerignore"
echo ""

# Check configuration files
echo "Configuration Files:"
check_file ".env.gateway.example"
echo ""

# Check documentation
echo "Documentation Files:"
check_file "DOCKER_GATEWAY.md"
check_file "SDK_USAGE.md"
check_file "README.md"
check_file "ARCHITECTURE.md"
echo ""

# Check script permissions
echo "Script Permissions:"
if [ -x "gateway-docker.sh" ]; then
    echo -e "${GREEN}✓${NC} gateway-docker.sh is executable"
else
    echo -e "${RED}✗${NC} gateway-docker.sh is not executable"
fi

if [ -x "test_docker_gateway.sh" ]; then
    echo -e "${GREEN}✓${NC} test_docker_gateway.sh is executable"
else
    echo -e "${RED}✗${NC} test_docker_gateway.sh is not executable"
fi
echo ""

# Check Docker installation
echo "Docker Environment:"
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker is installed"
    docker --version
else
    echo -e "${RED}✗${NC} Docker is not installed"
fi
echo ""

if command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker Compose is installed"
    docker-compose --version
else
    echo -e "${RED}✗${NC} Docker Compose is not installed"
fi
echo ""

# Summary
echo "=== Setup Summary ==="
echo ""
echo "Gateway Docker deployment is configured."
echo ""
echo "Next steps:"
echo "1. Build Docker image:"
echo "   ./gateway-docker.sh build"
echo ""
echo "2. Start gateway:"
echo "   ./gateway-docker.sh start"
echo ""
echo "3. Check status:"
echo "   ./gateway-docker.sh status"
echo ""
echo "4. View logs:"
echo "   ./gateway-docker.sh logs -f"
echo ""
echo "For full documentation, see:"
echo "  - DOCKER_GATEWAY.md (deployment guide)"
echo "  - SDK_USAGE.md (SDK usage guide)"
echo ""
