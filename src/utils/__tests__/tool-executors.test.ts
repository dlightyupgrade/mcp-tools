/**
 * Tool Executors Tests
 * 
 * Integration tests for tool execution functions
 */

import {
  executePRViolationsCommand,
  executeCodeReviewCommand,
  executeMorningWorkflowCommand,
  executeDeployApprovalCommand,
  executeNewWSCommand
} from '../tool-executors.js';

// Mock child_process for testing
jest.mock('child_process', () => ({
  execSync: jest.fn()
}));

import { execSync } from 'child_process';
const mockExecSync = execSync as jest.MockedFunction<typeof execSync>;

describe('Tool Executors', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('executePRViolationsCommand', () => {
    it('should execute pr-violations-claude command successfully', async () => {
      const mockOutput = 'PR violations analysis output';
      mockExecSync.mockReturnValue(mockOutput as any);

      const result = await executePRViolationsCommand(
        'https://github.com/owner/repo/pull/123',
        'Test analysis'
      );

      const parsedResult = JSON.parse(result);
      expect(parsedResult.status).toBe('success');
      expect(parsedResult.command).toBe('pr_violations');
      expect(parsedResult.pr_url).toBe('https://github.com/owner/repo/pull/123');
      expect(parsedResult.description).toBe('Test analysis');
      expect(parsedResult.result).toBe(mockOutput);
      
      expect(mockExecSync).toHaveBeenCalledWith(
        'pr-violations-claude "https://github.com/owner/repo/pull/123"',
        expect.any(Object)
      );
    });

    it('should handle command execution errors', async () => {
      mockExecSync.mockImplementation(() => {
        throw new Error('Command failed');
      });

      const result = await executePRViolationsCommand(
        'https://github.com/owner/repo/pull/123'
      );

      const parsedResult = JSON.parse(result);
      expect(parsedResult.status).toBe('error');
      expect(parsedResult.error).toBe('Command failed');
    });
  });

  describe('executeCodeReviewCommand', () => {
    it('should execute code-review-claude command successfully', async () => {
      const mockOutput = 'Code review output';
      mockExecSync.mockReturnValue(mockOutput as any);

      const result = await executeCodeReviewCommand(
        'https://github.com/owner/repo/pull/123'
      );

      const parsedResult = JSON.parse(result);
      expect(parsedResult.status).toBe('success');
      expect(parsedResult.command).toBe('code_review');
      
      expect(mockExecSync).toHaveBeenCalledWith(
        'code-review-claude "https://github.com/owner/repo/pull/123"',
        expect.any(Object)
      );
    });
  });

  describe('executeMorningWorkflowCommand', () => {
    it('should execute morning-workflow-claude command successfully', async () => {
      const mockOutput = 'Morning workflow output';
      mockExecSync.mockReturnValue(mockOutput as any);

      const result = await executeMorningWorkflowCommand('Daily workflow');

      const parsedResult = JSON.parse(result);
      expect(parsedResult.status).toBe('success');
      expect(parsedResult.command).toBe('morning_workflow');
      
      expect(mockExecSync).toHaveBeenCalledWith(
        'morning-workflow-claude',
        expect.any(Object)
      );
    });
  });

  describe('executeDeployApprovalCommand', () => {
    it('should execute deployment-diff-claude command successfully', async () => {
      const mockOutput = 'Deployment approval output';
      mockExecSync.mockReturnValue(mockOutput as any);

      const result = await executeDeployApprovalCommand(
        'https://github.com/owner/repo/pull/123'
      );

      const parsedResult = JSON.parse(result);
      expect(parsedResult.status).toBe('success');
      expect(parsedResult.command).toBe('deploy_approval');
      
      expect(mockExecSync).toHaveBeenCalledWith(
        'deployment-diff-claude "https://github.com/owner/repo/pull/123"',
        expect.any(Object)
      );
    });
  });

  describe('executeNewWSCommand', () => {
    it('should check for wclds command existence', async () => {
      // Mock the test command to succeed (wclds exists)
      mockExecSync
        .mockReturnValueOnce('' as any) // test -x command succeeds
        .mockReturnValueOnce('Workstream launched' as any); // wclds execution

      const result = await executeNewWSCommand('pr_violations', 'Test workstream');

      const parsedResult = JSON.parse(result);
      expect(parsedResult.status).toBe('success');
      expect(parsedResult.command).toBe('new_ws');
      expect(parsedResult.workstream_command).toBe('pr_violations');
      
      expect(mockExecSync).toHaveBeenCalledTimes(2);
    });

    it('should handle missing wclds command', async () => {
      // Mock the test command to fail (wclds doesn't exist)
      mockExecSync.mockImplementation(() => {
        throw new Error('Command not found');
      });

      const result = await executeNewWSCommand('pr_violations');

      const parsedResult = JSON.parse(result);
      expect(parsedResult.status).toBe('error');
      expect(parsedResult.error).toBe('wclds command not found or not executable');
    });
  });

  describe('Command execution environment', () => {
    it('should use correct execution options', async () => {
      mockExecSync.mockReturnValue('success' as any);

      await executePRViolationsCommand('https://github.com/owner/repo/pull/123');

      expect(mockExecSync).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          encoding: 'utf8',
          cwd: expect.any(String),
          env: expect.objectContaining({
            PATH: expect.stringContaining('/usr/local/bin:/opt/homebrew/bin')
          })
        })
      );
    });
  });
});