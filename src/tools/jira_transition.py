#!/usr/bin/env python3
"""
JIRA Transition Tool

Automatically perform JIRA ticket transitions using Atlassian MCP.
Provides intelligent workflow management with status aliases and embedded knowledge.
"""

import logging
from typing import Dict, Any

from fastmcp import FastMCP
from .base import ToolBase
from config.settings import Config

logger = logging.getLogger(__name__)


def register_jira_transition_tool(mcp: FastMCP):
    """Register the jira_transition tool with the FastMCP server"""
    
    @mcp.tool
    def jira_transition(ticket_id: str, target_state: str, description: str = "", current_status: str = "") -> Dict[str, Any]:
        """
        Automatically perform JIRA ticket transitions using Atlassian MCP.
        
        Natural language triggers: "jt", "jira transition", "move jira ticket to", 
        "transition ticket to", "change ticket status", "set jira status"
        
        Workflow:
        1. Gets current ticket status via Atlassian MCP
        2. Resolves target state aliases (e.g., 'dev' -> 'In Development')  
        3. Gets available transitions from JIRA
        4. Executes the appropriate transition
        5. Verifies final status
        
        Args:
            ticket_id: JIRA ticket ID (e.g., SI-8748, PROJ-123)
            target_state: Target JIRA status (full name or alias like 'dev', 'qa', 'done')
            description: Optional description or context for the transition
            current_status: Current JIRA status (if provided, returns specific transition path)
            
        Returns:
            Dictionary containing structured instructions for Claude Code to execute
        """
        logger.info(f"JIRA auto-transition (MCP): {ticket_id} -> {target_state}")
        
        try:
            # Validate inputs
            if not ticket_id or not ticket_id.strip():
                raise ValueError("Ticket ID cannot be empty")
            
            if not target_state or not target_state.strip():
                raise ValueError("Target state cannot be empty")
            
            # Clean inputs
            ticket_id = ticket_id.strip()
            target_state = target_state.strip()
            cloud_id = Config.JIRA_CLOUD_ID
            
            # Embedded JIRA workflow knowledge and status aliases
            status_aliases = {
                "In Development": ["dev", "development", "start", "begin", "work", "code"],
                "Ready For Codereview": ["review", "codereview", "cr", "pr"],
                "Ready for Validation": ["validation", "qa", "test", "testing"],
                "In Validation": ["validating", "validate", "val"],
                "Resolved": ["done", "resolved"],
                "In Definition": ["definition", "define"],
                "Ready For Eng": ["eng", "ready", "engineering"],
                "In Design": ["design"],
                "Open": ["open"],
                "Blocked": ["blocked", "block", "stop"],
                "Closed": ["closed", "close", "complete", "finish", "end"],
                "Won't Do": ["wont", "cancel", "skip"],
                "Reopened": ["reopened", "reopen"]
            }
            
            # Embedded workflow transitions with standard JIRA transition names
            workflow_transitions = {
                "Open": {
                    "In Definition": "Start Definition",
                    "Closed": "Close Issue"
                },
                "In Definition": {
                    "Ready For Eng": "Ready for Engineering",
                    "Open": "Reopen",
                    "Blocked": "Block"
                },
                "Ready For Eng": {
                    "In Development": "Start Progress",
                    "In Definition": "Back to Definition",
                    "Blocked": "Block"
                },
                "In Development": {
                    "Ready For Codereview": "Ready for Code Review",
                    "In Definition": "Back to Definition",
                    "Blocked": "Block"
                },
                "Ready For Codereview": {
                    "Ready for Validation": "Ready for QA",
                    "In Development": "Back to Development",
                    "Blocked": "Block"
                },
                "Ready for Validation": {
                    "In Validation": "Start Validation",
                    "In Development": "Back to Development",
                    "Blocked": "Block"
                },
                "In Validation": {
                    "Resolved": "Resolve Issue",
                    "In Development": "Reject", 
                    "Ready for Validation": "Back to Ready for Validation"
                },
                "Resolved": {
                    "Closed": "Close Issue",
                    "Reopened": "Reopen",
                    "In Validation": "Reopen for Validation"
                },
                "Blocked": {
                    "In Definition": "Unblock to Definition",
                    "Ready For Eng": "Unblock to Ready for Eng", 
                    "In Development": "Unblock to Development",
                    "Ready For Codereview": "Unblock to Code Review"
                }
            }
            
            # Resolve target state alias
            resolved_target = target_state
            for status, aliases in status_aliases.items():
                if target_state.lower() in [alias.lower() for alias in aliases]:
                    resolved_target = status
                    break
            
            # If current_status is provided, delegate to get_jira_transitions tool
            if current_status and current_status.strip():
                current_status = current_status.strip()
                return {
                    "type": "instruction_delegation",
                    "message": f"Use the dedicated get_jira_transitions tool for {ticket_id}: {current_status} → {resolved_target}",
                    "instruction": f"Call mcp__myt__get_jira_transitions(from_status='{current_status}', to_status='{resolved_target}') for the specific transition path",
                    "current_status": current_status,
                    "target_status": resolved_target,
                    "ticket_id": ticket_id
                }
            
            # Generate instructions that use our smart two-step approach
            instructions = f"""# JIRA Transition Instructions for {ticket_id} → {target_state}

## Step 1: Get Current Status
Execute this MCP command to get the current ticket status:

```
mcp__atlassian__getJiraIssue(
    cloudId="{cloud_id}",
    issueIdOrKey="{ticket_id}",
    fields=["status", "summary", "assignee"]
)
```

## Step 2: Calculate Specific Transition Path
After getting the current status from Step 1, use our dedicated transition calculator:

```
mcp__myt__get_jira_transitions(
    from_status="[CURRENT_STATUS_FROM_STEP_1]",
    to_status="{resolved_target}"
)
```

**This will return**:
- `type: "no_transition_needed"` → Already at target status
- `type: "direct_transition"` → Transition path with exact command
- `type: "no_direct_transition"` → No path available with alternatives

## Step 3: Execute Calculated Transitions
If Step 2 returns `type: "direct_transition"`, execute the transition using the provided command:

Example response from Step 2:
```json
{{
  "type": "direct_transition",
  "transitions": [{{"from": "Open", "to": "In Development", "transition_name": "Start Progress"}}],
  "atlassian_command": "mcp__atlassian__transitionJiraIssue(cloudId='credify.atlassian.net', issueIdOrKey='[TICKET_ID]', transition={{'name': 'Start Progress'}})"
}}
```

Replace `[TICKET_ID]` with `{ticket_id}` and execute the command.

## Step 4: Verify Final Status
Verify the transition was successful:

```
mcp__atlassian__getJiraIssue(
    cloudId="{cloud_id}",
    issueIdOrKey="{ticket_id}",
    fields=["status"]
)
```

## Key Benefits
- **Smart Path Calculation**: Our MCP tool calculates the optimal transition path
- **Current Status Aware**: Tool adapts based on the actual current status
- **Embedded Intelligence**: All workflow logic is contained in our MCP tool
- **Ready-to-Execute**: Returns exact Atlassian MCP commands to run

## Processing Logic
1. **Get Current Status**: Use Atlassian MCP to get ticket's current status
2. **Calculate Path**: Ask our MCP tool for specific transition sequence (with current_status)
3. **Execute Transitions**: Use the exact commands returned by our tool
4. **Verify Result**: Confirm the final status matches the target

## Resolved Target State
**Input**: '{target_state}' → **Resolved**: '{resolved_target}'

## Error Handling
- If ticket is already at target status, our tool returns "transition_complete"
- If no valid path exists, our tool returns "transition_error" with alternatives
- All workflow intelligence is embedded in our MCP tool

## Success Criteria
- Ticket status successfully changed to the resolved target state
- All MCP commands executed without errors
- Final verification confirms the status change

**Description**: {description or "Automated JIRA transition via MCP Tools"}
"""

            # Return instruction-based result for Claude Code to execute
            return {
                "type": "instruction_orchestration",
                "tool": "jira_transition", 
                "method": "atlassian_mcp",
                "ticket_id": ticket_id,
                "target_state": target_state,
                "resolved_target": next((status for status, aliases in status_aliases.items() 
                                       if target_state.lower() in [alias.lower() for alias in aliases]), target_state),
                "cloud_id": cloud_id,
                "instructions": instructions,
                "mcp_commands": [
                    f"mcp__atlassian__getJiraIssue(cloudId='{cloud_id}', issueIdOrKey='{ticket_id}', fields=['status', 'summary'])",
                    f"mcp__atlassian__getTransitionsForJiraIssue(cloudId='{cloud_id}', issueIdOrKey='{ticket_id}')",
                    f"mcp__atlassian__transitionJiraIssue(cloudId='{cloud_id}', issueIdOrKey='{ticket_id}', transition={{'id': 'TRANSITION_ID'}})",
                    f"mcp__atlassian__getJiraIssue(cloudId='{cloud_id}', issueIdOrKey='{ticket_id}', fields=['status'])"
                ],
                "description": description or "Automated JIRA transition via MCP Tools",
                "status_aliases": status_aliases
            }
            
        except Exception as e:
            logger.error(f"JIRA transition execution error: {str(e)}")
            return {
                "success": False,
                "error": f"JIRA transition execution failed: {str(e)}",
                "ticket_id": ticket_id,
                "target_state": target_state,
                "type": type(e).__name__,
                "method": "atlassian_mcp",
                "suggestion": "Check ticket ID format (e.g., SI-8748), target state, and Atlassian MCP authentication"
            }