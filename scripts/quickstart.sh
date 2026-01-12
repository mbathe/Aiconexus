#!/bin/bash

# AIConexus Quick Start Script
# Use this to quickly set up and test the gateway locally

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC} $1"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    echo -e "${GREEN}→${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

check_requirements() {
    print_header "Checking Requirements"
    
    print_step "Checking Python..."
    if command -v python3 &> /dev/null; then
        python3 --version
    else
        echo -e "${RED}✗ Python 3 not found${NC}"
        exit 1
    fi
    
    print_step "Checking Poetry..."
    if command -v poetry &> /dev/null; then
        poetry --version
    else
        print_warning "Poetry not found. Install: pip install poetry"
        exit 1
    fi
    
    print_step "Checking Docker (optional)..."
    if command -v docker &> /dev/null; then
        docker --version
        print_step "Docker is available ✓"
    else
        print_warning "Docker not installed. Docker features will be unavailable."
    fi
    
    print_step "Checking Docker Compose (optional)..."
    if command -v docker-compose &> /dev/null; then
        docker-compose --version
        print_step "Docker Compose is available ✓"
    else
        print_warning "Docker Compose not installed. Docker features will be unavailable."
    fi
}

verify_setup() {
    print_header "Verifying Setup"
    
    if [ -f "verify_docker_setup.sh" ]; then
        chmod +x verify_docker_setup.sh
        ./verify_docker_setup.sh
    else
        print_warning "verify_docker_setup.sh not found"
    fi
}

install_dependencies() {
    print_header "Installing Dependencies"
    
    print_step "Installing Python dependencies..."
    poetry install
    print_step "Done ✓"
}

show_quick_commands() {
    print_header "Quick Commands Reference"
    
    echo "Development:"
    echo "  poetry shell              # Activate virtual environment"
    echo "  poetry run pytest tests/   # Run all tests"
    echo ""
    
    echo "Gateway Management:"
    echo "  make gateway-build        # Build Docker image"
    echo "  make gateway-start        # Start gateway container"
    echo "  make gateway-stop         # Stop gateway container"
    echo "  make gateway-status       # Check gateway status"
    echo "  make gateway-logs         # View gateway logs"
    echo "  make gateway-health       # Check health endpoint"
    echo ""
    
    echo "Testing:"
    echo "  make test                 # Run all tests"
    echo "  make gateway-test         # Test Docker deployment"
    echo ""
    
    echo "Information:"
    echo "  cat DOCKER_GATEWAY.md     # Deployment guide"
    echo "  cat SDK_USAGE.md          # SDK usage guide"
    echo "  cat SPRINT5_SUMMARY.md    # Sprint summary"
}

show_next_steps() {
    print_header "Next Steps"
    
    echo "1. Verify Docker setup:"
    echo "   make gateway-verify"
    echo ""
    
    echo "2. Build Docker image (requires Docker):"
    echo "   make gateway-build"
    echo ""
    
    echo "3. Start gateway:"
    echo "   make gateway-start"
    echo ""
    
    echo "4. Check gateway status:"
    echo "   make gateway-status"
    echo ""
    
    echo "5. View logs:"
    echo "   make gateway-logs"
    echo ""
    
    echo "6. Test connectivity:"
    echo "   poetry run python test_two_clients.py"
    echo ""
    
    echo "7. Stop gateway:"
    echo "   make gateway-stop"
    echo ""
    
    echo -e "${GREEN}Setup complete! You're ready to use AIConexus.${NC}"
}

main() {
    clear
    
    print_header "AIConexus Quick Start"
    
    print_info "This script sets up your development environment"
    echo ""
    
    # Run checks
    check_requirements
    echo ""
    
    # Verify setup
    verify_setup
    echo ""
    
    # Install dependencies
    read -p "Install dependencies? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_dependencies
    fi
    echo ""
    
    # Show quick commands
    show_quick_commands
    echo ""
    
    # Show next steps
    show_next_steps
}

main "$@"
