/**
 * Input Validation Utilities
 * 
 * Comprehensive validation functions for MCP tool inputs
 * Provides consistent error messages and validation logic
 */

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

/**
 * Validate GitHub PR URL format
 */
export function validatePRUrl(url: any): ValidationResult {
  const errors: string[] = [];
  
  if (!url) {
    errors.push('PR URL is required');
    return { isValid: false, errors };
  }
  
  if (typeof url !== 'string') {
    errors.push('PR URL must be a string');
    return { isValid: false, errors };
  }
  
  const githubPRPattern = /^https:\/\/github\.com\/[^\/]+\/[^\/]+\/pull\/\d+$/;
  if (!githubPRPattern.test(url)) {
    errors.push('PR URL must be a valid GitHub PR URL (https://github.com/owner/repo/pull/number)');
  }
  
  return { isValid: errors.length === 0, errors };
}

/**
 * Validate command string for new_ws tool
 */
export function validateCommand(command: any): ValidationResult {
  const errors: string[] = [];
  
  if (!command) {
    errors.push('Command is required');
    return { isValid: false, errors };
  }
  
  if (typeof command !== 'string') {
    errors.push('Command must be a string');
    return { isValid: false, errors };
  }
  
  if (command.trim().length === 0) {
    errors.push('Command cannot be empty');
  }
  
  // Basic command injection protection
  const dangerousPatterns = [';', '&&', '||', '|', '`', '$', '(', ')', '{', '}'];
  for (const pattern of dangerousPatterns) {
    if (command.includes(pattern)) {
      errors.push(`Command contains potentially dangerous character: ${pattern}`);
    }
  }
  
  return { isValid: errors.length === 0, errors };
}

/**
 * Validate optional description field
 */
export function validateDescription(description: any): ValidationResult {
  const errors: string[] = [];
  
  if (description !== undefined && description !== null) {
    if (typeof description !== 'string') {
      errors.push('Description must be a string');
    } else if (description.length > 500) {
      errors.push('Description must be less than 500 characters');
    }
  }
  
  return { isValid: errors.length === 0, errors };
}

/**
 * Validate text input for echo tool
 */
export function validateText(text: any): ValidationResult {
  const errors: string[] = [];
  
  if (!text) {
    errors.push('Text is required');
    return { isValid: false, errors };
  }
  
  if (typeof text !== 'string') {
    errors.push('Text must be a string');
    return { isValid: false, errors };
  }
  
  if (text.length > 1000) {
    errors.push('Text must be less than 1000 characters');
  }
  
  return { isValid: errors.length === 0, errors };
}

/**
 * Comprehensive tool argument validation
 */
export function validateToolArguments(toolName: string, args: any): ValidationResult {
  const errors: string[] = [];
  
  if (!args || typeof args !== 'object') {
    errors.push('Tool arguments must be provided as an object');
    return { isValid: false, errors };
  }
  
  switch (toolName) {
    case 'new_ws':
      const commandValidation = validateCommand(args.command);
      if (!commandValidation.isValid) {
        errors.push(...commandValidation.errors);
      }
      
      const descValidation = validateDescription(args.description);
      if (!descValidation.isValid) {
        errors.push(...descValidation.errors);
      }
      break;
      
    case 'pr_violations':
    case 'code_review':
    case 'deploy_approval':
      const urlValidation = validatePRUrl(args.pr_url);
      if (!urlValidation.isValid) {
        errors.push(...urlValidation.errors);
      }
      
      const descValidation2 = validateDescription(args.description);
      if (!descValidation2.isValid) {
        errors.push(...descValidation2.errors);
      }
      break;
      
    case 'morning_workflow':
      const descValidation3 = validateDescription(args.description);
      if (!descValidation3.isValid) {
        errors.push(...descValidation3.errors);
      }
      break;
      
    case 'echo':
      const textValidation = validateText(args.text);
      if (!textValidation.isValid) {
        errors.push(...textValidation.errors);
      }
      break;
      
    case 'get_system_info':
      // No validation needed for system info
      break;
      
    default:
      errors.push(`Unknown tool: ${toolName}`);
      break;
  }
  
  return { isValid: errors.length === 0, errors };
}

/**
 * Create a standardized validation error message
 */
export function createValidationErrorMessage(toolName: string, errors: string[]): string {
  return `Validation failed for tool '${toolName}': ${errors.join(', ')}`;
}