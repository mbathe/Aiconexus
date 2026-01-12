#!/bin/bash
# Script élégant pour tester le SDK AIConexus

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        AIConexus SDK - Elegant Test Suite Runner              ║"
echo "╚════════════════════════════════════════════════════════════════╝"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonctions utilitaires
print_status() {
    echo -e "${BLUE}➜${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_section() {
    echo ""
    echo -e "${YELLOW}═══ $1 ═══${NC}"
    echo ""
}

# Vérifier les dépendances
print_section "Checking Dependencies"

if ! command -v python &> /dev/null; then
    print_error "Python not found"
    exit 1
fi
print_success "Python found: $(python --version)"

if ! python -c "import pytest" 2>/dev/null; then
    print_error "pytest not installed"
    echo "  Run: pip install -r requirements-test.txt"
    exit 1
fi
print_success "pytest is installed"

# Configuration
COVERAGE_THRESHOLD=80
TEST_TIMEOUT=300

# Options par défaut
TEST_TYPE="all"
VERBOSE="-v"
SHOW_COVERAGE=false
MARKERS=""

# Parser les arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --unit)
            TEST_TYPE="unit"
            MARKERS="-m unit"
            shift
            ;;
        --integration)
            TEST_TYPE="integration"
            MARKERS="-m integration"
            shift
            ;;
        --performance)
            TEST_TYPE="performance"
            MARKERS="-m performance"
            shift
            ;;
        --coverage)
            SHOW_COVERAGE=true
            shift
            ;;
        --quiet)
            VERBOSE="-q"
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --unit           Run unit tests only"
            echo "  --integration    Run integration tests only"
            echo "  --performance    Run performance tests only"
            echo "  --coverage       Show code coverage report"
            echo "  --quiet          Minimal output"
            echo "  --help           Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Déterminer le type de test
if [ "$TEST_TYPE" = "all" ]; then
    TEST_PATTERN="tests/sdk/"
    print_status "Running ALL tests"
elif [ "$TEST_TYPE" = "unit" ]; then
    TEST_PATTERN="tests/sdk/"
    print_status "Running UNIT tests"
elif [ "$TEST_TYPE" = "integration" ]; then
    TEST_PATTERN="tests/integration/"
    print_status "Running INTEGRATION tests"
elif [ "$TEST_TYPE" = "performance" ]; then
    TEST_PATTERN="tests/performance/"
    print_status "Running PERFORMANCE tests"
fi

# Lancer les tests
print_section "Running Tests (Type: $TEST_TYPE)"

if [ "$SHOW_COVERAGE" = true ]; then
    print_status "Testing with coverage analysis..."
    python -m pytest \
        $VERBOSE \
        $TEST_PATTERN \
        --timeout=$TEST_TIMEOUT \
        --cov=src/aiconexus/sdk \
        --cov-report=term-missing \
        --cov-report=html:htmlcov \
        --cov-fail-under=$COVERAGE_THRESHOLD \
        $MARKERS
else
    print_status "Running tests..."
    python -m pytest \
        $VERBOSE \
        $TEST_PATTERN \
        --timeout=$TEST_TIMEOUT \
        $MARKERS
fi

TEST_RESULT=$?

# Afficher les résultats
print_section "Test Results"

if [ $TEST_RESULT -eq 0 ]; then
    print_success "All tests passed!"
    
    if [ "$SHOW_COVERAGE" = true ]; then
        print_success "Coverage report generated in: htmlcov/index.html"
    fi
else
    print_error "Some tests failed (exit code: $TEST_RESULT)"
    exit $TEST_RESULT
fi

# Afficher les statistiques
print_section "Test Statistics"

# Compter les fichiers de test
UNIT_TESTS=$(find tests/sdk -name "test_*.py" | wc -l)
INTEGRATION_TESTS=$(find tests/integration -name "test_*.py" 2>/dev/null | wc -l)
PERFORMANCE_TESTS=$(find tests/performance -name "test_*.py" 2>/dev/null | wc -l)

echo "Unit tests: $UNIT_TESTS files"
echo "Integration tests: $INTEGRATION_TESTS files"
echo "Performance tests: $PERFORMANCE_TESTS files"

# Afficher les prochaines étapes
print_section "Next Steps"

if [ "$SHOW_COVERAGE" = true ]; then
    echo "1. View coverage report:"
    echo "   open htmlcov/index.html"
else
    echo "1. Run with coverage:"
    echo "   ./scripts/run_tests.sh --coverage"
fi

echo "2. Run specific test types:"
echo "   ./scripts/run_tests.sh --unit"
echo "   ./scripts/run_tests.sh --integration"
echo "   ./scripts/run_tests.sh --performance"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║             All tests completed successfully! ✓                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
