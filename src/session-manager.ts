/**
 * Session Management System - Based on MCP-RAG FastMCP patterns
 * 
 * Provides session lifecycle management, request correlation, and state tracking
 * for HTTP streaming sessions in mcp-tools.
 */

import { EventEmitter } from 'events';
import { randomUUID } from 'crypto';

export interface CorrelatedRequest {
  sessionId: string;
  requestId: string;
  correlationId: string;
  startTime: Date;
  tool: string;
  args: any;
  controller?: AbortController;
}

export interface StreamingResponse {
  sessionId: string;
  requestId: string;
  correlationId: string;
  type: 'progress' | 'result' | 'error' | 'complete';
  data: any;
  timestamp: string;
}

export interface SessionConfig {
  maxIdleTimeMs: number;
  maxActiveRequests: number;
  enableEventStore: boolean;
}

export class Session extends EventEmitter {
  public readonly id: string;
  public readonly createdAt: Date;
  public lastActivity: Date;
  private activeRequests = new Map<string, CorrelatedRequest>();
  private requestHistory: CorrelatedRequest[] = [];
  private config: SessionConfig;

  constructor(id: string, config: SessionConfig) {
    super();
    this.id = id;
    this.createdAt = new Date();
    this.lastActivity = new Date();
    this.config = config;
  }

  /**
   * Create a new correlated request for this session
   */
  createRequest(tool: string, args: any): CorrelatedRequest {
    const requestId = randomUUID();
    const correlationId = `${this.id}-${requestId.substring(0, 8)}`;
    
    const request: CorrelatedRequest = {
      sessionId: this.id,
      requestId,
      correlationId,
      startTime: new Date(),
      tool,
      args,
      controller: new AbortController()
    };

    if (this.activeRequests.size >= this.config.maxActiveRequests) {
      throw new Error(`Session ${this.id} has reached maximum active requests (${this.config.maxActiveRequests})`);
    }

    this.activeRequests.set(requestId, request);
    this.updateActivity();
    
    this.emit('requestCreated', request);
    return request;
  }

  /**
   * Complete a request and move it to history
   */
  completeRequest(requestId: string): void {
    const request = this.activeRequests.get(requestId);
    if (request) {
      this.activeRequests.delete(requestId);
      this.requestHistory.push(request);
      this.updateActivity();
      this.emit('requestCompleted', request);
    }
  }

  /**
   * Cancel a request
   */
  cancelRequest(requestId: string): void {
    const request = this.activeRequests.get(requestId);
    if (request) {
      request.controller?.abort();
      this.activeRequests.delete(requestId);
      this.updateActivity();
      this.emit('requestCancelled', request);
    }
  }

  /**
   * Get active request by ID
   */
  getActiveRequest(requestId: string): CorrelatedRequest | undefined {
    return this.activeRequests.get(requestId);
  }

  /**
   * Get all active requests
   */
  getActiveRequests(): CorrelatedRequest[] {
    return Array.from(this.activeRequests.values());
  }

  /**
   * Check if session is idle (no active requests and past idle timeout)
   */
  isIdle(): boolean {
    if (this.activeRequests.size > 0) {
      return false;
    }
    
    const idleTime = Date.now() - this.lastActivity.getTime();
    return idleTime > this.config.maxIdleTimeMs;
  }

  /**
   * Cancel all active requests and clean up
   */
  cleanup(): void {
    for (const request of this.activeRequests.values()) {
      request.controller?.abort();
    }
    this.activeRequests.clear();
    this.emit('cleanup');
  }

  private updateActivity(): void {
    this.lastActivity = new Date();
  }

  /**
   * Get session statistics
   */
  getStats() {
    return {
      id: this.id,
      createdAt: this.createdAt,
      lastActivity: this.lastActivity,
      activeRequests: this.activeRequests.size,
      totalRequests: this.requestHistory.length + this.activeRequests.size,
      isIdle: this.isIdle()
    };
  }
}

export class SessionManager extends EventEmitter {
  private sessions = new Map<string, Session>();
  private cleanupInterval: NodeJS.Timeout;
  private defaultConfig: SessionConfig;

  constructor(config: Partial<SessionConfig> = {}) {
    super();
    
    this.defaultConfig = {
      maxIdleTimeMs: 30 * 60 * 1000, // 30 minutes
      maxActiveRequests: 10,
      enableEventStore: false,
      ...config
    };

    // Start cleanup process
    this.cleanupInterval = setInterval(() => {
      this.cleanupExpiredSessions();
    }, 60 * 1000); // Check every minute
  }

  /**
   * Create a new session
   */
  createSession(config?: Partial<SessionConfig>): Session {
    const sessionId = randomUUID();
    const sessionConfig = { ...this.defaultConfig, ...config };
    const session = new Session(sessionId, sessionConfig);
    
    this.sessions.set(sessionId, session);
    this.emit('sessionCreated', session);
    
    return session;
  }

  /**
   * Get session by ID
   */
  getSession(sessionId: string): Session | null {
    return this.sessions.get(sessionId) || null;
  }

  /**
   * Get session by request ID (searches all sessions)
   */
  getSessionByRequestId(requestId: string): Session | null {
    for (const session of this.sessions.values()) {
      if (session.getActiveRequest(requestId)) {
        return session;
      }
    }
    return null;
  }

  /**
   * Delete a session and clean up its resources
   */
  deleteSession(sessionId: string): boolean {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.cleanup();
      this.sessions.delete(sessionId);
      this.emit('sessionDeleted', session);
      return true;
    }
    return false;
  }

  /**
   * Clean up expired sessions
   */
  cleanupExpiredSessions(): void {
    const expiredSessions: string[] = [];
    
    for (const [sessionId, session] of this.sessions.entries()) {
      if (session.isIdle()) {
        expiredSessions.push(sessionId);
      }
    }

    for (const sessionId of expiredSessions) {
      this.deleteSession(sessionId);
    }

    if (expiredSessions.length > 0) {
      this.emit('sessionsExpired', expiredSessions);
    }
  }

  /**
   * Get all active sessions
   */
  getActiveSessions(): Session[] {
    return Array.from(this.sessions.values());
  }

  /**
   * Get manager statistics
   */
  getStats() {
    const sessions = Array.from(this.sessions.values());
    return {
      totalSessions: sessions.length,
      activeSessions: sessions.filter(s => !s.isIdle()).length,
      idleSessions: sessions.filter(s => s.isIdle()).length,
      totalActiveRequests: sessions.reduce((sum, s) => sum + s.getActiveRequests().length, 0)
    };
  }

  /**
   * Shutdown the session manager
   */
  shutdown(): void {
    clearInterval(this.cleanupInterval);
    
    // Cleanup all sessions
    for (const session of this.sessions.values()) {
      session.cleanup();
    }
    this.sessions.clear();
    
    this.emit('shutdown');
  }
}

/**
 * Global session manager instance
 */
export const globalSessionManager = new SessionManager();

/**
 * Utility function to validate session ID format (matches MCP-RAG pattern)
 */
export function isValidSessionId(sessionId: string): boolean {
  // Visible ASCII characters only (matches MCP-RAG pattern)
  const SESSION_ID_PATTERN = /^[\x21-\x7E]+$/;
  return SESSION_ID_PATTERN.test(sessionId) && sessionId.length >= 8 && sessionId.length <= 128;
}

/**
 * HTTP headers for session management
 */
export const MCP_SESSION_ID_HEADER = 'Mcp-Session-Id';
export const MCP_REQUEST_ID_HEADER = 'Mcp-Request-Id';
export const MCP_CORRELATION_ID_HEADER = 'Mcp-Correlation-Id';