# MCP Tools - FastMCP Python Server
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

# Copy dependency files
COPY pyproject.toml uv.lock .python-version ./

# Install uv and dependencies
RUN pip install uv && \
    uv sync --frozen

# Copy source code
COPY src/ ./src/

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

# Start FastMCP server
CMD ["uv", "run", "python", "src/mcp_tools_server.py"]