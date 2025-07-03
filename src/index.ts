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
import { createHTTPServer } from './http-server-simple.js';

const DEFAULT_HTTP_PORT = 8000;

async function main() {
  const args = process.argv.slice(2);
  const isHTTPMode = args.includes('--http') || process.env.MCP_HTTP_MODE === 'true';
  const port = parseInt(process.env.PORT || DEFAULT_HTTP_PORT.toString(), 10);

  if (isHTTPMode) {
    // HTTP Transport Mode - for remote access and production
    console.log(`🚀 Starting MCP Tools Server in HTTP mode on port ${port}`);
    console.log(`📡 MCP endpoint: http://localhost:${port}/mcp`);
    
    await createHTTPServer(port);
  } else {
    // Stdio Transport Mode - for local development and Claude Desktop
    console.error('🔧 Starting MCP Tools Server in stdio mode');
    console.error('📋 Transport: stdio (local communication)');
    console.error('🛠️  Tools: new_ws, echo, get_system_info');
    
    const server = createMCPServer();
    const transport = new StdioServerTransport();
    
    await server.connect(transport);
    console.error('✅ MCP Tools Server connected via stdio');
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