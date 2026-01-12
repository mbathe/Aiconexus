#!/bin/bash

# AIConexus Gateway Docker Management Script
# This script manages the gateway container for easy deployment and testing

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Container and image names
CONTAINER_NAME="aiconexus-gateway"
IMAGE_NAME="aiconexus-gateway"
COMPOSE_FILE="docker-compose.gateway.yml"

# Functions
print_header() {
    echo ""
    echo "======================================================================"
    echo "$1"
    echo "======================================================================"
    echo ""
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
    print_success "Docker and Docker Compose are available"
}

# Build the gateway image
build_image() {
    print_header "Building AIConexus Gateway Docker Image"
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        print_error "File not found: $COMPOSE_FILE"
        exit 1
    fi
    
    print_info "Building from docker-compose configuration..."
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    
    print_success "Gateway image built successfully"
}

# Start the gateway
start_gateway() {
    print_header "Starting AIConexus Gateway Container"
    
    # Check if already running
    if docker ps | grep -q "$CONTAINER_NAME"; then
        print_warning "Gateway is already running"
        print_info "Container ID: $(docker ps | grep $CONTAINER_NAME | awk '{print $1}')"
        return 0
    fi
    
    print_info "Checking for stopped container..."
    if docker ps -a | grep -q "$CONTAINER_NAME"; then
        print_info "Found stopped container, removing it..."
        docker rm "$CONTAINER_NAME" -f
    fi
    
    print_info "Starting gateway container..."
    docker-compose -f "$COMPOSE_FILE" up -d
    
    # Wait for container to be healthy
    print_info "Waiting for gateway to be ready..."
    sleep 3
    
    # Check health
    if docker exec "$CONTAINER_NAME" python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" &> /dev/null; then
        print_success "Gateway is healthy and ready"
        print_info "Gateway is available at: ws://127.0.0.1:8000/ws"
        print_info "Health check: http://127.0.0.1:8000/health"
        print_info "Agent list: http://127.0.0.1:8000/agents"
    else
        print_warning "Gateway started but may not be fully ready yet"
        print_info "Check logs with: ./gateway-docker.sh logs"
    fi
}

# Stop the gateway
stop_gateway() {
    print_header "Stopping AIConexus Gateway Container"
    
    if ! docker ps | grep -q "$CONTAINER_NAME"; then
        print_warning "Gateway is not running"
        return 0
    fi
    
    print_info "Stopping container..."
    docker-compose -f "$COMPOSE_FILE" down
    
    print_success "Gateway stopped successfully"
}

# Restart the gateway
restart_gateway() {
    print_header "Restarting AIConexus Gateway Container"
    
    stop_gateway
    sleep 1
    start_gateway
}

# Show gateway status
show_status() {
    print_header "AIConexus Gateway Status"
    
    if docker ps | grep -q "$CONTAINER_NAME"; then
        print_success "Gateway is RUNNING"
        echo ""
        print_info "Container Details:"
        docker ps | grep "$CONTAINER_NAME"
        echo ""
        print_info "Container ID:"
        docker ps | grep "$CONTAINER_NAME" | awk '{print $1}'
    elif docker ps -a | grep -q "$CONTAINER_NAME"; then
        print_warning "Gateway is STOPPED"
        docker ps -a | grep "$CONTAINER_NAME"
    else
        print_warning "Gateway container not found"
    fi
}

# Show logs
show_logs() {
    print_header "AIConexus Gateway Logs"
    
    if ! docker ps -a | grep -q "$CONTAINER_NAME"; then
        print_error "Gateway container not found"
        exit 1
    fi
    
    print_info "Showing last 100 lines of logs (use -f for follow mode)..."
    docker-compose -f "$COMPOSE_FILE" logs -n 100 ${1:+-f}
}

# Remove everything
cleanup() {
    print_header "Cleaning Up AIConexus Gateway Docker Resources"
    
    print_warning "This will remove the container and image"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Removing container..."
        docker-compose -f "$COMPOSE_FILE" down -v 2>/dev/null || true
        
        print_info "Removing image..."
        docker rmi "$IMAGE_NAME" -f 2>/dev/null || true
        
        print_success "Cleanup completed"
    else
        print_info "Cleanup cancelled"
    fi
}

# Show help
show_help() {
    cat << 'EOF'
AIConexus Gateway Docker Management Script

Usage: ./gateway-docker.sh [COMMAND]

Commands:
    build       Build the Docker image for the gateway
    start       Start the gateway container in background
    stop        Stop the gateway container
    restart     Restart the gateway container
    status      Show gateway container status
    logs        Show gateway logs (add -f to follow)
    cleanup     Remove container and image
    shell       Open shell inside running container
    health      Check gateway health
    help        Show this help message

Examples:
    ./gateway-docker.sh build
    ./gateway-docker.sh start
    ./gateway-docker.sh logs -f
    ./gateway-docker.sh stop

Gateway will be available at:
    WebSocket: ws://127.0.0.1:8000/ws
    Health: http://127.0.0.1:8000/health
    Agents: http://127.0.0.1:8000/agents

EOF
}

# Shell access
shell_access() {
    print_header "Opening Shell in Gateway Container"
    
    if ! docker ps | grep -q "$CONTAINER_NAME"; then
        print_error "Gateway is not running"
        exit 1
    fi
    
    print_info "Connecting to container..."
    docker exec -it "$CONTAINER_NAME" /bin/bash
}

# Health check
health_check() {
    print_header "Checking Gateway Health"
    
    if ! docker ps | grep -q "$CONTAINER_NAME"; then
        print_error "Gateway is not running"
        exit 1
    fi
    
    print_info "Checking health endpoint..."
    if docker exec "$CONTAINER_NAME" python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" &> /dev/null; then
        print_success "Gateway is healthy"
        print_info "Fetching health status..."
        docker exec "$CONTAINER_NAME" python -c "
import urllib.request
import json
response = urllib.request.urlopen('http://localhost:8000/health')
data = json.loads(response.read())
print(json.dumps(data, indent=2))
"
    else
        print_error "Gateway health check failed"
        exit 1
    fi
}

# Main script logic
main() {
    case "${1:-help}" in
        build)
            check_docker
            build_image
            ;;
        start)
            check_docker
            start_gateway
            ;;
        stop)
            check_docker
            stop_gateway
            ;;
        restart)
            check_docker
            restart_gateway
            ;;
        status)
            check_docker
            show_status
            ;;
        logs)
            check_docker
            show_logs "${2:-}"
            ;;
        cleanup)
            check_docker
            cleanup
            ;;
        shell)
            check_docker
            shell_access
            ;;
        health)
            check_docker
            health_check
            ;;
        help)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
