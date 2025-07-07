# Myt MCP Server Fix Summary

## Issue
The "Myt MCP Server" was failing with:
- Status: ✘ failed
- URL: http://localhost:8002/mcp/
- Error: Dynamic client registration failed: HTTP 404

## Root Cause
1. **Port Conflict**: Port 8002 was occupied by `gvproxy` (Podman container runtime proxy)
2. **Server Not Running**: The mcp-tools server was not actually running
3. **Configuration Mismatch**: Claude was trying to connect to port 8002, but server couldn't start there

## Solution Applied

### 1. Started the Server on Port 8003
```bash
cd /Users/dlighty/code/mcp-tools
PORT=8003 node dist/index.js &
```

### 2. Updated Claude Configuration
Changed the server URL in `~/.claude.json`:
- **From**: `http://localhost:8002/mcp/`
- **To**: `http://localhost:8003/mcp`

### 3. Created Management Scripts
- **start-server.sh**: Automated startup script with proper error checking
- **stop-server.sh**: Clean shutdown script

### 4. Verified Endpoint Format
- Correct endpoint: `http://localhost:8003/mcp` (no trailing slash)
- Server responds with proper MCP protocol information

## Final Configuration

### Claude Config (`~/.claude.json`)
```json
{
  "mcpServers": {
    "upgrade-opex": {
      "type": "stdio",
      "command": "mcp-task",
      "args": [],
      "env": {}
    },
    "mykb": {
      "type": "http",
      "url": "http://localhost:8000/mcp/"
    },
    "myt": {
      "type": "http",
      "url": "http://localhost:8003/mcp"
    }
  }
}
```

### Server Status
- **Service**: mcp-tools v1.0.0
- **Transport**: Streamable HTTP
- **Endpoint**: http://localhost:8003/mcp
- **Status**: ✅ Running successfully

## Tools Available
The "myt" server provides these tools:
- pr_violations
- code_review  
- morning_workflow
- deploy_approval

## Management Commands
```bash
# Start server
./start-server.sh

# Stop server
./stop-server.sh

# Test endpoint
curl http://localhost:8003/mcp
```

## Why Port 8003?
- Port 8002 is used by gvproxy (Podman container runtime)
- gvproxy is essential for Podman functionality and should not be killed
- Port 8003 provides a clean, conflict-free alternative

## Verification
Server is responding correctly with MCP protocol compliance and all configured tools available.