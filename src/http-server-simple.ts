/**
 * Simplified HTTP Server Implementation
 * 
 * Basic HTTP server for MCP tools without complex request handling
 */

import fastify, { FastifyInstance } from 'fastify';

export async function createHTTPServer(port: number): Promise<FastifyInstance> {
  const app = fastify({
    logger: {
      level: 'info',
    },
  });

  // Health check endpoint
  app.get('/health', async () => {
    return { 
      status: 'healthy', 
      service: 'mcp-tools',
      version: '1.0.0',
      timestamp: new Date().toISOString(),
    };
  });

  // MCP endpoint discovery
  app.get('/mcp', async () => {
    return {
      service: 'mcp-tools',
      version: '1.0.0',
      protocol: 'Model Context Protocol',
      transport: 'Streamable HTTP',
      specification: '2025-03-26',
      capabilities: {
        tools: true,
        new_ws: true,
      },
      tools: [
        {
          name: 'new_ws',
          description: 'Launch workstream commands in iTerm2',
          examples: [
            'pr_violations <PR_URL>',
            'code_review <PR_URL>',
            'morning_workflow',
            'deploy_approval <PR_URL>'
          ]
        },
        {
          name: 'echo',
          description: 'Echo back input text'
        },
        {
          name: 'get_system_info', 
          description: 'Get system information'
        }
      ],
      timestamp: new Date().toISOString(),
    };
  });

  // Basic MCP request handling (simplified)
  app.post('/mcp', async (request, reply) => {
    reply.type('application/json');
    return {
      message: 'MCP tools server is running',
      note: 'Use stdio mode for full MCP functionality: node dist/index.js',
      service: 'mcp-tools',
      timestamp: new Date().toISOString(),
    };
  });

  // Start the server
  try {
    await app.listen({ port, host: '0.0.0.0' });
    app.log.info(`🚀 MCP Tools HTTP Server running on http://localhost:${port}`);
    app.log.info(`📡 MCP endpoint: http://localhost:${port}/mcp`);
    app.log.info(`💡 For full functionality, use stdio mode: node dist/index.js`);
    return app;
  } catch (err) {
    app.log.error('Failed to start server:', err);
    process.exit(1);
  }
}