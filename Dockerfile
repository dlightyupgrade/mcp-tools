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

# Install Python dependencies directly
RUN pip install --no-cache-dir \
    fastmcp>=2.10.2 \
    httpx>=0.28.1 \
    psutil>=7.0.0

# AUTHENTICATION FIX: Patch FastMCP OAuth client to prevent browser opening
# This prevents browser windows from opening in headless environments
RUN python -c "
import site
import os
packages_dir = site.getsitepackages()
for pkg_dir in packages_dir:
    oauth_file = os.path.join(pkg_dir, 'fastmcp', 'client', 'auth', 'oauth.py')
    if os.path.exists(oauth_file):
        with open(oauth_file, 'r') as f:
            content = f.read()
        patched_content = content.replace(
            'webbrowser.open(authorization_url)',
            '# PATCHED: Disable browser opening in containers\\n        pass  # webbrowser.open(authorization_url)'
        )
        with open(oauth_file, 'w') as f:
            f.write(patched_content)
        print(f'Patched FastMCP OAuth client: {oauth_file}')
        break
else:
    print('FastMCP OAuth client not found - no patching needed')
"

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
CMD ["python", "src/mcp_tools_server.py"]