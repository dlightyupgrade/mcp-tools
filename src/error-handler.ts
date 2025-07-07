/**
 * Error Handling System for MCP Streamable HTTP Transport
 * 
 * Provides comprehensive error handling with session context and correlation
 */

import { FastifyRequest, FastifyReply } from 'fastify';
import { Session, CorrelatedRequest } from './session-manager.js';

export interface MCPError {
  code: number;
  message: string;
  data?: any;
  correlationId?: string;
  sessionId?: string;
  requestId?: string;
}

export interface ErrorContext {
  session?: Session;
  correlatedRequest?: CorrelatedRequest;
  request?: FastifyRequest;
  reply?: FastifyReply;
  tool?: string;
  method?: string;
}

// MCP Error Codes based on JSON-RPC 2.0 spec
export const MCPErrorCodes = {
  // JSON-RPC 2.0 standard errors
  PARSE_ERROR: -32700,
  INVALID_REQUEST: -32600,
  METHOD_NOT_FOUND: -32601,
  INVALID_PARAMS: -32602,
  INTERNAL_ERROR: -32603,
  
  // MCP-specific errors (application-defined range)
  SESSION_INVALID: -32000,
  SESSION_EXPIRED: -32001,
  SESSION_LIMIT_EXCEEDED: -32002,
  TOOL_EXECUTION_FAILED: -32010,
  TOOL_TIMEOUT: -32011,
  TOOL_CANCELLED: -32012,
  VALIDATION_FAILED: -32020,
  AUTHORIZATION_FAILED: -32030,
  RATE_LIMITED: -32040,
  STREAMING_ERROR: -32050,
  CORRELATION_FAILED: -32060,
} as const;

export class MCPErrorHandler {
  private static instance: MCPErrorHandler;

  static getInstance(): MCPErrorHandler {
    if (!MCPErrorHandler.instance) {
      MCPErrorHandler.instance = new MCPErrorHandler();
    }
    return MCPErrorHandler.instance;
  }

  /**
   * Handle session-related errors
   */
  handleSessionError(
    error: any, 
    context: ErrorContext
  ): MCPError {
    const baseError = this.createBaseError(error, context);

    if (error.message?.includes('session not found')) {
      return {
        ...baseError,
        code: MCPErrorCodes.SESSION_INVALID,
        message: 'Session not found or expired',
      };
    }

    if (error.message?.includes('maximum active requests')) {
      return {
        ...baseError,
        code: MCPErrorCodes.SESSION_LIMIT_EXCEEDED,
        message: 'Session has reached maximum active requests',
      };
    }

    if (error.message?.includes('session expired')) {
      return {
        ...baseError,
        code: MCPErrorCodes.SESSION_EXPIRED,
        message: 'Session has expired',
      };
    }

    return {
      ...baseError,
      code: MCPErrorCodes.INTERNAL_ERROR,
      message: 'Session management error',
    };
  }

  /**
   * Handle tool execution errors
   */
  handleToolError(
    error: any,
    context: ErrorContext
  ): MCPError {
    const baseError = this.createBaseError(error, context);

    if (error.message?.includes('timeout')) {
      return {
        ...baseError,
        code: MCPErrorCodes.TOOL_TIMEOUT,
        message: `Tool execution timed out: ${context.tool}`,
      };
    }

    if (error.message?.includes('cancelled') || error.message?.includes('aborted')) {
      return {
        ...baseError,
        code: MCPErrorCodes.TOOL_CANCELLED,
        message: `Tool execution cancelled: ${context.tool}`,
      };
    }

    if (error.code === 'ENOENT') {
      return {
        ...baseError,
        code: MCPErrorCodes.TOOL_EXECUTION_FAILED,
        message: `Tool not found or not executable: ${context.tool}`,
      };
    }

    if (error.code === 'EACCES') {
      return {
        ...baseError,
        code: MCPErrorCodes.AUTHORIZATION_FAILED,
        message: `Permission denied executing tool: ${context.tool}`,
      };
    }

    return {
      ...baseError,
      code: MCPErrorCodes.TOOL_EXECUTION_FAILED,
      message: `Tool execution failed: ${context.tool}`,
    };
  }

  /**
   * Handle validation errors
   */
  handleValidationError(
    error: any,
    context: ErrorContext
  ): MCPError {
    const baseError = this.createBaseError(error, context);

    return {
      ...baseError,
      code: MCPErrorCodes.VALIDATION_FAILED,
      message: 'Request validation failed',
      data: {
        tool: context.tool,
        validationErrors: error.validationErrors || [error.message]
      }
    };
  }

  /**
   * Handle streaming errors
   */
  handleStreamingError(
    error: any,
    context: ErrorContext
  ): MCPError {
    const baseError = this.createBaseError(error, context);

    if (error.message?.includes('connection closed')) {
      return {
        ...baseError,
        code: MCPErrorCodes.STREAMING_ERROR,
        message: 'Streaming connection closed unexpectedly',
      };
    }

    if (error.message?.includes('correlation')) {
      return {
        ...baseError,
        code: MCPErrorCodes.CORRELATION_FAILED,
        message: 'Request correlation failed',
      };
    }

    return {
      ...baseError,
      code: MCPErrorCodes.STREAMING_ERROR,
      message: 'Streaming operation failed',
    };
  }

  /**
   * Handle HTTP request/response errors
   */
  handleHTTPError(
    error: any,
    context: ErrorContext
  ): MCPError {
    const baseError = this.createBaseError(error, context);

    // Handle common HTTP errors
    if (error.statusCode) {
      switch (error.statusCode) {
        case 400:
          return {
            ...baseError,
            code: MCPErrorCodes.INVALID_REQUEST,
            message: 'Bad request format',
          };
        case 401:
          return {
            ...baseError,
            code: MCPErrorCodes.AUTHORIZATION_FAILED,
            message: 'Authentication required',
          };
        case 403:
          return {
            ...baseError,
            code: MCPErrorCodes.AUTHORIZATION_FAILED,
            message: 'Access denied',
          };
        case 429:
          return {
            ...baseError,
            code: MCPErrorCodes.RATE_LIMITED,
            message: 'Rate limit exceeded',
          };
        default:
          return {
            ...baseError,
            code: MCPErrorCodes.INTERNAL_ERROR,
            message: `HTTP error: ${error.statusCode}`,
          };
      }
    }

    return {
      ...baseError,
      code: MCPErrorCodes.INTERNAL_ERROR,
      message: 'HTTP request processing failed',
    };
  }

  /**
   * Handle JSON-RPC parsing errors
   */
  handleParseError(
    error: any,
    context: ErrorContext
  ): MCPError {
    const baseError = this.createBaseError(error, context);

    return {
      ...baseError,
      code: MCPErrorCodes.PARSE_ERROR,
      message: 'Invalid JSON-RPC request format',
    };
  }

  /**
   * Create base error with correlation information
   */
  private createBaseError(error: any, context: ErrorContext): MCPError {
    const timestamp = new Date().toISOString();
    
    return {
      code: MCPErrorCodes.INTERNAL_ERROR,
      message: error.message || 'Unknown error',
      correlationId: context.correlatedRequest?.correlationId,
      sessionId: context.session?.id,
      requestId: context.correlatedRequest?.requestId,
      data: {
        timestamp,
        originalError: error.name || error.constructor?.name,
        stack: process.env.NODE_ENV === 'development' ? error.stack : undefined,
        context: {
          tool: context.tool,
          method: context.method,
          requestPath: context.request?.url,
          userAgent: context.request?.headers['user-agent']
        }
      }
    };
  }

  /**
   * Convert MCPError to JSON-RPC error response
   */
  toJSONRPCError(mcpError: MCPError, id?: string | number | null): any {
    return {
      jsonrpc: '2.0',
      id: id || null,
      error: {
        code: mcpError.code,
        message: mcpError.message,
        data: mcpError.data
      }
    };
  }

  /**
   * Convert MCPError to SSE event
   */
  toSSEEvent(mcpError: MCPError): any {
    return {
      type: 'error',
      error: {
        code: mcpError.code,
        message: mcpError.message,
        correlationId: mcpError.correlationId,
        sessionId: mcpError.sessionId,
        requestId: mcpError.requestId
      },
      timestamp: new Date().toISOString(),
      data: mcpError.data
    };
  }

  /**
   * Log error with correlation context
   */
  logError(mcpError: MCPError, context: ErrorContext, logger: any): void {
    const logContext = {
      correlationId: mcpError.correlationId,
      sessionId: mcpError.sessionId,
      requestId: mcpError.requestId,
      tool: context.tool,
      method: context.method,
      errorCode: mcpError.code,
      timestamp: new Date().toISOString()
    };

    if (mcpError.code >= -32099 && mcpError.code <= -32000) {
      // Application-defined errors (MCP-specific)
      logger.warn(`MCP Error [${mcpError.code}]: ${mcpError.message}`, logContext);
    } else if (mcpError.code >= -32768 && mcpError.code <= -32000) {
      // JSON-RPC standard errors
      logger.error(`JSON-RPC Error [${mcpError.code}]: ${mcpError.message}`, logContext);
    } else {
      // Unknown error codes
      logger.error(`Unknown Error [${mcpError.code}]: ${mcpError.message}`, logContext);
    }
  }
}

/**
 * Global error handler instance
 */
export const globalErrorHandler = MCPErrorHandler.getInstance();

/**
 * Error handling middleware for Fastify
 */
export function createErrorMiddleware(logger: any) {
  return (error: any, request: FastifyRequest, reply: FastifyReply) => {
    const context: ErrorContext = {
      request,
      reply,
      method: (request.body as any)?.method
    };

    let mcpError: MCPError;

    // Determine error type and handle accordingly
    if (error.validation) {
      mcpError = globalErrorHandler.handleValidationError(error, context);
    } else if (error.statusCode) {
      mcpError = globalErrorHandler.handleHTTPError(error, context);
    } else if (error.message?.includes('JSON')) {
      mcpError = globalErrorHandler.handleParseError(error, context);
    } else {
      mcpError = globalErrorHandler.handleHTTPError(error, context);
    }

    // Log the error
    globalErrorHandler.logError(mcpError, context, logger);

    // Send error response
    reply.code(error.statusCode || 500);
    return globalErrorHandler.toJSONRPCError(mcpError);
  };
}

/**
 * Utility function to safely execute async operations with error handling
 */
export async function safeExecute<T>(
  operation: () => Promise<T>,
  context: ErrorContext,
  logger: any
): Promise<{ success: true; data: T } | { success: false; error: MCPError }> {
  try {
    const data = await operation();
    return { success: true, data };
  } catch (error) {
    let mcpError: MCPError;

    // Route to appropriate error handler based on context
    if (context.tool) {
      mcpError = globalErrorHandler.handleToolError(error, context);
    } else if (context.session) {
      mcpError = globalErrorHandler.handleSessionError(error, context);
    } else {
      mcpError = globalErrorHandler.handleHTTPError(error, context);
    }

    globalErrorHandler.logError(mcpError, context, logger);
    return { success: false, error: mcpError };
  }
}