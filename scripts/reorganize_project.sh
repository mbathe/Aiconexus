#!/bin/bash

# AIConexus Project Reorganization Script
# This script organizes files into proper directory structure

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
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

# Create directories
create_dirs() {
    print_step "Creating directory structure..."
    
    mkdir -p docs/deployment
    mkdir -p docs/guides
    mkdir -p docs/api
    mkdir -p docs/sprints
    
    mkdir -p gateway/src
    mkdir -p gateway/docker
    
    mkdir -p src/sdk
    mkdir -p src/aiconexus
    
    mkdir -p scripts/tests
    
    mkdir -p examples/agents
    mkdir -p examples/gateway
    
    mkdir -p tests/unit
    mkdir -p tests/integration
    mkdir -p tests/load
    
    mkdir -p config
    
    print_info "Directories created"
}

# Move documentation files
move_docs() {
    print_step "Moving documentation files..."
    
    # Main docs
    [ -f "QUICK_START.md" ] && mv QUICK_START.md docs/ && echo "  QUICK_START.md"
    [ -f "ARCHITECTURE.md" ] && mv ARCHITECTURE.md docs/ && echo "  ARCHITECTURE.md"
    [ -f "PROTOCOL_DESIGN.md" ] && mv PROTOCOL_DESIGN.md docs/ && echo "  PROTOCOL_DESIGN.md"
    [ -f "DOCUMENTATION_INDEX.md" ] && mv DOCUMENTATION_INDEX.md docs/ && echo "  DOCUMENTATION_INDEX.md"
    
    # Deployment docs
    [ -f "DOCKER_GATEWAY.md" ] && mv DOCKER_GATEWAY.md docs/deployment/ && echo "  DOCKER_GATEWAY.md → deployment/"
    [ -f "DOCKER.md" ] && mv DOCKER.md docs/deployment/ && echo "  DOCKER.md → deployment/"
    
    # Guides
    [ -f "SDK_USAGE.md" ] && mv SDK_USAGE.md docs/guides/ && echo "  SDK_USAGE.md → guides/"
    [ -f "TROUBLESHOOTING.md" ] && mv TROUBLESHOOTING.md docs/guides/ && echo "  TROUBLESHOOTING.md → guides/"
    
    # API docs
    [ -f "PROTOCOL_MESSAGES.md" ] && mv PROTOCOL_MESSAGES.md docs/api/ && echo "  PROTOCOL_MESSAGES.md → api/"
    
    # Sprint reports
    [ -f "SPRINT_1_REPORT.md" ] && mv SPRINT_1_REPORT.md docs/sprints/ && echo "  SPRINT_1_REPORT.md → sprints/"
    [ -f "SPRINT_2_REPORT.md" ] && mv SPRINT_2_REPORT.md docs/sprints/ && echo "  SPRINT_2_REPORT.md → sprints/"
    [ -f "SPRINT_3_REPORT.md" ] && mv SPRINT_3_REPORT.md docs/sprints/ && echo "  SPRINT_3_REPORT.md → sprints/"
    [ -f "SPRINT_4_REPORT.md" ] && mv SPRINT_4_REPORT.md docs/sprints/ && echo "  SPRINT_4_REPORT.md → sprints/"
    [ -f "SPRINT_5_REPORT.md" ] && mv SPRINT_5_REPORT.md docs/sprints/ && echo "  SPRINT_5_REPORT.md → sprints/"
    [ -f "SPRINT5_RESUME_FR.md" ] && mv SPRINT5_RESUME_FR.md docs/sprints/ && echo "  SPRINT5_RESUME_FR.md → sprints/"
    [ -f "SPRINT5_SUMMARY.md" ] && mv SPRINT5_SUMMARY.md docs/sprints/ && echo "  SPRINT5_SUMMARY.md → sprints/"
    [ -f "COMMIT_GUIDE.md" ] && mv COMMIT_GUIDE.md docs/sprints/ && echo "  COMMIT_GUIDE.md → sprints/"
    [ -f "PROJECT_STATUS_FINAL.md" ] && mv PROJECT_STATUS_FINAL.md docs/sprints/ && echo "  PROJECT_STATUS_FINAL.md → sprints/"
    [ -f "PROJECT_STATUS.md" ] && mv PROJECT_STATUS.md docs/sprints/ && echo "  PROJECT_STATUS.md → sprints/"
    [ -f "PROJECT_STRUCTURE.md" ] && mv PROJECT_STRUCTURE.md docs/ && echo "  PROJECT_STRUCTURE.md"
    [ -f "ROADMAP.md" ] && mv ROADMAP.md docs/ && echo "  ROADMAP.md"
    [ -f "SPECIFICATIONS.md" ] && mv SPECIFICATIONS.md docs/ && echo "  SPECIFICATIONS.md"
    
    print_info "Documentation moved"
}

# Move gateway files
move_gateway() {
    print_step "Moving gateway files..."
    
    # Gateway source code
    [ -f "gateway_app.py" ] && mv gateway_app.py gateway/src/ && echo "  gateway_app.py"
    [ -f "gateway_listen.py" ] && mv gateway_listen.py gateway/src/ && echo "  gateway_listen.py"
    
    # Gateway docker files
    [ -f "Dockerfile.gateway" ] && mv Dockerfile.gateway gateway/docker/Dockerfile && echo "  Dockerfile.gateway → docker/Dockerfile"
    [ -f "docker-compose.gateway.yml" ] && mv docker-compose.gateway.yml gateway/docker/docker-compose.yml && echo "  docker-compose.gateway.yml → docker/docker-compose.yml"
    
    # Gateway env
    [ -f ".env.gateway.example" ] && mv .env.gateway.example config/.env.gateway.example && echo "  .env.gateway.example → config/"
    
    print_info "Gateway files moved"
}

# Move scripts
move_scripts() {
    print_step "Moving scripts..."
    
    [ -f "gateway-docker.sh" ] && mv gateway-docker.sh scripts/ && echo "  gateway-docker.sh"
    [ -f "test-docker-gateway.sh" ] && [ -f "test_docker_gateway.sh" ] && mv test_docker_gateway.sh scripts/tests/ && echo "  test_docker_gateway.sh → tests/"
    [ -f "verify-docker-setup.sh" ] && [ -f "verify_docker_setup.sh" ] && mv verify_docker_setup.sh scripts/ && echo "  verify_docker_setup.sh"
    [ -f "quickstart.sh" ] && mv quickstart.sh scripts/ && echo "  quickstart.sh"
    [ -f "git-commit.sh" ] && [ -f "git_commit_sprint5.sh" ] && mv git_commit_sprint5.sh scripts/git-commit.sh && echo "  git_commit_sprint5.sh → git-commit.sh"
    [ -f "test-all-features.sh" ] && [ -f "test_all_features.sh" ] && mv test_all_features.sh scripts/tests/run-all-tests.sh && echo "  test_all_features.sh → tests/run-all-tests.sh"
    [ -f "verify-setup.sh" ] && [ -f "verify_setup.sh" ] && mv verify_setup.sh scripts/verify-legacy-setup.sh && echo "  verify_setup.sh → verify-legacy-setup.sh"
    
    print_info "Scripts moved"
}

# Move config files
move_config() {
    print_step "Moving configuration files..."
    
    [ -f ".env.example" ] && mv .env.example config/.env.example && echo "  .env.example"
    
    print_info "Configuration moved"
}

# Summary
show_summary() {
    print_header "Reorganization Complete!"
    
    echo "New structure:"
    echo "  docs/              - All documentation"
    echo "  gateway/           - Gateway service (separate)"
    echo "  src/               - Source code"
    echo "  scripts/           - Utility scripts"
    echo "  examples/          - Code examples"
    echo "  tests/             - Test suite"
    echo "  config/            - Configuration files"
    echo ""
    echo "Root directory now contains only:"
    echo "  - README.md"
    echo "  - LICENSE"
    echo "  - pyproject.toml"
    echo "  - Makefile"
    echo "  - CONTRIBUTING.md"
    echo "  - .gitignore"
    echo ""
}

# Confirmation
ask_confirmation() {
    echo -e "${YELLOW}This will reorganize your project structure.${NC}"
    echo "Files will be moved to:"
    echo "  - docs/      (all documentation)"
    echo "  - gateway/   (gateway service)"
    echo "  - scripts/   (shell scripts)"
    echo "  - config/    (configuration)"
    echo ""
    read -p "Continue? (y/n) " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
}

main() {
    print_header "AIConexus Project Reorganization"
    
    ask_confirmation
    
    create_dirs
    move_docs
    move_gateway
    move_scripts
    move_config
    
    show_summary
    
    print_step "Reorganization successful!"
    echo ""
    echo "Next steps:"
    echo "1. Update Makefile paths"
    echo "2. Update scripts to use new paths"
    echo "3. Update .gitignore"
    echo "4. Commit changes: git add . && git commit -m 'refactor: reorganize project structure'"
}

main "$@"
