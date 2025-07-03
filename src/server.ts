/**
 * MCP Server Configuration
 * 
 * Core MCP server setup with tool registration and resource management
 * Implements MCP specification 2025-03-26 with streaming support
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import {
  ListToolsRequestSchema,
  CallToolRequestSchema,
  ErrorCode,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';

import { setupBasicTools } from './tools/basic-tools.js';
import { setupNewWSTools } from './tools/new-ws-tools.js';

export function createMCPServer(): Server {
  const server = new Server(
    {
      name: 'mcp-tools',
      version: '1.0.0',
    },
    {
      capabilities: {
        tools: {},
        resources: {},
      },
    }
  );

  // Register basic utility tools
  setupBasicTools(server);
  
  // Register new_ws integration tools
  setupNewWSTools(server);

  // Handle tool listing
  server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
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
          name: 'new_ws',
          description: 'Launch a new workstream command in iTerm2',
          inputSchema: {
            type: 'object',
            properties: {
              command: {
                type: 'string',
                description: 'The workstream command to execute (e.g., "pr_violations <URL>", "code_review <URL>", "morning_workflow")',
              },
              description: {
                type: 'string',
                description: 'Optional description of the workstream task',
              },
            },
            required: ['command'],
          },
        },
      ],
    };
  });

  // Handle tool execution
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;
    
    if (!args) {
      throw new McpError(
        ErrorCode.InvalidParams,
        'Tool arguments are required'
      );
    }

    try {
      switch (name) {
        case 'echo':
          return {
            content: [
              {
                type: 'text',
                text: `Echo: ${(args as any).text}`,
              },
            ],
          };

        case 'get_system_info':
          return {
            content: [
              {
                type: 'text',
                text: JSON.stringify({
                  platform: process.platform,
                  node_version: process.version,
                  architecture: process.arch,
                  uptime: process.uptime(),
                  memory_usage: process.memoryUsage(),
                  timestamp: new Date().toISOString(),
                }, null, 2),
              },
            ],
          };

        case 'new_ws':
          // Execute new_ws workstream command
          const result = await executeNewWSCommand((args as any).command, (args as any).description);
          return {
            content: [
              {
                type: 'text',
                text: result,
              },
            ],
          };

        default:
          throw new McpError(
            ErrorCode.MethodNotFound,
            `Unknown tool: ${name}`
          );
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      throw new McpError(
        ErrorCode.InternalError,
        `Tool execution failed: ${errorMessage}`
      );
    }
  });

  return server;
}

/**
 * Execute new_ws workstream command
 * Integrates with existing new_ws infrastructure
 */
async function executeNewWSCommand(command: string, description?: string): Promise<string> {
  const timestamp = new Date().toISOString();
  
  try {
    // Parse the command to extract command type and parameters
    const parsedCommand = parseNewWSCommand(command);
    
    // Execute the workstream launch
    const launchResult = await launchWorkstream(parsedCommand, description);
    
    return JSON.stringify({
      status: 'success',
      command: command,
      parsed_command: parsedCommand,
      description: description || 'No description provided',
      timestamp: timestamp,
      workstream_id: launchResult.workstreamId,
      iterm_pane: launchResult.paneId,
      message: `Successfully launched workstream: ${parsedCommand.type}`,
      next_steps: [
        'Workstream executing in new iTerm2 pane',
        'Claude session initialized with appropriate context',
        'Monitor progress in dedicated pane',
        'Results will be tracked in session'
      ]
    }, null, 2);
    
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    
    return JSON.stringify({
      status: 'error',
      command: command,
      description: description,
      timestamp: timestamp,
      error: errorMessage,
      message: `Failed to launch workstream: ${errorMessage}`,
      troubleshooting: [
        'Verify iTerm2 is installed and accessible',
        'Check that required tools are in PATH',
        'Ensure command syntax is correct',
        'Review available workstream commands'
      ]
    }, null, 2);
  }
}

/**
 * Parse new_ws command into structured format
 */
function parseNewWSCommand(command: string): { type: string; parameters: string[]; url?: string } {
  const parts = command.trim().split(/\s+/);
  const type = parts[0];
  const parameters = parts.slice(1);
  
  // Extract URL if present
  const urlPattern = /https:\/\/github\.com\/[^\/]+\/[^\/]+\/pull\/\d+/;
  const url = parameters.find(param => urlPattern.test(param));
  
  return {
    type,
    parameters,
    url
  };
}

/**
 * Launch workstream in iTerm2 with appropriate setup
 */
async function launchWorkstream(parsedCommand: { type: string; parameters: string[]; url?: string }, description?: string): Promise<{ workstreamId: string; paneId: string }> {
  const { execSync } = await import('child_process');
  const workstreamId = `ws_${Date.now()}`;
  
  // Construct the command to execute
  let executeCommand = '';
  
  switch (parsedCommand.type) {
    case 'pr_violations':
      if (parsedCommand.url) {
        executeCommand = `pr-violations-claude "${parsedCommand.url}"`;
      } else {
        throw new Error('pr_violations requires a GitHub PR URL');
      }
      break;
      
    case 'code_review':
      if (parsedCommand.url) {
        executeCommand = `code-review-claude "${parsedCommand.url}"`;
      } else {
        throw new Error('code_review requires a GitHub PR URL');
      }
      break;
      
    case 'morning_workflow':
      executeCommand = 'morning-workflow-claude';
      break;
      
    case 'deploy_approval':
      if (parsedCommand.url) {
        executeCommand = `deployment-diff-claude "${parsedCommand.url}"`;
      } else {
        throw new Error('deploy_approval requires a GitHub PR URL');
      }
      break;
      
    default:
      // Generic command execution
      executeCommand = parsedCommand.parameters.join(' ');
      break;
  }
  
  // Create AppleScript to launch new iTerm2 pane
  const title = description ? `${parsedCommand.type}: ${description}` : `${parsedCommand.type}`;
  const appleScript = `
    tell application "iTerm2"
      tell current window
        create tab with default profile
        tell current session of current tab
          write text "# ${title}"
          write text "# Workstream ID: ${workstreamId}"
          write text "${executeCommand}"
        end tell
      end tell
    end tell
  `;
  
  try {
    // Execute AppleScript to create new pane
    execSync(`osascript -e '${appleScript.replace(/'/g, "\\'")}'`, { encoding: 'utf8' });
    
    return {
      workstreamId,
      paneId: `iterm_${workstreamId}`
    };
  } catch (error) {
    throw new Error(`Failed to create iTerm2 pane: ${error}`);
  }
}