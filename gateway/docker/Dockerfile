# Use Python 3.13 slim image as base
FROM python:3.13-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install Poetry
RUN pip install poetry==1.7.1

# Copy Poetry files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-directory --no-interaction --no-ansi

# ============================================================================
# Development Stage
# ============================================================================
FROM base as development

# Copy entire project
COPY . .

# Install dev dependencies
RUN poetry install --no-interaction --no-ansi

# Expose port for development
EXPOSE 8000

# Default command for development
CMD ["poetry", "run", "pytest"]


# ============================================================================
# Testing Stage
# ============================================================================
FROM base as testing

# Copy entire project
COPY . .

# Install dev dependencies including test packages
RUN poetry install --with dev --no-interaction --no-ansi

# Run tests
CMD ["poetry", "run", "pytest", "tests/"]


# ============================================================================
# Production Stage
# ============================================================================
FROM base as production

# Install only production dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-directory --no-interaction --no-ansi --no-dev

# Copy only necessary files
COPY src/ ./src/
COPY README.md ./

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "-m", "aiconexus.server"]
