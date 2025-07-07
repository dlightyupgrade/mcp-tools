/**
 * Validation Utilities Tests
 * 
 * Unit tests for input validation functions
 */

import {
  validatePRUrl,
  validateCommand,
  validateDescription,
  validateText,
  validateToolArguments,
  createValidationErrorMessage
} from '../validation.js';

describe('Validation Utilities', () => {
  describe('validatePRUrl', () => {
    it('should validate correct GitHub PR URLs', () => {
      const validUrls = [
        'https://github.com/owner/repo/pull/123',
        'https://github.com/Credify/loan-servicing-srvc/pull/5315',
        'https://github.com/test-org/test-repo/pull/1'
      ];

      validUrls.forEach(url => {
        const result = validatePRUrl(url);
        expect(result.isValid).toBe(true);
        expect(result.errors).toHaveLength(0);
      });
    });

    it('should reject invalid PR URLs', () => {
      const invalidUrls = [
        '',
        null,
        undefined,
        'not-a-url',
        'https://github.com/owner/repo',
        'https://github.com/owner/repo/issues/123',
        'https://gitlab.com/owner/repo/pull/123'
      ];

      invalidUrls.forEach(url => {
        const result = validatePRUrl(url);
        expect(result.isValid).toBe(false);
        expect(result.errors.length).toBeGreaterThan(0);
      });
    });
  });

  describe('validateCommand', () => {
    it('should validate safe commands', () => {
      const validCommands = [
        'pr_violations',
        'code_review',
        'morning_workflow',
        'deploy_approval',
        'simple command'
      ];

      validCommands.forEach(command => {
        const result = validateCommand(command);
        expect(result.isValid).toBe(true);
        expect(result.errors).toHaveLength(0);
      });
    });

    it('should reject dangerous commands', () => {
      const dangerousCommands = [
        'rm -rf /',
        'command; rm file',
        'cmd && malicious',
        'echo `whoami`',
        'test$(dangerous)',
        'cmd{danger}'
      ];

      dangerousCommands.forEach(command => {
        const result = validateCommand(command);
        expect(result.isValid).toBe(false);
        expect(result.errors.length).toBeGreaterThan(0);
      });
    });

    it('should reject empty or invalid commands', () => {
      const invalidCommands = [
        '',
        '   ',
        null,
        undefined,
        123
      ];

      invalidCommands.forEach(command => {
        const result = validateCommand(command);
        expect(result.isValid).toBe(false);
        expect(result.errors.length).toBeGreaterThan(0);
      });
    });
  });

  describe('validateDescription', () => {
    it('should allow valid descriptions', () => {
      const validDescriptions = [
        undefined,
        null,
        'A simple description',
        'Short desc',
        'A'.repeat(500) // exactly 500 chars
      ];

      validDescriptions.forEach(desc => {
        const result = validateDescription(desc);
        expect(result.isValid).toBe(true);
        expect(result.errors).toHaveLength(0);
      });
    });

    it('should reject invalid descriptions', () => {
      const invalidDescriptions = [
        123,
        [],
        {},
        'A'.repeat(501) // too long
      ];

      invalidDescriptions.forEach(desc => {
        const result = validateDescription(desc);
        expect(result.isValid).toBe(false);
        expect(result.errors.length).toBeGreaterThan(0);
      });
    });
  });

  describe('validateText', () => {
    it('should validate text input', () => {
      const validTexts = [
        'Hello world',
        'A'.repeat(1000) // exactly 1000 chars
      ];

      validTexts.forEach(text => {
        const result = validateText(text);
        expect(result.isValid).toBe(true);
        expect(result.errors).toHaveLength(0);
      });
    });

    it('should reject invalid text', () => {
      const invalidTexts = [
        '',
        null,
        undefined,
        123,
        'A'.repeat(1001) // too long
      ];

      invalidTexts.forEach(text => {
        const result = validateText(text);
        expect(result.isValid).toBe(false);
        expect(result.errors.length).toBeGreaterThan(0);
      });
    });
  });

  describe('validateToolArguments', () => {
    it('should validate pr_violations tool arguments', () => {
      const validArgs = {
        pr_url: 'https://github.com/owner/repo/pull/123',
        description: 'Test description'
      };

      const result = validateToolArguments('pr_violations', validArgs);
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should validate new_ws tool arguments', () => {
      const validArgs = {
        command: 'pr_violations',
        description: 'Test workstream'
      };

      const result = validateToolArguments('new_ws', validArgs);
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should validate echo tool arguments', () => {
      const validArgs = {
        text: 'Hello world'
      };

      const result = validateToolArguments('echo', validArgs);
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should reject invalid tool arguments', () => {
      const invalidScenarios = [
        { tool: 'pr_violations', args: { pr_url: 'invalid-url' } },
        { tool: 'new_ws', args: { command: 'dangerous; command' } },
        { tool: 'echo', args: { text: '' } },
        { tool: 'unknown_tool', args: {} }
      ];

      invalidScenarios.forEach(scenario => {
        const result = validateToolArguments(scenario.tool, scenario.args);
        expect(result.isValid).toBe(false);
        expect(result.errors.length).toBeGreaterThan(0);
      });
    });
  });

  describe('createValidationErrorMessage', () => {
    it('should create formatted error messages', () => {
      const errors = ['Error 1', 'Error 2'];
      const message = createValidationErrorMessage('test_tool', errors);
      
      expect(message).toBe("Validation failed for tool 'test_tool': Error 1, Error 2");
    });
  });
});