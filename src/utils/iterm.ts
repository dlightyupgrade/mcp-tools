/**
 * iTerm2 Automation Utilities
 * 
 * Utilities for creating and managing iTerm2 panes for workstream execution
 */

import { execSync } from 'child_process';

export interface WorkstreamPane {
  workstreamId: string;
  paneId: string;
  title: string;
  command: string;
}

/**
 * Create a new iTerm2 tab for workstream execution
 */
export async function createWorkstreamPane(
  command: string,
  title: string,
  workstreamId: string
): Promise<WorkstreamPane> {
  const appleScript = `
    tell application "iTerm2"
      tell current window
        create tab with default profile
        tell current session of current tab
          set name to "${title}"
          write text "# ${title}"
          write text "# Workstream ID: ${workstreamId}"
          write text "# Started: $(date)"
          write text ""
          write text "${command}"
        end tell
      end tell
    end tell
  `;

  try {
    execSync(`osascript -e '${appleScript.replace(/'/g, "\\'")}'`, { encoding: 'utf8' });
    
    return {
      workstreamId,
      paneId: `iterm_${workstreamId}`,
      title,
      command
    };
  } catch (error) {
    throw new Error(`Failed to create iTerm2 pane: ${error}`);
  }
}

/**
 * Check if iTerm2 is available
 */
export function isITermAvailable(): boolean {
  try {
    execSync('osascript -e "tell application \\"iTerm2\\" to get version"', { encoding: 'utf8' });
    return true;
  } catch {
    return false;
  }
}

/**
 * Send text to a specific iTerm2 session
 */
export function sendToITermSession(sessionId: string, text: string): void {
  const appleScript = `
    tell application "iTerm2"
      tell session id "${sessionId}"
        write text "${text}"
      end tell
    end tell
  `;
  
  try {
    execSync(`osascript -e '${appleScript.replace(/'/g, "\\'")}'`, { encoding: 'utf8' });
  } catch (error) {
    throw new Error(`Failed to send text to iTerm2 session: ${error}`);
  }
}

/**
 * Generate workstream ID
 */
export function generateWorkstreamId(): string {
  return `ws_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`;
}