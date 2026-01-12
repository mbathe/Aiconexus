#!/bin/bash

# AIConexus Git Commit Script
# Use this to commit all Sprint 5 Phase 4 changes

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

print_section() {
    echo -e "${BLUE}→ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

main() {
    print_header "AIConexus Sprint 5 Phase 4 - Git Commit Helper"
    
    echo "This script will help you commit the Docker deployment changes."
    echo ""
    
    # Check git
    if ! command -v git &> /dev/null; then
        echo -e "${RED}✗ Git is not installed${NC}"
        exit 1
    fi
    
    print_section "Current Git Status:"
    git status --short | head -20
    echo ""
    
    # Show changes summary
    print_section "Summary of Changes:"
    echo "Files Created:"
    echo "  • Docker Infrastructure: Dockerfile.gateway, docker-compose.gateway.yml"
    echo "  • Management Scripts: gateway-docker.sh, test_docker_gateway.sh"
    echo "  • Verification Scripts: verify_docker_setup.sh, quickstart.sh"
    echo "  • Configuration: .env.gateway.example"
    echo "  • Documentation: DOCKER_GATEWAY.md, SDK_USAGE.md, SPRINT5_SUMMARY.md"
    echo "  • Additional: DOCUMENTATION_INDEX.md, COMMIT_GUIDE.md, SPRINT5_RESUME_FR.md"
    echo ""
    echo "Files Modified:"
    echo "  • Makefile (added 10 gateway commands)"
    echo ""
    
    # Ask for confirmation
    read -p "Proceed with git commit? (y/n) " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
    
    print_section "Staging all changes..."
    git add -A
    print_success "Files staged"
    echo ""
    
    # Show what will be committed
    print_section "Files to be committed:"
    git diff --cached --name-only
    echo ""
    
    # Commit message
    COMMIT_MSG="feat: Add Docker deployment for Gateway service

- Separate Gateway as standalone Docker service
- Add Dockerfile.gateway with multi-stage build
- Add docker-compose.gateway.yml for orchestration
- Add gateway-docker.sh management script (10 commands)
- Add test_docker_gateway.sh for deployment testing
- Add DOCKER_GATEWAY.md deployment guide
- Add SDK_USAGE.md SDK usage guide
- Add .env.gateway.example configuration template
- Add verify_docker_setup.sh setup verification
- Add quickstart.sh interactive setup script
- Add SPRINT5_SUMMARY.md sprint summary
- Add DOCUMENTATION_INDEX.md documentation index
- Add SPRINT5_RESUME_FR.md French summary
- Update Makefile with gateway commands (10 new targets)

Features:
- Multi-stage Docker build for optimization
- Health checks with HTTP endpoints
- Auto-restart policy for reliability
- Non-root execution for security
- Complete lifecycle management (build/start/stop/logs)
- Comprehensive test suite for deployment
- Production-ready configuration

Architecture:
- Gateway: Standalone backend service (Docker)
- SDK: Pure client library (pip installable)
- Communication: WebSocket (ws://gateway:8000/ws)
- Deployment: Docker Compose with auto-scaling support

Documentation:
- DOCKER_GATEWAY.md: 450+ line deployment guide
- SDK_USAGE.md: 500+ line usage guide
- SPRINT5_SUMMARY.md: 600+ line completion summary
- DOCUMENTATION_INDEX.md: 400+ line documentation index
- SPRINT5_RESUME_FR.md: French language summary

Testing:
- Automatic deployment tests (9 test scenarios)
- Health endpoint validation
- Connectivity tests with real agents
- Resource cleanup verification

BREAKING CHANGE: Gateway now deployed as separate service

Closes #NNN (if applicable)"
    
    echo -e "${YELLOW}Commit message:${NC}"
    echo "─────────────────────────────────────────────────────────────"
    echo "$COMMIT_MSG"
    echo "─────────────────────────────────────────────────────────────"
    echo ""
    
    read -p "Confirm commit? (y/n) " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        git reset
        exit 0
    fi
    
    # Perform commit
    print_section "Creating commit..."
    git commit -m "$COMMIT_MSG"
    print_success "Commit created!"
    echo ""
    
    # Show commit info
    print_section "Commit Details:"
    git log -1 --oneline
    echo ""
    
    # Suggest next steps
    print_section "Next Steps:"
    echo "1. Review the commit:"
    echo "   git show"
    echo ""
    echo "2. Push to remote:"
    echo "   git push origin main"
    echo ""
    echo "3. Verify deployment:"
    echo "   ./verify_docker_setup.sh"
    echo ""
    echo "4. Build Docker image:"
    echo "   ./gateway-docker.sh build"
    echo ""
    echo "5. Start gateway:"
    echo "   ./gateway-docker.sh start"
    echo ""
    
    print_success "Git commit complete!"
}

main "$@"
