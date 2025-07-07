# MCP Tools Server

A production-ready Model Context Protocol (MCP) server built with FastMCP Python framework, featuring HTTP Streaming transport and comprehensive development workflow tools for PR analysis, code review, morning workflow automation, and deployment approvals.

## Features

- **🚀 FastMCP Framework**: Modern Python MCP server with auto-generated schemas
- **📡 HTTP Streaming Transport**: MCP 2025-03-26 specification compliant
- **🐳 Container Ready**: Podman/Docker support with health checks
- **⚡ Development Tools**: PR violations, code review, morning workflow, deploy approval
- **🔧 Hybrid Architecture**: Bash data extraction + AI-powered analysis
- **📊 External Context**: Configurable context files for domain-specific analysis

## Tools Available

### 1. PR Violations (`pr_violations`)
Analyze PR violations, open review threads, CI failures, and merge conflicts.
- **Input**: GitHub PR URL, optional description
- **Output**: Comprehensive violation analysis with actionable solutions

### 2. Code Review (`code_review`) 
Perform comprehensive code quality review of pull requests.
- **Input**: GitHub PR URL, optional review focus description
- **Output**: Quality assessment with severity-prioritized findings

### 3. Morning Workflow (`morning_workflow`)
Execute daily morning workflow automation with parallel subagent orchestration.
- **Input**: Optional workflow customization description
- **Output**: Todo import, PR analysis, master updates, thread resolution

### 4. Deploy Approval (`deploy_approval`)
Generate deployment approval messages for Slack team coordination.
- **Input**: GitHub PR URL, optional deployment description  
- **Output**: Formatted Slack message with author approvals

### 5. New Workstream (`new_ws`)
Launch workstream commands in iTerm2 for multi-Claude coordination.
- **Input**: Command to execute, optional description
- **Output**: Workstream launch status and iTerm2 pane creation

### 6. System Tools
- **echo**: Simple echo for testing MCP connectivity
- **get_system_info**: System information and server diagnostics

## Quick Start

### Python/uv (Recommended)
```bash
# Install dependencies
uv sync

# Run the server
uv run python src/mcp_tools_server.py
```

### Docker/Podman Container
```bash
# Build container (use podman for this environment)
podman build -t mcp-tools .

# Run container
podman run --rm -p 8002:8002 -d --name mcp-tools mcp-tools

# Check status
podman ps
podman logs mcp-tools
```

Server runs on `http://localhost:8002` with endpoints:
- **Health**: `GET /health`
- **MCP Discovery**: `GET /mcp` 
- **MCP Protocol**: `POST /mcp`
- **Streaming**: Available via FastMCP HTTP implementation

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
Each tool leverages proven CLI scripts:
- `pr-violations-claude`: Comprehensive PR violation analysis
- `code-review-claude`: Quality assessment automation  
- `morning-workflow-claude`: Multi-subagent workflow orchestration
- `deployment-diff-claude`: Slack message generation
- `wclds`: iTerm2 workstream coordination

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
- `MORNING_WORKFLOW_SCRIPT`: Path to morning-workflow-claude script
- `DEPLOY_APPROVAL_SCRIPT`: Path to deployment-diff-claude script
- `NEW_WS_SCRIPT`: Path to wclds script

### External Dependencies
- **GitHub CLI** (`gh`) for API access
- **jq** for JSON processing
- **External tool scripts** in PATH or configured paths
- **uv** for Python dependency management

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