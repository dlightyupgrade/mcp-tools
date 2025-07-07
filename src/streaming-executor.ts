/**
 * Streaming Tool Executor - Replaces synchronous execSync with streaming execution
 * 
 * Based on MCP-RAG patterns for asynchronous tool execution with progress tracking
 */

import { spawn, ChildProcess } from 'child_process';
import { EventEmitter } from 'events';
import { CorrelatedRequest, StreamingResponse } from './session-manager.js';

export interface ExecutionProgress {
  type: 'stdout' | 'stderr' | 'progress' | 'complete' | 'error';
  data: string;
  timestamp: string;
  exitCode?: number;
}

export interface ExecutionOptions {
  cwd?: string;
  env?: Record<string, string>;
  timeout?: number;
  maxOutputSize?: number;
  shell?: boolean;
}

export interface ExecutionResult {
  success: boolean;
  exitCode: number;
  stdout: string;
  stderr: string;
  executionTime: number;
  error?: Error;
}

export class StreamingExecutor extends EventEmitter {
  private activeExecutions = new Map<string, ChildProcess>();
  private executionResults = new Map<string, ExecutionResult>();

  /**
   * Execute a command with streaming output
   */
  async executeStreaming(
    correlatedRequest: CorrelatedRequest,
    command: string,
    args: string[] = [],
    options: ExecutionOptions = {}
  ): Promise<void> {
    const { requestId, correlationId } = correlatedRequest;
    const startTime = Date.now();

    try {
      // Set up execution options
      const execOptions = {
        cwd: options.cwd || process.cwd(),
        env: { ...process.env, ...options.env },
        shell: options.shell !== false // Default to true for shell execution
      };

      // Start the child process
      const childProcess = spawn(command, args, execOptions);
      this.activeExecutions.set(requestId, childProcess);

      // Set up timeout if specified
      let timeoutHandle: NodeJS.Timeout | undefined;
      if (options.timeout) {
        timeoutHandle = setTimeout(() => {
          this.cancelExecution(requestId);
          this.emitProgress(correlatedRequest, {
            type: 'error',
            data: `Execution timed out after ${options.timeout}ms`,
            timestamp: new Date().toISOString()
          });
        }, options.timeout);
      }

      // Track output sizes to prevent memory issues
      let stdoutSize = 0;
      let stderrSize = 0;
      const maxSize = options.maxOutputSize || 10 * 1024 * 1024; // 10MB default

      let stdout = '';
      let stderr = '';

      // Handle stdout
      childProcess.stdout?.on('data', (data: Buffer) => {
        const chunk = data.toString();
        stdoutSize += chunk.length;

        if (stdoutSize > maxSize) {
          this.cancelExecution(requestId);
          this.emitProgress(correlatedRequest, {
            type: 'error',
            data: `Output size exceeded maximum of ${maxSize} bytes`,
            timestamp: new Date().toISOString()
          });
          return;
        }

        stdout += chunk;
        this.emitProgress(correlatedRequest, {
          type: 'stdout',
          data: chunk,
          timestamp: new Date().toISOString()
        });
      });

      // Handle stderr
      childProcess.stderr?.on('data', (data: Buffer) => {
        const chunk = data.toString();
        stderrSize += chunk.length;

        if (stderrSize > maxSize) {
          this.cancelExecution(requestId);
          this.emitProgress(correlatedRequest, {
            type: 'error',
            data: `Error output size exceeded maximum of ${maxSize} bytes`,
            timestamp: new Date().toISOString()
          });
          return;
        }

        stderr += chunk;
        this.emitProgress(correlatedRequest, {
          type: 'stderr',
          data: chunk,
          timestamp: new Date().toISOString()
        });
      });

      // Handle process completion
      childProcess.on('close', (exitCode: number | null) => {
        if (timeoutHandle) {
          clearTimeout(timeoutHandle);
        }

        this.activeExecutions.delete(requestId);
        const executionTime = Date.now() - startTime;

        const result: ExecutionResult = {
          success: exitCode === 0,
          exitCode: exitCode || -1,
          stdout,
          stderr,
          executionTime
        };

        this.executionResults.set(requestId, result);

        this.emitProgress(correlatedRequest, {
          type: 'complete',
          data: JSON.stringify(result),
          timestamp: new Date().toISOString(),
          exitCode: exitCode || -1
        });

        this.emit('executionComplete', correlatedRequest, result);
      });

      // Handle process errors
      childProcess.on('error', (error: Error) => {
        if (timeoutHandle) {
          clearTimeout(timeoutHandle);
        }

        this.activeExecutions.delete(requestId);
        const executionTime = Date.now() - startTime;

        const result: ExecutionResult = {
          success: false,
          exitCode: -1,
          stdout,
          stderr,
          executionTime,
          error
        };

        this.executionResults.set(requestId, result);

        this.emitProgress(correlatedRequest, {
          type: 'error',
          data: error.message,
          timestamp: new Date().toISOString()
        });

        this.emit('executionError', correlatedRequest, error);
      });

      // Handle abort signal from session
      correlatedRequest.controller?.signal.addEventListener('abort', () => {
        this.cancelExecution(requestId);
      });

    } catch (error) {
      this.emitProgress(correlatedRequest, {
        type: 'error',
        data: error instanceof Error ? error.message : String(error),
        timestamp: new Date().toISOString()
      });

      this.emit('executionError', correlatedRequest, error);
    }
  }

  /**
   * Cancel an active execution
   */
  cancelExecution(requestId: string): boolean {
    const childProcess = this.activeExecutions.get(requestId);
    if (childProcess) {
      childProcess.kill('SIGTERM');
      
      // Force kill after 5 seconds
      setTimeout(() => {
        if (this.activeExecutions.has(requestId)) {
          childProcess.kill('SIGKILL');
          this.activeExecutions.delete(requestId);
        }
      }, 5000);

      return true;
    }
    return false;
  }

  /**
   * Get execution result
   */
  getExecutionResult(requestId: string): ExecutionResult | undefined {
    return this.executionResults.get(requestId);
  }

  /**
   * Check if execution is active
   */
  isExecutionActive(requestId: string): boolean {
    return this.activeExecutions.has(requestId);
  }

  /**
   * Get all active executions
   */
  getActiveExecutions(): string[] {
    return Array.from(this.activeExecutions.keys());
  }

  /**
   * Emit progress update
   */
  private emitProgress(correlatedRequest: CorrelatedRequest, progress: ExecutionProgress): void {
    const response: StreamingResponse = {
      sessionId: correlatedRequest.sessionId,
      requestId: correlatedRequest.requestId,
      correlationId: correlatedRequest.correlationId,
      type: progress.type === 'complete' ? 'complete' : 'progress',
      data: {
        progress,
        tool: correlatedRequest.tool,
        args: correlatedRequest.args
      },
      timestamp: progress.timestamp
    };

    this.emit('progress', response);
  }

  /**
   * Clean up completed executions to prevent memory leaks
   */
  cleanup(): void {
    // Cancel all active executions
    for (const requestId of this.activeExecutions.keys()) {
      this.cancelExecution(requestId);
    }

    // Clear results cache
    this.executionResults.clear();
  }

  /**
   * Get executor statistics
   */
  getStats() {
    return {
      activeExecutions: this.activeExecutions.size,
      completedExecutions: this.executionResults.size,
      totalMemoryUsage: this.calculateMemoryUsage()
    };
  }

  private calculateMemoryUsage(): number {
    let totalSize = 0;
    for (const result of this.executionResults.values()) {
      totalSize += result.stdout.length + result.stderr.length;
    }
    return totalSize;
  }
}

/**
 * Utility functions for common CLI tool patterns
 */
export class ToolExecutionHelper {
  constructor(private executor: StreamingExecutor) {}

  /**
   * Execute bash command with streaming
   */
  async executeBash(correlatedRequest: CorrelatedRequest, command: string, options: ExecutionOptions = {}): Promise<void> {
    return this.executor.executeStreaming(
      correlatedRequest,
      'bash',
      ['-c', command],
      { shell: true, ...options }
    );
  }

  /**
   * Execute git command with streaming
   */
  async executeGit(correlatedRequest: CorrelatedRequest, args: string[], options: ExecutionOptions = {}): Promise<void> {
    return this.executor.executeStreaming(
      correlatedRequest,
      'git',
      args,
      options
    );
  }

  /**
   * Execute npm command with streaming
   */
  async executeNpm(correlatedRequest: CorrelatedRequest, args: string[], options: ExecutionOptions = {}): Promise<void> {
    return this.executor.executeStreaming(
      correlatedRequest,
      'npm',
      args,
      options
    );
  }

  /**
   * Execute grep with streaming
   */
  async executeGrep(correlatedRequest: CorrelatedRequest, pattern: string, files: string[], options: ExecutionOptions = {}): Promise<void> {
    const args = [pattern, ...files];
    return this.executor.executeStreaming(
      correlatedRequest,
      'grep',
      args,
      options
    );
  }

  /**
   * Execute find command with streaming
   */
  async executeFind(correlatedRequest: CorrelatedRequest, path: string, expression: string[], options: ExecutionOptions = {}): Promise<void> {
    const args = [path, ...expression];
    return this.executor.executeStreaming(
      correlatedRequest,
      'find',
      args,
      options
    );
  }
}

/**
 * Global streaming executor instance
 */
export const globalStreamingExecutor = new StreamingExecutor();
export const globalToolHelper = new ToolExecutionHelper(globalStreamingExecutor);