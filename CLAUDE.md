# CLAUDE.md

This file provides guidance to Claude Code when working with the MCP Tools project.

## Project Information
- **Name**: MYT (My Tools) Server
- **Version**: 1.0.0
- **Type**: Node.js/TypeScript MCP Server
- **Transport**: MCP 2025-03-26 Streamable HTTP (primary), stdio (legacy)
- **Port**: 8002 (default)
- **Architecture**: Session-managed streaming with request correlation

## Container Preferences

### ⚠️ IMPORTANT: Use Podman, NOT Docker
**Container Tool**: Always use `podman` instead of `docker` for this project and environment.

**Container Commands**:
```bash
# Build container
podman build -t myt:latest .

# Run container
podman run --rm -p 8002:8002 -d --name myt myt:latest

# Check running containers
podman ps

# Stop container
podman stop myt

# View logs
podman logs myt

# Available tags
podman images | grep myt
```

### Container Configuration
- **Base Image**: node:20-alpine (updated from node:18 for dependency compatibility)
- **Port**: 8002 (both host and container)
- **Health Check**: http://localhost:8002/health
- **Format**: OCI (Podman default), not Docker format
- **User**: Non-root user (mcp:1001) for security
- **Tags**: `latest`, `streamable-http`
- **Transport**: MCP 2025-03-26 Streamable HTTP with session management

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
# Development
npm install
npm run build
npm run dev          # Watch mode
npm start            # Production mode

# Testing
npm test             # Run tests
npm run test:watch   # Watch mode
npm run test:coverage # With coverage

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
- **index.ts**: Entry point with transport selection
- **server.ts**: MCP server implementation (stdio)
- **http-server.ts**: Streaming HTTP implementation
- **utils/tool-executors.ts**: Shared tool execution functions
- **utils/validation.ts**: Input validation and security

### Available Tools
1. **new_ws**: Launch workstream commands in iTerm2
2. **pr_violations**: Analyze PR violations and threads
3. **code_review**: Comprehensive code quality review
4. **morning_workflow**: Daily workflow automation
5. **deploy_approval**: Generate Slack deployment messages
6. **echo**: Simple echo for testing
7. **get_system_info**: System information

## Quality Features
- **Input Validation**: Security checks and parameter validation
- **Error Handling**: Standardized error responses
- **Test Coverage**: Jest with TypeScript support
- **Code Quality**: Shared utilities, no duplication
- **Container Ready**: Production-ready with health checks

## Integration Notes
- **CLI Tools**: Integrates with personal-dev-tools CLI scripts
- **Workstreams**: Uses wclds for iTerm2 pane management
- **GitHub**: Requires gh CLI for PR analysis tools
- **Dependencies**: jq, curl, git, openssh-client for tool execution

## Environment Variables
- `PORT`: HTTP server port (default: 8002)
- `MCP_TRANSPORT`: Transport mode (http/stdio)
- `NODE_ENV`: Node environment (production/development)
- `MCP_STDIO_MODE`: Force stdio mode (true/false)