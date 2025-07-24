# MCP Tools Server

A production-ready Model Context Protocol (MCP) server built with FastMCP Python framework, featuring HTTP Streaming transport and streamlined development workflow tools for PR analysis and code review.

## Features

- **🚀 FastMCP Framework**: Modern Python MCP server with auto-generated schemas
- **📡 HTTP Streaming Transport**: MCP 2025-03-26 specification compliant  
- **🐳 Container Ready**: Podman/Docker support with health checks and auto-restart
- **⚡ Instruction-Based Tools**: Returns Claude Code execution instructions for GitHub analysis
- **🔐 Shell Authentication**: OAuth-compatible authentication for headless/containerized environments
- **📊 External Context**: Configurable context files for domain-specific analysis patterns

## Tools Available (4 Core Tools)

### 1. PR Violations (`pr_violations`)
**Architecture**: Instruction-based orchestration (does NOT execute GitHub commands directly)

Analyzes PR violations, open review threads, CI failures, and merge conflicts by returning structured instructions for Claude Code to execute.

- **Input**: GitHub PR URL, optional description
- **Output**: Detailed GitHub API commands and analysis format requirements for Claude Code execution
- **Context**: Loads external PR-VIOLATIONS-CONTEXT.md for domain-specific patterns
- **Categories**: Blocking, High Priority, Medium Priority, Discussion threads with complexity assessment

### 2. Code Review (`code_review`)
**Architecture**: Instruction-based orchestration (does NOT execute GitHub commands directly)

Performs comprehensive code quality review by returning structured instructions for Claude Code to execute.

- **Input**: GitHub PR URL, optional focus area, max diff lines (default: 2000)
- **Output**: Detailed GitHub API commands and comprehensive analysis format for Claude Code execution  
- **Context**: Loads external CODE-REVIEW-CONTEXT.md for quality assessment patterns
- **Analysis**: Violations, code quality, tests, security, business logic, JIRA compliance

### 3. System Tools
- **echo**: Simple echo for testing MCP connectivity and basic functionality
- **get_system_info**: System information, server diagnostics, and process monitoring

## Key Architecture: Instruction-Based Orchestration

**Critical Design Pattern**: These tools do NOT execute GitHub CLI commands or JIRA commands directly. Instead, they return comprehensive instructions for Claude Code to execute externally.

**Why This Architecture**:
- MCP servers can't reliably run external commands in containerized environments
- Claude Code has proper GitHub CLI authentication and environment access
- Maintains separation of concerns: data orchestration vs execution
- Follows the same pattern as other successful MCP tools

**Example Flow**:
1. User calls `pr_violations` tool with PR URL
2. Tool returns structured GitHub API commands and analysis requirements
3. Claude Code executes the GitHub API calls using `gh` CLI
4. Claude Code processes results using the provided analysis format
5. Result: Comprehensive PR violations analysis with actionable solutions

## Quick Start

### For Other Developers: Container Setup Guide

**Prerequisites**:
- Podman or Docker for containerization (Podman preferred)
- GitHub CLI (`gh`) authenticated in your environment for testing tools

#### 1. Clone and Build
```bash
# Clone the repository
git clone <repository-url>
cd mcp-tools

# Build container (prefer podman over docker)
podman build -t mcp-tools:latest .
```

#### 2. Deploy Container
```bash
# Run with auto-restart capability
podman run --restart=always -p 8002:8002 -d --name mcp-tools mcp-tools:latest

# Verify container health
podman ps --filter name=mcp-tools
curl http://localhost:8002/health
```

#### 3. Add to Claude Code
```bash
# Add the MCP server to your Claude Code environment with HTTP transport
claude mcp add http://localhost:8002 --transport http --scope user

# Verify MCP server appears in Claude Code
claude mcp list
```

#### 4. Test Tools
Once added to Claude Code, test the tools:

**Test PR Violations Tool**:
```
In Claude Code, try: "Use pr_violations tool to analyze this PR: https://github.com/owner/repo/pull/123"
```

**Test Code Review Tool**:
```  
In Claude Code, try: "Use code_review tool to review this PR with focus on security: https://github.com/owner/repo/pull/123"
```

Server runs on `http://localhost:8002` with endpoints:
- **Health**: `GET /health` - Container health monitoring
- **MCP Discovery**: `GET /mcp` - Protocol capabilities
- **OAuth Discovery**: `GET /.well-known/oauth-authorization-server-mcp` - Authentication metadata
- **MCP Protocol**: `POST /mcp` - Tool execution and streaming

**Important**: When adding to Claude Code, use `--transport http --scope user` flags for HTTP-based MCP servers.

## MCP Protocol Examples

### List Available Tools
```bash
curl -X POST http://localhost:8002/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'
```

### Call PR Violations Tool
```bash
curl -X POST http://localhost:8002/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0", 
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "pr_violations",
      "arguments": {
        "pr_url": "https://github.com/owner/repo/pull/123"
      }
    }
  }'
```

### Test Echo Tool
```bash
curl -X POST http://localhost:8002/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "echo",
      "arguments": {
        "text": "Hello FastMCP!"
      }
    }
  }'
```

## Architecture

### FastMCP Framework
- **Auto-generated schemas**: Type-safe tool definitions with validation
- **HTTP Streaming**: Production-ready transport with uvicorn ASGI server
- **Comprehensive logging**: Structured logging with configurable levels
- **Error handling**: Robust error handling with timeout management

### Hybrid Scripting Pattern
- **Bash Scripts**: Reliable data extraction using GitHub CLI
- **AI Processing**: Intelligent analysis and categorization
- **External Context**: Domain-specific guidelines and patterns

### Tool Integration
**Architecture Change**: Tools now use instruction-based orchestration instead of external script execution:

**Previous Architecture** (Deprecated):
- `pr-violations-claude`: External script execution
- `code-review-claude`: External script execution  

**Current Architecture** (Active):
- `pr_violations`: Returns GitHub API instructions for Claude Code execution
- `code_review`: Returns comprehensive analysis instructions for Claude Code execution
- External context files: `PR-VIOLATIONS-CONTEXT.md`, `CODE-REVIEW-CONTEXT.md` for domain patterns

## Troubleshooting for Developers

### Common Setup Issues

#### 1. Container Port Conflicts
```bash
# Check if port 8002 is already in use
lsof -i :8002

# If MCP-RAG is using 8000, MCP Tools should use 8002 (different services)
# If you see conflicts, kill existing containers:
podman stop mcp-tools && podman rm mcp-tools
```

#### 2. Authentication Issues in Claude Code
```bash
# Verify MCP server is running and healthy
curl http://localhost:8002/health

# Check OAuth discovery endpoint exists
curl http://localhost:8002/.well-known/oauth-authorization-server-mcp

# Ensure correct claude mcp add command with transport and scope
claude mcp add http://localhost:8002 --transport http --scope user

# If authentication fails, rebuild container with latest auth fixes:
podman build -t mcp-tools:latest . --no-cache
podman run --restart=always -p 8002:8002 -d --name mcp-tools mcp-tools:latest
```

#### 3. Container Build Issues
```bash
# If build fails, try clean build
podman build -t mcp-tools:latest . --no-cache

# Check if container runs locally first
podman run --rm -p 8002:8002 mcp-tools:latest

# If successful, then run with auto-restart
podman run --restart=always -p 8002:8002 -d --name mcp-tools mcp-tools:latest
```

#### 4. Tool Execution Issues
**Problem**: Tools return "invalid GitHub PR URL" errors
**Solution**: Ensure PR URLs are in exact format: `https://github.com/owner/repo/pull/number`

**Problem**: Tools don't return expected analysis instructions
**Solution**: Check that external context files exist:
- `/Users/dlighty/code/llm-context/PR-VIOLATIONS-CONTEXT.md`
- `/Users/dlighty/code/llm-context/CODE-REVIEW-CONTEXT.md`

#### 5. Container Auto-Restart Issues
```bash
# Verify container restart policy
podman inspect mcp-tools | grep -A 5 "RestartPolicy"

# Should show: "Name": "always", "MaximumRetryCount": 0

# If not set correctly, remove and recreate:
podman stop mcp-tools && podman rm mcp-tools
podman run --restart=always -p 8002:8002 -d --name mcp-tools mcp-tools:latest
```

### Development Testing

#### Test Individual Tools via Direct API
```bash
# Test pr_violations tool
curl -X POST http://localhost:8002/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "pr_violations",
      "arguments": {
        "pr_url": "https://github.com/owner/repo/pull/123",
        "description": "Test analysis"
      }
    }
  }'

# Test code_review tool  
curl -X POST http://localhost:8002/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "code_review",
      "arguments": {
        "pr_url": "https://github.com/owner/repo/pull/123",
        "focus": "security"
      }
    }
  }'
```

## Configuration

### Environment Variables
- `MCP_SERVER_PORT`: HTTP server port (default: 8002)
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)
- `TOOL_TIMEOUT`: Tool execution timeout in seconds (default: 300)
- `RATE_LIMIT_REQUESTS`: Rate limit for requests (default: 100)

### Tool Script Paths
Configure paths to external scripts via environment variables:
- `PR_VIOLATIONS_SCRIPT`: Path to pr-violations-claude script
- `CODE_REVIEW_SCRIPT`: Path to code-review-claude script

### External Dependencies
For deployment and testing:
- **Podman** or Docker for containerization (Podman preferred)
- **GitHub CLI** (`gh`) for testing tools via Claude Code (not required for server operation)

**Note**: The container includes all Python dependencies. The MCP server does NOT require external dependencies - tools return instructions for Claude Code to execute independently.

## Health Monitoring

### Health Check Endpoint
```bash
curl http://localhost:8002/health
```

Response includes:
- Service status and version
- Transport mode and MCP specification
- System metrics (CPU, memory, disk)
- Timestamp for monitoring

### Container Health Check
Built-in health check with 30s intervals:
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8002/health || exit 1
```

## Development

### Project Structure
```
mcp-tools/
├── src/
│   └── mcp_tools_server.py    # FastMCP server implementation
├── pyproject.toml             # Python dependencies and config
├── uv.lock                    # Locked dependencies
├── .python-version            # Python version specification
├── Dockerfile                 # Container configuration
└── README.md                  # This file
```

### Build and Test
```bash
# Install dependencies
uv sync

# Run in development mode
uv run python src/mcp_tools_server.py

# Build container
podman build -t mcp-tools .

# Run container
podman run --rm -p 8002:8002 mcp-tools

# Check health
curl http://localhost:8002/health
```

### Adding New Tools
1. Add tool function with `@mcp.tool` decorator
2. Include proper type hints and docstring
3. Add error handling and logging
4. Update this README with tool documentation

## FastMCP Compliance

- ✅ Python 3.11+ compatibility
- ✅ Auto-generated JSON-RPC schemas
- ✅ HTTP Streaming transport
- ✅ Tool discovery and execution
- ✅ Comprehensive error handling
- ✅ Production-ready deployment
- ✅ Container support
- ✅ Health monitoring

## Port Allocation

This server uses **port 8002** to avoid conflicts with:
- **8000**: MCP-RAG production service
- **8001**: ChromaDB (MCP-RAG dependency)
- **8003+**: Reserved for future MCP services

## Container Preferences

**⚠️ Important**: Use `podman` instead of `docker` for this environment:
```bash
# Preferred container commands
podman build -t mcp-tools .
podman run --rm -p 8002:8002 mcp-tools
podman ps
podman logs mcp-tools
```

## License

MIT License - See LICENSE file for details