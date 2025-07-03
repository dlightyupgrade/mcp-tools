#!/usr/bin/env node

/**
 * MCP Tools Server
 * 
 * Entry point that handles both stdio and HTTP transport modes
 * Includes new_ws workstream integration tools
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { createMCPServer } from './server.js';
import { createHTTPServer } from './http-server.js';

const DEFAULT_HTTP_PORT = 8002;

async function main() {
  const args = process.argv.slice(2);
  const isStdioMode = args.includes('--stdio') || process.env.MCP_STDIO_MODE === 'true';
  const port = parseInt(process.env.PORT || DEFAULT_HTTP_PORT.toString(), 10);

  if (isStdioMode) {
    // Stdio Transport Mode - legacy/optional for local development
    console.error('🔧 Starting MCP Tools Server in stdio mode (legacy)');
    console.error('📋 Transport: stdio (local communication only)');
    console.error('🛠️  Tools: pr_violations, code_review, morning_workflow, deploy_approval');
    
    const server = createMCPServer();
    const transport = new StdioServerTransport();
    
    await server.connect(transport);
    console.error('✅ MCP Tools Server connected via stdio');
  } else {
    // Streaming HTTP Transport Mode - default for containers and production
    console.log(`🚀 Starting MCP Tools Server with Streaming HTTP transport on port ${port}`);
    console.log(`📡 MCP endpoint: http://localhost:${port}/mcp`);
    console.log(`🐳 Container-ready with streaming HTTP as default transport`);
    console.log(`🛠️  Tools: pr_violations, code_review, morning_workflow, deploy_approval`);
    
    await createHTTPServer(port);
  }
}

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.error('🛑 Shutting down MCP Tools Server...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.error('🛑 Shutting down MCP Tools Server...');
  process.exit(0);
});

// Start the server
main().catch((error) => {
  console.error('❌ Fatal error starting MCP Tools Server:', error);
  process.exit(1);
});