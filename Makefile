.PHONY: help install test lint format clean run docs

help:
	@echo "AIConexus Development Commands"
	@echo "=============================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install       Install dependencies"
	@echo "  make dev-install   Install with dev dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test          Run all tests"
	@echo "  make test-unit     Run unit tests only"
	@echo "  make test-cov      Run tests with coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint          Run linting checks"
	@echo "  make format        Format code (black, isort)"
	@echo "  make type-check    Run type checking with mypy"
	@echo ""
	@echo "Running:"
	@echo "  make run           Run the API server"
	@echo "  make dev           Run in development mode (with reload)"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs          Build documentation"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean         Remove build artifacts"
	@echo "  make shell         Open poetry shell"
	@echo ""

install:
	poetry install

dev-install:
	poetry install --with dev

test:
	poetry run pytest -v

test-unit:
	poetry run pytest tests/unit/ -v

test-integration:
	poetry run pytest tests/integration/ -v

test-e2e:
	poetry run pytest tests/e2e/ -v

test-cov:
	poetry run pytest --cov=src/aiconexus --cov-report=html --cov-report=term-missing -v
	@echo "Coverage report: htmlcov/index.html"

lint:
	poetry run ruff check src tests examples

format:
	poetry run black src tests examples
	poetry run isort src tests examples

type-check:
	poetry run mypy src/aiconexus

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '.pytest_cache' -exec rm -rf {} +
	find . -name '.mypy_cache' -exec rm -rf {} +
	find . -name '.ruff_cache' -exec rm -rf {} +
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '.coverage' -exec rm -f {} +
	rm -rf htmlcov/
	@echo "[OK] Cleaned up"

run:
	poetry run uvicorn src.aiconexus.api.app:app --host 0.0.0.0 --port 8000

dev:
	poetry run uvicorn src.aiconexus.api.app:app --host 0.0.0.0 --port 8000 --reload

docs:
	@echo "Building documentation..."
	@echo "Documentation build will be implemented soon"

shell:
	poetry shell

setup:
	@bash scripts/setup_dev_env.sh

example-hello:
	poetry run python examples/hello_world/agent.py

# Gateway Docker Commands
gateway-build:
	@echo "Building Gateway Docker image..."
	./gateway-docker.sh build

gateway-start:
	@echo "Starting Gateway..."
	./gateway-docker.sh start
	@echo "Gateway is running on ws://127.0.0.1:8000/ws"

gateway-stop:
	@echo "Stopping Gateway..."
	./gateway-docker.sh stop

gateway-restart:
	@echo "Restarting Gateway..."
	./gateway-docker.sh restart

gateway-status:
	./gateway-docker.sh status

gateway-logs:
	./gateway-docker.sh logs -f

gateway-health:
	./gateway-docker.sh health

gateway-shell:
	./gateway-docker.sh shell

gateway-cleanup:
	./gateway-docker.sh cleanup

gateway-test:
	@echo "Testing Gateway Docker deployment..."
	./test_docker_gateway.sh

gateway-verify:
	@echo "Verifying Docker setup..."
	./verify_docker_setup.sh

.DEFAULT_GOAL := help
