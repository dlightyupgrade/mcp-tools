# MCP Tools Server

A container-ready Model Context Protocol (MCP) server with streaming HTTP transport, implementing development workflow tools for PR analysis, code review, morning workflow automation, and deployment approvals.

## Features

- **🚀 Streaming HTTP Transport**: MCP 2025-03-26 specification compliant
- **🐳 Container Ready**: Docker support with health checks
- **⚡ Four Core Tools**: PR violations, code review, morning workflow, deploy approval
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

## Quick Start

### HTTP Mode (Default)
```bash
npm install
npm run build
npm start
```

Server runs on `http://localhost:8002` with endpoints:
- **Health**: `GET /health`
- **MCP Discovery**: `GET /mcp` 
- **MCP Protocol**: `POST /mcp`
- **Streaming**: `GET /mcp/stream`

### Stdio Mode (Legacy)
```bash
npm start -- --stdio
```

### Docker Container
```bash
docker build -t mcp-tools .
docker run -p 8002:8002 mcp-tools
```

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

## Architecture

### Transport Modes
- **Streaming HTTP** (Default): Container-ready, production-focused
- **Stdio** (Legacy): Local development, CLI integration

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

## Configuration

### Environment Variables
- `PORT`: HTTP server port (default: 8002)
- `MCP_TRANSPORT`: Transport mode (`http` or `stdio`)
- `NODE_ENV`: Node environment (`production`, `development`)

### External Dependencies
- GitHub CLI (`gh`) for API access
- `jq` for JSON processing
- External tool scripts in PATH

## Health Monitoring

### Health Check Endpoint
```bash
curl http://localhost:8002/health
```

Response includes:
- Service status and version
- Transport mode and MCP specification
- Timestamp for monitoring

### Docker Health Check
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
│   ├── index.ts          # Entry point with transport selection
│   ├── server.ts         # MCP server implementation
│   └── http-server.ts    # Streaming HTTP implementation
├── dist/                 # Compiled JavaScript
├── Dockerfile           # Container configuration
└── package.json         # Dependencies and scripts
```

### Build and Test
```bash
npm run build    # Compile TypeScript
npm test         # Run tests (if available)
npm start        # Start HTTP server
npm run dev      # Development mode
```

## MCP 2025-03-26 Compliance

- ✅ JSON-RPC 2.0 protocol
- ✅ Streaming HTTP transport
- ✅ Tool discovery and execution
- ✅ Proper error handling
- ✅ Server-Sent Events support
- ✅ CORS enabled
- ✅ Health checks
- ✅ Container ready

## License

MIT License - See LICENSE file for details