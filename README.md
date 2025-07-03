# MCP Tools

MCP server with new_ws workstream integration tools built on the official TypeScript SDK with streaming HTTP transport.

## Features

- ✅ **new_ws Integration** - Launch workstream commands via MCP
- ✅ **Official MCP TypeScript SDK** - Full 2025-03-26 spec compliance
- ✅ **Streaming HTTP Transport** - Modern MCP protocol support
- ✅ **Dual Transport Support** - Both stdio and HTTP for maximum compatibility  
- ✅ **iTerm2 Integration** - Automated pane creation for workstreams
- ✅ **High Performance** - Fast HTTP server with Fastify
- ✅ **Production Ready** - Robust error handling and logging

## Tools Included

### new_ws Tool
Launch new workstream commands with automated iTerm2 pane creation:

```json
{
  "name": "new_ws",
  "description": "Launch a new workstream command in iTerm2",
  "inputSchema": {
    "type": "object",
    "properties": {
      "command": {
        "type": "string", 
        "description": "The workstream command to execute"
      },
      "description": {
        "type": "string",
        "description": "Optional description of the workstream"
      }
    },
    "required": ["command"]
  }
}
```

**Example Usage:**
- `new_ws pr_violations https://github.com/owner/repo/pull/123`
- `new_ws code_review https://github.com/owner/repo/pull/456`
- `new_ws morning_workflow`

## Quick Start

```bash
# Install dependencies
npm install

# Development mode with hot reload
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## Integration with Claude Desktop

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "mcp-tools": {
      "command": "node",
      "args": ["/path/to/mcp-tools/dist/index.js"]
    }
  }
}
```

## new_ws Command Integration

The new_ws tool integrates with your existing workstream infrastructure:

1. **Command Parsing** - Intelligently parses new_ws commands
2. **iTerm2 Automation** - Creates new panes for workstream execution
3. **Context Switching** - Sets up appropriate Claude context for each workstream
4. **Session Tracking** - Tracks workstream status and outcomes

### Supported Commands

- `pr_violations <PR_URL>` - Comprehensive PR violations analysis
- `code_review <PR_URL>` - Automated code quality review  
- `morning_workflow` - Daily workflow automation
- `deploy_approval <PR_URL>` - Deployment approval messaging
- Custom commands via extension

## Project Structure

```
src/
├── index.ts          # Entry point and transport setup
├── server.ts         # MCP server with new_ws tools
├── tools/
│   ├── basic-tools.ts    # Basic utility tools
│   └── new-ws-tools.ts   # new_ws workstream integration
└── utils/
    └── iterm.ts      # iTerm2 automation utilities
```

## Development

### Adding New Workstream Commands

1. Update the new_ws tool handler in `src/server.ts`
2. Add command parsing logic in `src/tools/new-ws-tools.ts`
3. Test with MCP inspector or Claude Desktop

### iTerm2 Integration

The server includes utilities for iTerm2 automation:
- Create new panes
- Execute commands in specific panes
- Set pane titles and organize workstreams

## Requirements

- Node.js >= 18.0.0
- iTerm2 (for workstream automation)
- Claude Desktop or MCP-compatible client

## License

MIT License - see LICENSE file for details.