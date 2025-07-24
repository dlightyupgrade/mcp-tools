# CLAUDE.md

This file provides guidance to Claude Code when working with the MCP Tools project.

## Project Information
- **Name**: MCP Tools Server
- **Version**: 1.0.0
- **Type**: Python FastMCP Server
- **Transport**: MCP 2025-03-26 HTTP Streaming (FastMCP)
- **Port**: 8002 (default)
- **Architecture**: FastMCP with hybrid scripting pattern

## Container Preferences

### ⚠️ IMPORTANT: Use Podman, NOT Docker
**Container Tool**: Always use `podman` instead of `docker` for this project and environment.

**Container Commands**:
```bash
# Build container
podman build -t mcp-tools:latest .

# Run container
podman run --rm -p 8002:8002 -d --name mcp-tools mcp-tools:latest

# Check running containers
podman ps

# Stop container
podman stop mcp-tools

# View logs
podman logs mcp-tools

# Available tags
podman images | grep mcp-tools
```

### Container Configuration
- **Base Image**: python:3.11-slim
- **Port**: 8002 (both host and container)
- **Health Check**: http://localhost:8002/health
- **Format**: OCI (Podman default), not Docker format
- **User**: Non-root user for security
- **Tags**: `latest`
- **Transport**: FastMCP HTTP Streaming

## Port Configuration

### Default Port: 8002
- **HTTP Server**: http://localhost:8002
- **MCP Endpoint**: http://localhost:8002/mcp
- **Health Check**: http://localhost:8002/health
- **Environment Variable**: PORT=8002

### Port Memory/Context
The port 8002 is specifically chosen for MCP Tools to avoid conflicts with:
- **8000**: MCP-RAG production service
- **8001**: ChromaDB (MCP-RAG dependency)
- **8003+**: Future MCP services

## Development Commands

### Build and Run
```bash
# Python/uv (Recommended)
uv sync              # Install dependencies
uv run python src/mcp_tools_server.py  # Run server

# Alternative with pip
pip install -e .
python src/mcp_tools_server.py

# Container
podman build -t mcp-tools .
podman run --rm -p 8002:8002 mcp-tools
```

### Testing Endpoints
```bash
# Health check
curl http://localhost:8002/health

# List tools
curl -X POST http://localhost:8002/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'

# Test echo tool
curl -X POST http://localhost:8002/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "echo", "arguments": {"text": "Hello MCP"}}}'
```

## Architecture

### Core Components
- **src/mcp_tools_server.py**: FastMCP server implementation
- **pyproject.toml**: Python dependencies and configuration
- **uv.lock**: Locked dependency versions
- **Dockerfile**: Container configuration

### Available Tools
1. **pr_violations**: Analyze PR violations and threads
2. **code_review**: Comprehensive code quality review
3. **echo**: Simple echo for testing
4. **get_system_info**: System information

## Quality Features
- **Input Validation**: Security checks and parameter validation
- **Error Handling**: Standardized error responses
- **Test Coverage**: Jest with TypeScript support
- **Code Quality**: Shared utilities, no duplication
- **Container Ready**: Production-ready with health checks

## Integration Notes
- **CLI Tools**: Integrates with pr-violations-claude and code-review-claude scripts
- **GitHub**: Requires gh CLI for PR analysis tools
- **Dependencies**: jq, curl, git for tool execution

## Environment Variables
- `MCP_SERVER_PORT`: HTTP server port (default: 8002)
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)
- `TOOL_TIMEOUT`: Tool execution timeout in seconds (default: 300)
- `RATE_LIMIT_REQUESTS`: Rate limit for requests (default: 100)