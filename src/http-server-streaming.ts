/**
 * MCP Streamable HTTP Server Implementation
 * 
 * Implements MCP 2024-11-05 Streamable HTTP transport specification
 * Replaces the previous HTTP+SSE transport with proper session management
 */

import fastify, { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { randomUUID } from 'crypto';
import { 
  globalSessionManager, 
  Session, 
  MCP_SESSION_ID_HEADER,
  MCP_REQUEST_ID_HEADER,
  MCP_CORRELATION_ID_HEADER,
  isValidSessionId 
} from './session-manager.js';
import { 
  globalStreamingExecutor, 
  globalToolHelper 
} from './streaming-executor.js';
import { 
  validateToolArguments, 
  createValidationErrorMessage 
} from './utils/validation.js';

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

interface StreamableHttpHeaders {
  sessionId?: string;
  requestId?: string;
  correlationId?: string;
  origin?: string;
  accept?: string;
  lastEventId?: string;
  authorization?: string;
}

export async function createStreamableHTTPServer(port: number): Promise<FastifyInstance> {
  const app = fastify({
    logger: {
      level: 'info',
    },
  });

  // Enable CORS - allow all origins for simple HTTP streaming
  await app.register(import('@fastify/cors'), {
    origin: true,  // Allow all origins
    credentials: false,  // No credentials needed
  });

  // No form parsing needed - simple HTTP streaming only

  // Health check endpoint
  app.get('/health', async () => {
    return { 
      status: 'healthy', 
      service: 'mcp-tools',
      version: '1.0.0',
      transport: 'Streamable HTTP',
      specification: '2024-11-05',
      timestamp: new Date().toISOString(),
      sessions: globalSessionManager.getStats()
    };
  });

  // MCP server capabilities discovery
  app.get('/mcp', async (request: FastifyRequest, reply: FastifyReply) => {
    const headers = extractHeaders(request);
    
    // If session ID provided, try to establish/resume SSE stream
    if (headers.sessionId) {
      return handleSSEStream(request, reply, headers);
    }

    // Otherwise return basic capabilities
    return {
      service: 'mcp-tools',
      version: '1.0.0',
      protocol: 'Model Context Protocol',
      transport: 'Streamable HTTP',
      specification: '2024-11-05',
      capabilities: {
        tools: {
          listChanged: false
        },
        resources: {
          subscribe: false,
          listChanged: false
        },
        prompts: {
          listChanged: false
        }
      },
      tools: getAvailableTools(),
      endpoints: {
        mcp: '/mcp',
        health: '/health',
      },
      timestamp: new Date().toISOString(),
    };
  });

  // Add redirect for trailing slash
  app.post('/mcp/', async (request: FastifyRequest, reply: FastifyReply) => {
    // Redirect to /mcp without trailing slash
    return app.inject({
      method: 'POST',
      url: '/mcp',
      headers: request.headers,
      payload: request.body as any
    }).then(response => {
      reply.code(response.statusCode);
      reply.headers(response.headers);
      return response.body;
    });
  });

  // No OAuth endpoints - simple HTTP streaming only

  // Main MCP endpoint - handles JSON-RPC 2.0 requests (POST) and SSE streams (GET)
  app.post('/mcp', async (request: FastifyRequest, reply: FastifyReply) => {
    const headers = extractHeaders(request);
    
    try {
      // Validate request format
      const mcpRequest = request.body as MCPRequest;
      if (!mcpRequest || mcpRequest.jsonrpc !== '2.0' || !mcpRequest.method) {
        return createErrorResponse(null, -32600, 'Invalid Request');
      }

      // Check if client accepts streaming
      const acceptsSSE = headers.accept?.includes('text/event-stream') || false;
      const acceptsJSON = headers.accept?.includes('application/json') || false;

      // Handle session management
      const session = await handleSessionManagement(headers, mcpRequest, reply);
      if (!session) {
        return createErrorResponse(mcpRequest.id, -32603, 'Session management failed');
      }

      // Handle different MCP methods
      switch (mcpRequest.method) {
        case 'initialize':
          return handleInitialize(mcpRequest, reply, session, acceptsSSE);

        case 'tools/list':
          return createSuccessResponse(mcpRequest.id, {
            tools: getAvailableTools().map(tool => ({
              name: tool.name,
              description: tool.description,
              inputSchema: tool.inputSchema || {
                type: 'object',
                properties: {},
              },
            }))
          });

        case 'resources/list':
          return createSuccessResponse(mcpRequest.id, {
            resources: []
          });

        case 'prompts/list':
          return createSuccessResponse(mcpRequest.id, {
            prompts: []
          });

        case 'tools/call':
          // Tool calls can be streaming or non-streaming based on Accept header
          if (acceptsSSE) {
            return handleStreamingToolCall(mcpRequest, reply, session);
          } else {
            return handleDirectToolCall(mcpRequest, session);
          }

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

  // OPTIONS endpoint for CORS preflight (MCP spec compliance)
  app.options('/mcp', async (request: FastifyRequest, reply: FastifyReply) => {
    reply.code(204);
    reply.header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS');
    reply.header('Access-Control-Allow-Headers', 'Content-Type, Accept, Authorization, Mcp-Session-Id, Mcp-Request-Id, Mcp-Correlation-Id');
    reply.header('Access-Control-Max-Age', '86400'); // 24 hours
    return;
  });

  // Session management endpoint
  app.delete('/mcp', async (request: FastifyRequest, reply: FastifyReply) => {
    const headers = extractHeaders(request);
    
    if (headers.sessionId && globalSessionManager.getSession(headers.sessionId)) {
      globalSessionManager.deleteSession(headers.sessionId);
      reply.code(200);
      return { message: 'Session terminated' };
    }
    
    reply.code(404);
    return { error: 'Session not found' };
  });

  // Setup streaming executor event handlers
  setupStreamingHandlers(app);

  // Start the server
  try {
    await app.listen({ port, host: '0.0.0.0' });
    app.log.info(`🚀 MCP Tools Streamable HTTP Server running on http://localhost:${port}`);
    app.log.info(`📡 MCP endpoint: http://localhost:${port}/mcp`);
    app.log.info(`✨ Streamable HTTP transport (MCP 2024-11-05 specification)`);
    return app;
  } catch (err) {
    app.log.error('Failed to start server:', err);
    process.exit(1);
  }
}

/**
 * Extract and validate headers according to MCP spec
 */
function extractHeaders(request: FastifyRequest): StreamableHttpHeaders {
  const headers = request.headers as Record<string, string>;
  
  return {
    sessionId: headers[MCP_SESSION_ID_HEADER.toLowerCase()],
    requestId: headers[MCP_REQUEST_ID_HEADER.toLowerCase()],
    correlationId: headers[MCP_CORRELATION_ID_HEADER.toLowerCase()],
    origin: headers.origin,
    accept: headers.accept,
    lastEventId: headers['last-event-id'],
    authorization: headers.authorization
  };
}

/**
 * Handle session management - simplified, no authentication required
 */
async function handleSessionManagement(
  headers: StreamableHttpHeaders,
  mcpRequest: MCPRequest,
  reply: FastifyReply
): Promise<Session | null> {
  try {
    let session: Session;

    if (headers.sessionId) {
      // Get existing session or create new one if not found
      const existingSession = globalSessionManager.getSession(headers.sessionId);
      if (existingSession) {
        session = existingSession;
      } else {
        // Create new session if the provided ID doesn't exist
        session = globalSessionManager.createSession();
        reply.header(MCP_SESSION_ID_HEADER, session.id);
      }
    } else {
      // Always create new session if no session ID provided
      session = globalSessionManager.createSession();
      reply.header(MCP_SESSION_ID_HEADER, session.id);
    }

    return session;
  } catch (error) {
    app.log.error('Session management error:', error);
    // Even on error, create a new session to keep things working
    const session = globalSessionManager.createSession();
    reply.header(MCP_SESSION_ID_HEADER, session.id);
    return session;
  }
}

/**
 * Handle initialize request with optional streaming response
 */
async function handleInitialize(
  mcpRequest: MCPRequest,
  reply: FastifyReply,
  session: Session,
  acceptsSSE: boolean
): Promise<MCPResponse> {
  const response = {
    capabilities: {
      tools: {
        listChanged: false
      },
      resources: {
        subscribe: false,
        listChanged: false
      },
      prompts: {
        listChanged: false
      }
    },
    serverInfo: {
      name: 'mcp-tools',
      version: '1.0.0',
    },
    protocolVersion: '2024-11-05',
  };

  // Set session header for new sessions
  reply.header(MCP_SESSION_ID_HEADER, session.id);

  return createSuccessResponse(mcpRequest.id, response);
}

/**
 * Handle Server-Sent Events stream for session
 */
async function handleSSEStream(
  request: FastifyRequest,
  reply: FastifyReply,
  headers: StreamableHttpHeaders
): Promise<void> {
  const session = globalSessionManager.getSession(headers.sessionId!);
  if (!session) {
    reply.code(400);
    return reply.send({ error: 'Invalid session ID' });
  }

  // Set up SSE headers
  reply.raw.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache, no-transform',
    'Connection': 'keep-alive',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Cache-Control',
    [MCP_SESSION_ID_HEADER]: session.id
  });

  // Send initial connection message
  writeSSEMessage(reply, {
    type: 'connected',
    sessionId: session.id,
    server: 'mcp-tools',
    version: '1.0.0',
    timestamp: new Date().toISOString()
  });

  // Handle session events
  const eventHandler = (eventType: string, data: any) => {
    writeSSEMessage(reply, {
      type: eventType,
      sessionId: session.id,
      data,
      timestamp: new Date().toISOString()
    });
  };

  session.on('requestCreated', (req) => eventHandler('requestCreated', req));
  session.on('requestCompleted', (req) => eventHandler('requestCompleted', req));
  session.on('requestCancelled', (req) => eventHandler('requestCancelled', req));

  // Handle streaming executor events for this session
  const progressHandler = (response: any) => {
    if (response.sessionId === session.id) {
      writeSSEMessage(reply, response, response.correlationId);
    }
  };

  globalStreamingExecutor.on('progress', progressHandler);

  // Cleanup on connection close
  request.raw.on('close', () => {
    session.off('requestCreated', eventHandler);
    session.off('requestCompleted', eventHandler);
    session.off('requestCancelled', eventHandler);
    globalStreamingExecutor.off('progress', progressHandler);
  });

  // Keep connection alive with heartbeat
  const heartbeatInterval = setInterval(() => {
    if (!reply.raw.destroyed) {
      writeSSEMessage(reply, {
        type: 'heartbeat',
        timestamp: new Date().toISOString()
      });
    } else {
      clearInterval(heartbeatInterval);
    }
  }, 30000);

  request.raw.on('close', () => {
    clearInterval(heartbeatInterval);
  });
}

/**
 * Handle streaming tool call with SSE response
 */
async function handleStreamingToolCall(
  mcpRequest: MCPRequest,
  reply: FastifyReply,
  session: Session
): Promise<void> {
  const { name, arguments: args } = mcpRequest.params || {};
  
  // Validate tool arguments
  const validation = validateToolArguments(name, args);
  if (!validation.isValid) {
    reply.code(400);
    return reply.send(createErrorResponse(
      mcpRequest.id, 
      -32602, 
      createValidationErrorMessage(name, validation.errors)
    ));
  }

  // Create correlated request
  const correlatedRequest = session.createRequest(name, args);

  // Set up SSE response
  reply.raw.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache, no-transform',
    'Connection': 'keep-alive',
    [MCP_SESSION_ID_HEADER]: session.id,
    [MCP_REQUEST_ID_HEADER]: correlatedRequest.requestId,
    [MCP_CORRELATION_ID_HEADER]: correlatedRequest.correlationId
  });

  // Send initial message
  writeSSEMessage(reply, {
    type: 'tool_call_started',
    tool: name,
    requestId: correlatedRequest.requestId,
    correlationId: correlatedRequest.correlationId,
    timestamp: new Date().toISOString()
  }, correlatedRequest.correlationId);

  // Execute tool with streaming
  try {
    await executeToolStreaming(correlatedRequest, name, args);
  } catch (error) {
    writeSSEMessage(reply, {
      type: 'error',
      error: error instanceof Error ? error.message : String(error),
      timestamp: new Date().toISOString()
    }, correlatedRequest.correlationId);
  }

  // The actual progress will be sent via the streaming executor events
  // This function just sets up the SSE stream
}

/**
 * Handle direct (non-streaming) tool call
 */
async function handleDirectToolCall(
  mcpRequest: MCPRequest,
  session: Session
): Promise<MCPResponse> {
  const { name, arguments: args } = mcpRequest.params || {};
  
  // Validate tool arguments
  const validation = validateToolArguments(name, args);
  if (!validation.isValid) {
    return createErrorResponse(
      mcpRequest.id, 
      -32602, 
      createValidationErrorMessage(name, validation.errors)
    );
  }

  try {
    // For non-streaming, we'll need to collect all output
    // This is a simplified implementation - in practice you might want
    // to still use the streaming executor but collect results
    const result = await executeToolDirect(name, args);
    
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

/**
 * Execute tool with streaming output
 */
async function executeToolStreaming(
  correlatedRequest: any,
  toolName: string,
  args: any
): Promise<void> {
  switch (toolName) {
    case 'echo':
      // Simple echo - send immediate result
      globalStreamingExecutor.emit('progress', {
        sessionId: correlatedRequest.sessionId,
        requestId: correlatedRequest.requestId,
        correlationId: correlatedRequest.correlationId,
        type: 'complete',
        data: {
          content: [{ type: 'text', text: `Echo: ${args.text}` }]
        },
        timestamp: new Date().toISOString()
      });
      break;

    case 'get_system_info':
      // System info - send immediate result
      globalStreamingExecutor.emit('progress', {
        sessionId: correlatedRequest.sessionId,
        requestId: correlatedRequest.requestId,
        correlationId: correlatedRequest.correlationId,
        type: 'complete',
        data: {
          content: [{ 
            type: 'text', 
            text: JSON.stringify({
              platform: process.platform,
              node_version: process.version,
              architecture: process.arch,
              uptime: process.uptime(),
              memory_usage: process.memoryUsage(),
              timestamp: new Date().toISOString(),
            }, null, 2)
          }]
        },
        timestamp: new Date().toISOString()
      });
      break;

    case 'pr_violations':
      await globalToolHelper.executeBash(
        correlatedRequest,
        `pr-violations-claude "${args.pr_url}"`
      );
      break;

    case 'code_review':
      await globalToolHelper.executeBash(
        correlatedRequest,
        `code-review-claude "${args.pr_url}"`
      );
      break;

    case 'morning_workflow':
      await globalToolHelper.executeBash(
        correlatedRequest,
        'morning-workflow-claude'
      );
      break;

    case 'deploy_approval':
      await globalToolHelper.executeBash(
        correlatedRequest,
        `deployment-diff-claude "${args.pr_url}"`
      );
      break;

    case 'new_ws':
      await globalToolHelper.executeBash(
        correlatedRequest,
        `wclds "${args.command}"`
      );
      break;

    default:
      throw new Error(`Unknown tool: ${toolName}`);
  }
}

/**
 * Execute tool directly (non-streaming) - simplified fallback
 */
async function executeToolDirect(toolName: string, args: any): Promise<string> {
  // This is a simplified implementation for non-streaming clients
  // In practice, you might want more sophisticated handling
  
  switch (toolName) {
    case 'echo':
      return `Echo: ${args.text}`;
      
    case 'get_system_info':
      return JSON.stringify({
        platform: process.platform,
        node_version: process.version,
        architecture: process.arch,
        uptime: process.uptime(),
        memory_usage: process.memoryUsage(),
        timestamp: new Date().toISOString(),
      }, null, 2);
      
    default:
      throw new Error(`Direct execution not supported for tool: ${toolName}`);
  }
}

/**
 * Write SSE message with proper formatting
 */
function writeSSEMessage(reply: FastifyReply, data: any, eventId?: string): void {
  if (reply.raw.destroyed) return;

  if (eventId) {
    reply.raw.write(`id: ${eventId}\n`);
  }
  
  reply.raw.write(`data: ${JSON.stringify(data)}\n\n`);
}

/**
 * Get available tools definition
 */
function getAvailableTools() {
  return [
    {
      name: 'new_ws',
      description: 'Launch a new workstream command in iTerm2',
      parameters: ['command', 'description?'],
      inputSchema: {
        type: 'object',
        properties: {
          command: { type: 'string', description: 'The workstream command to execute' },
          description: { type: 'string', description: 'Optional description of the workstream' }
        },
        required: ['command']
      }
    },
    {
      name: 'pr_violations',
      description: 'Analyze PR violations, open threads, CI failures, and merge conflicts',
      parameters: ['pr_url', 'description?'],
      inputSchema: {
        type: 'object',
        properties: {
          pr_url: { type: 'string', description: 'GitHub PR URL to analyze' },
          description: { type: 'string', description: 'Optional description of the analysis task' }
        },
        required: ['pr_url']
      }
    },
    {
      name: 'code_review',
      description: 'Perform comprehensive code quality review of a PR',
      parameters: ['pr_url', 'description?'],
      inputSchema: {
        type: 'object',
        properties: {
          pr_url: { type: 'string', description: 'GitHub PR URL to review' },
          description: { type: 'string', description: 'Optional description of the review focus' }
        },
        required: ['pr_url']
      }
    },
    {
      name: 'morning_workflow',
      description: 'Execute daily morning workflow automation',
      parameters: ['description?'],
      inputSchema: {
        type: 'object',
        properties: {
          description: { type: 'string', description: 'Optional description of workflow customization' }
        }
      }
    },
    {
      name: 'deploy_approval',
      description: 'Generate deployment approval message for Slack',
      parameters: ['pr_url', 'description?'],
      inputSchema: {
        type: 'object',
        properties: {
          pr_url: { type: 'string', description: 'GitHub PR URL for deployment' },
          description: { type: 'string', description: 'Optional deployment description' }
        },
        required: ['pr_url']
      }
    },
    {
      name: 'echo',
      description: 'Echo back input text',
      parameters: ['text'],
      inputSchema: {
        type: 'object',
        properties: {
          text: { type: 'string', description: 'Text to echo back' }
        },
        required: ['text']
      }
    },
    {
      name: 'get_system_info',
      description: 'Get system information',
      parameters: [],
      inputSchema: {
        type: 'object',
        properties: {}
      }
    }
  ];
}

/**
 * Setup streaming executor event handlers
 */
function setupStreamingHandlers(app: FastifyInstance): void {
  globalStreamingExecutor.on('executionComplete', (correlatedRequest, result) => {
    app.log.info(`Tool execution completed: ${correlatedRequest.tool} (${correlatedRequest.correlationId})`);
  });

  globalStreamingExecutor.on('executionError', (correlatedRequest, error) => {
    app.log.error(`Tool execution error: ${correlatedRequest.tool} (${correlatedRequest.correlationId})`, error);
  });

  // Cleanup expired sessions periodically
  setInterval(() => {
    globalSessionManager.cleanupExpiredSessions();
  }, 60000); // Every minute
}

/**
 * Helper functions for JSON-RPC 2.0 responses
 */
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