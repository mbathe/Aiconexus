#!/bin/bash
# Complete AIConexus testing suite

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         AIConexus - Complete Testing Suite                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}[1/4]${NC} Running unit tests..."
poetry run pytest tests/unit/ -q --tb=short
if [ $? -ne 0 ]; then
    echo "❌ Unit tests failed!"
    exit 1
fi
echo -e "${GREEN}✅ All unit tests passed!${NC}\n"

echo -e "${BLUE}[2/4]${NC} Running load tests..."
poetry run pytest tests/load/test_load.py -v --tb=short
if [ $? -ne 0 ]; then
    echo "❌ Load tests failed!"
    exit 1
fi
echo -e "${GREEN}✅ All load tests passed!${NC}\n"

echo -e "${BLUE}[3/4]${NC} Starting gateway server..."
(poetry run uvicorn gateway_app:app --host 127.0.0.1 --port 8000 2>&1 &) &
GATEWAY_PID=$!
sleep 4

echo -e "${BLUE}[4/4]${NC} Running integration tests..."
echo ""
echo "  Test 1: Two-client connectivity..."
poetry run python test_two_clients.py > /tmp/test1.log 2>&1
if grep -q "Both clients connected successfully" /tmp/test1.log; then
    echo "  ✅ Two-client connectivity test PASSED"
else
    echo "  ❌ Two-client connectivity test FAILED"
    pkill -f "uvicorn gateway_app"
    exit 1
fi

echo ""
echo "  Test 2: Message exchange..."
poetry run python test_message_exchange.py > /tmp/test2.log 2>&1
if grep -q "Two-way message exchange SUCCESSFUL" /tmp/test2.log; then
    echo "  ✅ Message exchange test PASSED"
else
    echo "  ❌ Message exchange test FAILED"
    pkill -f "uvicorn gateway_app"
    exit 1
fi

# Cleanup
sleep 1
pkill -f "uvicorn gateway_app" 2>/dev/null || true

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  ✅ ALL TESTS PASSED! 🎉                      ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  • Unit Tests: PASSED                                        ║"
echo "║  • Load Tests: PASSED                                        ║"
echo "║  • Server Connectivity: PASSED                               ║"
echo "║  • Message Routing: PASSED                                   ║"
echo "║                                                              ║"
echo "║  Platform is production-ready! 🚀                            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
