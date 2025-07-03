/**
 * MCP Streaming HTTP Server Implementation
 * 
 * Implements MCP 2025-03-26 specification with streaming HTTP transport
 * Container-ready with full MCP protocol support over HTTP
 */

import fastify, { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { 
  McpError,
  ErrorCode 
} from '@modelcontextprotocol/sdk/types.js';

interface MCPRequest {
  jsonrpc: '2.0';
  id?: string | number | null;
  method: string;
  params?: any;
}

interface MCPResponse {
  jsonrpc: '2.0';
  id?: string | number | null;
  result?: any;
  error?: {
    code: number;
    message: string;
    data?: any;
  };
}

export async function createHTTPServer(port: number): Promise<FastifyInstance> {
  const app = fastify({
    logger: {
      level: 'info',
    },
  });

  // Enable CORS for browser access
  await app.register(import('@fastify/cors'), {
    origin: true,
    credentials: true,
  });

  // Health check endpoint
  app.get('/health', async () => {
    return { 
      status: 'healthy', 
      service: 'mcp-tools',
      version: '1.0.0',
      transport: 'Streaming HTTP',
      specification: '2025-03-26',
      timestamp: new Date().toISOString(),
    };
  });

  // MCP server capabilities discovery
  app.get('/mcp', async () => {
    return {
      service: 'mcp-tools',
      version: '1.0.0',
      protocol: 'Model Context Protocol',
      transport: 'Streaming HTTP',
      specification: '2025-03-26',
      capabilities: {
        tools: {},
        resources: {},
      },
      tools: [
        {
          name: 'pr_violations',
          description: 'Analyze PR violations, open threads, CI failures, and merge conflicts',
          parameters: ['pr_url', 'description?']
        },
        {
          name: 'code_review',
          description: 'Perform comprehensive code quality review of a PR',
          parameters: ['pr_url', 'description?']
        },
        {
          name: 'morning_workflow',
          description: 'Execute daily morning workflow automation',
          parameters: ['description?']
        },
        {
          name: 'deploy_approval',
          description: 'Generate deployment approval message for Slack',
          parameters: ['pr_url', 'description?']
        },
        {
          name: 'echo',
          description: 'Echo back input text',
          parameters: ['text']
        },
        {
          name: 'get_system_info',
          description: 'Get system information',
          parameters: []
        }
      ],
      endpoints: {
        mcp: '/mcp',
        health: '/health',
        capabilities: '/capabilities'
      },
      timestamp: new Date().toISOString(),
    };
  });

  // MCP capabilities endpoint (JSON-RPC 2.0 compatible)
  app.get('/capabilities', async () => {
    return {
      jsonrpc: '2.0',
      result: {
        capabilities: {
          tools: {},
          resources: {},
        },
        serverInfo: {
          name: 'mcp-tools',
          version: '1.0.0',
        },
        protocolVersion: '2025-03-26',
      },
    };
  });

  // Main MCP endpoint - handles JSON-RPC 2.0 requests
  app.post('/mcp', async (request: FastifyRequest, reply: FastifyReply) => {
    reply.type('application/json');

    try {
      const mcpRequest = request.body as MCPRequest;

      // Validate JSON-RPC 2.0 format
      if (!mcpRequest || mcpRequest.jsonrpc !== '2.0' || !mcpRequest.method) {
        return createErrorResponse(null, -32600, 'Invalid Request');
      }

      // Handle MCP methods
      switch (mcpRequest.method) {
        case 'initialize':
          return createSuccessResponse(mcpRequest.id, {
            capabilities: {
              tools: {},
              resources: {},
            },
            serverInfo: {
              name: 'mcp-tools',
              version: '1.0.0',
            },
            protocolVersion: '2025-03-26',
          });

        case 'tools/list':
          return createSuccessResponse(mcpRequest.id, {
            tools: [
              {
                name: 'echo',
                description: 'Echo back the input text - useful for testing',
                inputSchema: {
                  type: 'object',
                  properties: {
                    text: {
                      type: 'string',
                      description: 'Text to echo back',
                    },
                  },
                  required: ['text'],
                },
              },
              {
                name: 'get_system_info',
                description: 'Get basic system information',
                inputSchema: {
                  type: 'object',
                  properties: {},
                },
              },
              {
                name: 'pr_violations',
                description: 'Analyze PR violations, open threads, CI failures, and merge conflicts',
                inputSchema: {
                  type: 'object',
                  properties: {
                    pr_url: {
                      type: 'string',
                      description: 'GitHub PR URL to analyze',
                    },
                    description: {
                      type: 'string',
                      description: 'Optional description of the analysis task',
                    },
                  },
                  required: ['pr_url'],
                },
              },
              {
                name: 'code_review',
                description: 'Perform comprehensive code quality review of a PR',
                inputSchema: {
                  type: 'object',
                  properties: {
                    pr_url: {
                      type: 'string',
                      description: 'GitHub PR URL to review',
                    },
                    description: {
                      type: 'string',
                      description: 'Optional description of the review focus',
                    },
                  },
                  required: ['pr_url'],
                },
              },
              {
                name: 'morning_workflow',
                description: 'Execute daily morning workflow automation',
                inputSchema: {
                  type: 'object',
                  properties: {
                    description: {
                      type: 'string',
                      description: 'Optional description of workflow customization',
                    },
                  },
                },
              },
              {
                name: 'deploy_approval',
                description: 'Generate deployment approval message for Slack',
                inputSchema: {
                  type: 'object',
                  properties: {
                    pr_url: {
                      type: 'string',
                      description: 'GitHub PR URL for deployment',
                    },
                    description: {
                      type: 'string',
                      description: 'Optional deployment description',
                    },
                  },
                  required: ['pr_url'],
                },
              },
            ],
          });

        case 'tools/call':
          return await handleToolCall(mcpRequest);

        case 'ping':
          return createSuccessResponse(mcpRequest.id, { status: 'pong' });

        default:
          return createErrorResponse(mcpRequest.id, -32601, `Method not found: ${mcpRequest.method}`);
      }

    } catch (error) {
      app.log.error('Error processing MCP request:', error);
      return createErrorResponse(null, -32603, 'Internal error', error);
    }
  });

  // Server-Sent Events endpoint for streaming (future enhancement)
  app.get('/mcp/stream', async (request: FastifyRequest, reply: FastifyReply) => {
    reply.raw.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Headers': 'Cache-Control'
    });

    // Send initial connection message
    reply.raw.write(`data: ${JSON.stringify({
      type: 'connected',
      server: 'mcp-tools',
      version: '1.0.0',
      timestamp: new Date().toISOString()
    })}\n\n`);

    // Keep connection alive
    const heartbeat = setInterval(() => {
      reply.raw.write(`data: ${JSON.stringify({
        type: 'heartbeat',
        timestamp: new Date().toISOString()
      })}\n\n`);
    }, 30000);

    // Cleanup on connection close
    request.raw.on('close', () => {
      clearInterval(heartbeat);
    });
  });

  // Start the server
  try {
    await app.listen({ port, host: '0.0.0.0' });
    app.log.info(`🚀 MCP Tools Streaming HTTP Server running on http://localhost:${port}`);
    app.log.info(`📡 MCP endpoint: http://localhost:${port}/mcp`);
    app.log.info(`🐳 Container-ready with full MCP protocol support`);
    app.log.info(`✨ Streaming HTTP transport (MCP 2025-03-26 specification)`);
    return app;
  } catch (err) {
    app.log.error('Failed to start server:', err);
    process.exit(1);
  }
}

// Handle tool execution (imported from server.ts logic)
async function handleToolCall(mcpRequest: MCPRequest): Promise<MCPResponse> {
  try {
    const { name, arguments: args } = mcpRequest.params || {};
    
    if (!args) {
      return createErrorResponse(mcpRequest.id, -32602, 'Tool arguments are required');
    }

    let result: string;

    switch (name) {
      case 'echo':
        result = `Echo: ${args.text}`;
        break;

      case 'get_system_info':
        result = JSON.stringify({
          platform: process.platform,
          node_version: process.version,
          architecture: process.arch,
          uptime: process.uptime(),
          memory_usage: process.memoryUsage(),
          timestamp: new Date().toISOString(),
        }, null, 2);
        break;

      case 'pr_violations':
        result = await executePRViolationsCommand(args.pr_url, args.description);
        break;

      case 'code_review':
        result = await executeCodeReviewCommand(args.pr_url, args.description);
        break;

      case 'morning_workflow':
        result = await executeMorningWorkflowCommand(args.description);
        break;

      case 'deploy_approval':
        result = await executeDeployApprovalCommand(args.pr_url, args.description);
        break;

      default:
        return createErrorResponse(mcpRequest.id, -32601, `Unknown tool: ${name}`);
    }

    return createSuccessResponse(mcpRequest.id, {
      content: [
        {
          type: 'text',
          text: result,
        },
      ],
    });

  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    return createErrorResponse(mcpRequest.id, -32603, `Tool execution failed: ${errorMessage}`);
  }
}

// Tool execution functions (copied from server.ts)
async function executePRViolationsCommand(prUrl: string, description?: string): Promise<string> {
  const timestamp = new Date().toISOString();
  
  try {
    const { execSync } = await import('child_process');
    const command = `pr-violations-claude "${prUrl}"`;
    
    const result = execSync(command, { 
      encoding: 'utf8',
      cwd: process.env.HOME || '/Users/dlighty',
      env: { ...process.env, PATH: `${process.env.PATH}:/usr/local/bin:/opt/homebrew/bin` }
    });
    
    return JSON.stringify({
      status: 'success',
      command: 'pr_violations',
      pr_url: prUrl,
      description: description || 'PR violations analysis',
      timestamp: timestamp,
      result: result,
      message: 'PR violations analysis completed successfully'
    }, null, 2);
    
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    
    return JSON.stringify({
      status: 'error',
      command: 'pr_violations',
      pr_url: prUrl,
      description: description,
      timestamp: timestamp,
      error: errorMessage,
      message: `PR violations analysis failed: ${errorMessage}`
    }, null, 2);
  }
}

async function executeCodeReviewCommand(prUrl: string, description?: string): Promise<string> {
  const timestamp = new Date().toISOString();
  
  try {
    const { execSync } = await import('child_process');
    const command = `code-review-claude "${prUrl}"`;
    
    const result = execSync(command, { 
      encoding: 'utf8',
      cwd: process.env.HOME || '/Users/dlighty',
      env: { ...process.env, PATH: `${process.env.PATH}:/usr/local/bin:/opt/homebrew/bin` }
    });
    
    return JSON.stringify({
      status: 'success',
      command: 'code_review',
      pr_url: prUrl,
      description: description || 'Code review analysis',
      timestamp: timestamp,
      result: result,
      message: 'Code review completed successfully'
    }, null, 2);
    
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    
    return JSON.stringify({
      status: 'error',
      command: 'code_review',
      pr_url: prUrl,
      description: description,
      timestamp: timestamp,
      error: errorMessage,
      message: `Code review failed: ${errorMessage}`
    }, null, 2);
  }
}

async function executeMorningWorkflowCommand(description?: string): Promise<string> {
  const timestamp = new Date().toISOString();
  
  try {
    const { execSync } = await import('child_process');
    const command = 'morning-workflow-claude';
    
    const result = execSync(command, { 
      encoding: 'utf8',
      cwd: process.env.HOME || '/Users/dlighty',
      env: { ...process.env, PATH: `${process.env.PATH}:/usr/local/bin:/opt/homebrew/bin` }
    });
    
    return JSON.stringify({
      status: 'success',
      command: 'morning_workflow',
      description: description || 'Daily morning workflow automation',
      timestamp: timestamp,
      result: result,
      message: 'Morning workflow completed successfully'
    }, null, 2);
    
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    
    return JSON.stringify({
      status: 'error',
      command: 'morning_workflow',
      description: description,
      timestamp: timestamp,
      error: errorMessage,
      message: `Morning workflow failed: ${errorMessage}`
    }, null, 2);
  }
}

async function executeDeployApprovalCommand(prUrl: string, description?: string): Promise<string> {
  const timestamp = new Date().toISOString();
  
  try {
    const { execSync } = await import('child_process');
    const command = `deployment-diff-claude "${prUrl}"`;
    
    const result = execSync(command, { 
      encoding: 'utf8',
      cwd: process.env.HOME || '/Users/dlighty',
      env: { ...process.env, PATH: `${process.env.PATH}:/usr/local/bin:/opt/homebrew/bin` }
    });
    
    return JSON.stringify({
      status: 'success',
      command: 'deploy_approval',
      pr_url: prUrl,
      description: description || 'Deployment approval message generation',
      timestamp: timestamp,
      result: result,
      message: 'Deployment approval message generated successfully'
    }, null, 2);
    
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    
    return JSON.stringify({
      status: 'error',
      command: 'deploy_approval',
      pr_url: prUrl,
      description: description,
      timestamp: timestamp,
      error: errorMessage,
      message: `Deployment approval failed: ${errorMessage}`
    }, null, 2);
  }
}

// Helper functions for JSON-RPC 2.0 responses
function createSuccessResponse(id: string | number | null | undefined, result: any): MCPResponse {
  return {
    jsonrpc: '2.0',
    id: id || null,
    result,
  };
}

function createErrorResponse(
  id: string | number | null | undefined, 
  code: number, 
  message: string, 
  data?: any
): MCPResponse {
  return {
    jsonrpc: '2.0',
    id: id || null,
    error: {
      code,
      message,
      ...(data && { data }),
    },
  };
}