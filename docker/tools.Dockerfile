# Tools MCP Server Dockerfile
# Multi-stage build for optimized production container

FROM python:3.11-slim as builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Set poetry configuration
RUN poetry config virtualenvs.create false

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --only=main --no-dev

# Production stage
FROM python:3.11-slim as production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash mcp

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=mcp:mcp tools/ /app/tools/
COPY --chown=mcp:mcp common/ /app/common/

# Set working directory
WORKDIR /app

# Switch to non-root user
USER mcp

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${MCP_SERVER_PORT:-8003}/health || exit 1

# Default environment variables
ENV MCP_SERVER_PORT=8003
ENV LOG_LEVEL=INFO
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8003

# Start tools server
CMD ["python", "tools/server.py"]