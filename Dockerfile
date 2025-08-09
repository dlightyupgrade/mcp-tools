# MCP Tools - FastMCP Python Server
# Version: 2.0.0
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies for tool execution
RUN apt-get update && apt-get install -y \
    git \
    bash \
    curl \
    jq \
    openssh-client \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy dependency files first for better layer caching
COPY pyproject.toml poetry.lock* README.md ./

# Configure Poetry and install dependencies (dependencies only, not the package itself)
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-root

# Skip OAuth patching for now - FastMCP handles headless environments

# Copy source code
COPY src/ ./src/
COPY common/ ./common/
COPY mcp_tools_server.py version.py ./

# Now install the package itself
RUN poetry install --only-root

# Create non-root user
RUN groupadd -g 1001 mcp && \
    useradd -r -u 1001 -g mcp mcp

# Set ownership
RUN chown -R mcp:mcp /app
USER mcp

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Environment variables
ENV PYTHONPATH=/app
ENV MCP_SERVER_PORT=8002
ENV LOG_LEVEL=INFO
ENV MCP_TOOLS_VERSION=2.0.0

# Labels for container metadata
LABEL org.opencontainers.image.title="MCP Tools"
LABEL org.opencontainers.image.description="FastMCP Tools Server v2.0 - Modular development workflow automation"
LABEL org.opencontainers.image.version="2.0.0"
LABEL org.opencontainers.image.source="https://github.com/user/mcp-tools"
LABEL org.opencontainers.image.vendor="Development Tools"

# Start FastMCP server
CMD ["python", "mcp_tools_server.py"]