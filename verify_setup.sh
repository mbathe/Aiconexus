#!/bin/bash
# AIConexus Setup Verification Script

echo "AIConexus Project Verification"
echo "=============================="
echo ""

# Count files
echo "Project Statistics:"
echo "  Source files: $(find src -type f -name '*.py' | wc -l)"
echo "  Test files: $(find tests -type f -name '*.py' | wc -l)"
echo "  Documentation: $(ls -1 *.md 2>/dev/null | wc -l) files"
echo ""

# Check key files
echo "Checking core files:"
files_to_check=(
    "pyproject.toml"
    "README.md"
    "SPECIFICATIONS.md"
    "ARCHITECTURE.md"
    "CONTRIBUTING.md"
    "Makefile"
    ".env.example"
    ".gitignore"
    "src/aiconexus/__init__.py"
    "src/aiconexus/config.py"
    "src/aiconexus/types.py"
    "src/aiconexus/exceptions.py"
    "src/aiconexus/core/agent.py"
    "tests/conftest.py"
)

for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        echo "  [OK] $file"
    else
        echo "  [FAIL] $file MISSING"
    fi
done

echo ""
echo "Checking modules:"
modules=(
    "core"
    "protocol"
    "discovery"
    "negotiation"
    "execution"
    "economics"
    "security"
    "marketplace"
    "monitoring"
    "storage"
    "api"
    "sdk"
    "utils"
)

for module in "${modules[@]}"; do
    if [ -d "src/aiconexus/$module" ] && [ -f "src/aiconexus/$module/__init__.py" ]; then
        echo "  [OK] $module/"
    else
        echo "  [FAIL] $module/ INCOMPLETE"
    fi
done

echo ""
echo "Checking test structure:"
test_dirs=("unit" "integration" "e2e" "load")
for dir in "${test_dirs[@]}"; do
    if [ -d "tests/$dir" ]; then
        echo "  [OK] tests/$dir/"
    else
        echo "  [FAIL] tests/$dir/ MISSING"
    fi
done

echo ""
echo "Checking scripts:"
scripts=("setup_dev_env.sh" "run_tests.sh" "format_code.sh")
for script in "${scripts[@]}"; do
    if [ -f "scripts/$script" ]; then
        echo "  [OK] $script"
    else
        echo "  [FAIL] $script MISSING"
    fi
done

echo ""
echo "Checking examples:"
if [ -d "examples/hello_world" ] && [ -f "examples/hello_world/agent.py" ]; then
    echo "  [OK] hello_world example"
else
    echo "  [FAIL] hello_world example INCOMPLETE"
fi

echo ""
echo "Configuration:"
if [ -f ".env.example" ]; then
    echo "  [OK] Environment template (.env.example)"
    echo "       Configured settings: $(grep -c '^[A-Z]' .env.example)"
else
    echo "  [FAIL] .env.example MISSING"
fi

echo ""
echo "Next Steps:"
echo "  1. Setup development environment: bash scripts/setup_dev_env.sh"
echo "  2. Install dependencies: poetry install"
echo "  3. Run tests: make test"
echo "  4. Run hello world: make example-hello"
echo "  5. View help: make help"
echo ""
echo "Documentation:"
echo "  - Quick Start: README.md"
echo "  - Specifications: SPECIFICATIONS.md"
echo "  - Architecture: ARCHITECTURE.md"
echo "  - Contributing: CONTRIBUTING.md"
echo ""
echo "Project setup is complete!"
