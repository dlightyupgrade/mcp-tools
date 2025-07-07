/**
 * Shared Tool Executors
 * 
 * Common tool execution functions shared between stdio and HTTP transports
 * Eliminates code duplication and centralizes tool logic
 */

import { execSync } from 'child_process';

export interface ToolResult {
  status: 'success' | 'error';
  command: string;
  timestamp: string;
  result?: string;
  error?: string;
  message: string;
  [key: string]: any;
}

/**
 * Common execution environment for CLI tools
 */
const getExecOptions = () => ({
  encoding: 'utf8' as const,
  cwd: process.env.HOME || '/Users/dlighty',
  env: { 
    ...process.env, 
    PATH: `${process.env.PATH}:/usr/local/bin:/opt/homebrew/bin` 
  }
});

/**
 * Execute PR violations analysis command
 */
export async function executePRViolationsCommand(prUrl: string, description?: string): Promise<string> {
  const timestamp = new Date().toISOString();
  
  try {
    const command = `pr-violations-claude "${prUrl}"`;
    const result = execSync(command, getExecOptions());
    
    return JSON.stringify({
      status: 'success',
      command: 'pr_violations',
      pr_url: prUrl,
      description: description || 'PR violations analysis',
      timestamp,
      result: result.toString(),
      message: 'PR violations analysis completed successfully'
    } as ToolResult, null, 2);
    
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    
    return JSON.stringify({
      status: 'error',
      command: 'pr_violations',
      pr_url: prUrl,
      description,
      timestamp,
      error: errorMessage,
      message: `PR violations analysis failed: ${errorMessage}`
    } as ToolResult, null, 2);
  }
}

/**
 * Execute code review command
 */
export async function executeCodeReviewCommand(prUrl: string, description?: string): Promise<string> {
  const timestamp = new Date().toISOString();
  
  try {
    const command = `code-review-claude "${prUrl}"`;
    const result = execSync(command, getExecOptions());
    
    return JSON.stringify({
      status: 'success',
      command: 'code_review',
      pr_url: prUrl,
      description: description || 'Code review analysis',
      timestamp,
      result: result.toString(),
      message: 'Code review completed successfully'
    } as ToolResult, null, 2);
    
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    
    return JSON.stringify({
      status: 'error',
      command: 'code_review',
      pr_url: prUrl,
      description,
      timestamp,
      error: errorMessage,
      message: `Code review failed: ${errorMessage}`
    } as ToolResult, null, 2);
  }
}

/**
 * Execute morning workflow command
 */
export async function executeMorningWorkflowCommand(description?: string): Promise<string> {
  const timestamp = new Date().toISOString();
  
  try {
    const command = 'morning-workflow-claude';
    const result = execSync(command, getExecOptions());
    
    return JSON.stringify({
      status: 'success',
      command: 'morning_workflow',
      description: description || 'Daily morning workflow automation',
      timestamp,
      result: result.toString(),
      message: 'Morning workflow completed successfully'
    } as ToolResult, null, 2);
    
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    
    return JSON.stringify({
      status: 'error',
      command: 'morning_workflow',
      description,
      timestamp,
      error: errorMessage,
      message: `Morning workflow failed: ${errorMessage}`
    } as ToolResult, null, 2);
  }
}

/**
 * Execute deployment approval command
 */
export async function executeDeployApprovalCommand(prUrl: string, description?: string): Promise<string> {
  const timestamp = new Date().toISOString();
  
  try {
    const command = `deployment-diff-claude "${prUrl}"`;
    const result = execSync(command, getExecOptions());
    
    return JSON.stringify({
      status: 'success',
      command: 'deploy_approval',
      pr_url: prUrl,
      description: description || 'Deployment approval message generation',
      timestamp,
      result: result.toString(),
      message: 'Deployment approval message generated successfully'
    } as ToolResult, null, 2);
    
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    
    return JSON.stringify({
      status: 'error',
      command: 'deploy_approval',
      pr_url: prUrl,
      description,
      timestamp,
      error: errorMessage,
      message: `Deployment approval failed: ${errorMessage}`
    } as ToolResult, null, 2);
  }
}

/**
 * Execute new_ws workstream command
 */
export async function executeNewWSCommand(command: string, description?: string): Promise<string> {
  const timestamp = new Date().toISOString();
  
  try {
    // Check if wclds command exists
    const wclds_cmd = process.env.HOME + '/code/personal-dev-tools/cli/wclds';
    
    try {
      // Test if wclds exists and is executable
      execSync(`test -x "${wclds_cmd}"`, getExecOptions());
    } catch {
      return JSON.stringify({
        status: 'error',
        command: 'new_ws',
        workstream_command: command,
        description,
        timestamp,
        error: 'wclds command not found or not executable',
        message: 'wclds tool not available at expected location: ' + wclds_cmd
      } as ToolResult, null, 2);
    }
    
    // Execute wclds with the provided command
    const fullCommand = `"${wclds_cmd}" "${command}"`;
    const result = execSync(fullCommand, getExecOptions());
    
    return JSON.stringify({
      status: 'success',
      command: 'new_ws',
      workstream_command: command,
      description: description || 'New workstream launched',
      timestamp,
      result: result.toString(),
      message: `Successfully launched workstream: ${command}`
    } as ToolResult, null, 2);
    
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    
    return JSON.stringify({
      status: 'error',
      command: 'new_ws',
      workstream_command: command,
      description,
      timestamp,
      error: errorMessage,
      message: `New workstream launch failed: ${errorMessage}`
    } as ToolResult, null, 2);
  }
}