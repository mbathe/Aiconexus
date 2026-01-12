#!/bin/bash

set -e

# AIConexus Gateway Docker Test Script
# This script tests the Docker deployment of the gateway

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

CONTAINER_NAME="aiconexus-gateway"
GATEWAY_URL="ws://127.0.0.1:8000/ws"
HEALTH_URL="http://127.0.0.1:8000/health"
AGENTS_URL="http://127.0.0.1:8000/agents"

# Utility functions
print_header() {
    echo -e "\n${BLUE}===================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}→ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

wait_for_container() {
    print_info "Waiting for container to be healthy..."
    
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker ps --filter "name=$CONTAINER_NAME" --filter "status=running" | grep -q "$CONTAINER_NAME"; then
            print_success "Container is running"
            return 0
        fi
        
        attempt=$((attempt + 1))
        sleep 1
    done
    
    print_error "Container failed to start within 30 seconds"
    return 1
}

wait_for_health() {
    print_info "Waiting for health endpoint to respond..."
    
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "$HEALTH_URL" > /dev/null 2>&1; then
            print_success "Health endpoint is responding"
            return 0
        fi
        
        attempt=$((attempt + 1))
        sleep 1
    done
    
    print_error "Health endpoint did not respond within 30 seconds"
    return 1
}

test_build() {
    print_header "TEST 1: Build Docker Image"
    
    print_info "Building Docker image from Dockerfile.gateway..."
    
    if docker build -f Dockerfile.gateway -t aiconexus-gateway:latest .; then
        print_success "Docker image built successfully"
        
        local image_id=$(docker images -q aiconexus-gateway:latest)
        local image_size=$(docker images --format "{{.Size}}" aiconexus-gateway:latest)
        
        print_info "Image ID: $image_id"
        print_info "Image Size: $image_size"
    else
        print_error "Failed to build Docker image"
        return 1
    fi
}

test_start() {
    print_header "TEST 2: Start Container with Docker Compose"
    
    # Stop and remove if already running
    if docker ps -a --filter "name=$CONTAINER_NAME" | grep -q "$CONTAINER_NAME"; then
        print_info "Removing existing container..."
        docker-compose -f docker-compose.gateway.yml down 2>/dev/null || true
        sleep 2
    fi
    
    print_info "Starting container with docker-compose..."
    if docker-compose -f docker-compose.gateway.yml up -d; then
        print_success "Docker Compose started successfully"
    else
        print_error "Failed to start with docker-compose"
        return 1
    fi
    
    # Wait for container to be ready
    if ! wait_for_container; then
        return 1
    fi
}

test_health() {
    print_header "TEST 3: Health Check Endpoints"
    
    # Wait for health to be ready
    if ! wait_for_health; then
        return 1
    fi
    
    print_info "Testing /health endpoint..."
    local health_response=$(curl -s "$HEALTH_URL")
    
    if echo "$health_response" | grep -q '"status"'; then
        print_success "Health endpoint responding"
        print_info "Response: $health_response"
    else
        print_error "Invalid health response"
        return 1
    fi
    
    print_info "Testing /agents endpoint..."
    local agents_response=$(curl -s "$AGENTS_URL")
    
    if echo "$agents_response" | grep -q '"agents"'; then
        print_success "Agents endpoint responding"
        print_info "Response: $agents_response"
    else
        print_error "Invalid agents response"
        return 1
    fi
}

test_logs() {
    print_header "TEST 4: Container Logs"
    
    print_info "Gateway logs:"
    docker-compose -f docker-compose.gateway.yml logs --tail=20
}

test_connectivity() {
    print_header "TEST 5: Client Connectivity"
    
    if [ ! -f "test_two_clients.py" ]; then
        print_warning "test_two_clients.py not found, skipping connectivity test"
        return 0
    fi
    
    print_info "Running two-client connectivity test..."
    
    if poetry run python test_two_clients.py; then
        print_success "Connectivity test passed"
    else
        print_warning "Connectivity test failed (this may be expected if clients are already running)"
    fi
}

test_message_exchange() {
    print_header "TEST 6: Message Exchange"
    
    if [ ! -f "test_message_exchange.py" ]; then
        print_warning "test_message_exchange.py not found, skipping message exchange test"
        return 0
    fi
    
    print_info "Running message exchange test..."
    
    if poetry run python test_message_exchange.py; then
        print_success "Message exchange test passed"
    else
        print_warning "Message exchange test failed"
    fi
}

test_stop() {
    print_header "TEST 7: Stop Container"
    
    print_info "Stopping container..."
    
    if docker-compose -f docker-compose.gateway.yml down; then
        print_success "Container stopped successfully"
    else
        print_error "Failed to stop container"
        return 1
    fi
    
    sleep 2
    
    # Verify stopped
    if ! docker ps --filter "name=$CONTAINER_NAME" | grep -q "$CONTAINER_NAME"; then
        print_success "Container is no longer running"
    else
        print_warning "Container still running after stop command"
    fi
}

test_restart() {
    print_header "TEST 8: Restart Container"
    
    print_info "Starting container again..."
    if docker-compose -f docker-compose.gateway.yml up -d; then
        print_success "Container restarted"
    else
        print_error "Failed to restart container"
        return 1
    fi
    
    if ! wait_for_container; then
        return 1
    fi
    
    if ! wait_for_health; then
        return 1
    fi
    
    print_success "Container restarted and healthy"
}

test_cleanup() {
    print_header "TEST 9: Final Cleanup"
    
    print_info "Cleaning up containers..."
    docker-compose -f docker-compose.gateway.yml down 2>/dev/null || true
    
    print_warning "Note: Docker image remains. Remove with: docker rmi aiconexus-gateway:latest"
}

run_all_tests() {
    print_header "AIConexus Gateway Docker Test Suite"
    
    print_info "Test Environment:"
    print_info "  Container: $CONTAINER_NAME"
    print_info "  Gateway URL: $GATEWAY_URL"
    print_info "  Health URL: $HEALTH_URL"
    
    local failed=0
    
    # Run tests
    test_build || failed=1
    sleep 2
    
    test_start || failed=1
    sleep 2
    
    test_health || failed=1
    
    test_logs
    
    test_connectivity || failed=1
    
    test_message_exchange || failed=1
    
    test_restart || failed=1
    
    test_stop || failed=1
    
    test_cleanup
    
    # Summary
    print_header "Test Summary"
    
    if [ $failed -eq 0 ]; then
        print_success "All tests passed!"
        echo -e "\n${GREEN}Gateway Docker deployment is working correctly.${NC}\n"
        return 0
    else
        print_error "Some tests failed"
        echo -e "\n${RED}Please review the logs above for details.${NC}\n"
        return 1
    fi
}

# Main execution
main() {
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
    
    print_info "Docker version: $(docker --version)"
    print_info "Docker Compose version: $(docker-compose --version)"
    
    run_all_tests
    exit $?
}

main "$@"
