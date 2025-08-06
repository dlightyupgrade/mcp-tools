#!/usr/bin/env python3
"""
JIRA Transitions Calculator Tool

Calculate the transition path between two JIRA statuses using embedded workflow knowledge.
Supports preset workflow shortcuts and multi-step path finding.
"""

import logging
from typing import Dict, Any
from collections import deque

from fastmcp import FastMCP
from .base import ToolBase

logger = logging.getLogger(__name__)


def register_jira_transitions_tool(mcp: FastMCP):
    """Register the get_jira_transitions tool with the FastMCP server"""
    
    @mcp.tool
    def get_jira_transitions(from_status: str, to_status: str = "") -> Dict[str, Any]:
        """
        Calculate the transition path between two JIRA statuses using embedded workflow knowledge.
        
        Supports preset workflow shortcuts for common development patterns:
        - "start"|"dev" → Open to In Development (3-step preset)
        - "review"|"pr" → In Development to Ready For Codereview (1-step preset)
        - "qa"|"test" → Ready For Codereview to Ready for Validation (1-step preset)
        - "done" → In Validation to Resolved (1-step preset)
        
        Natural language triggers: "get transitions", "transition path", "jira workflow"
        
        Args:
            from_status: Current JIRA status OR preset shortcut ("start", "dev", "review", "pr", "qa", "test", "done")
            to_status: Target JIRA status (optional if using preset shortcuts)
            
        Returns:
            Dictionary with transition path, commands, or error information
        """
        logger.info(f"Calculating JIRA transition path: {from_status} -> {to_status}")
        
        try:
            # Validate inputs
            if not from_status or not from_status.strip():
                raise ValueError("from_status cannot be empty")
            
            # Clean inputs
            from_status = from_status.strip()
            to_status = to_status.strip() if to_status else ""
            
            # Initialize preset tracking
            preset_used = None
            
            # Preset workflow shortcuts for common patterns
            workflow_presets = {
                "start": {"from": "Open", "to": "In Development", "description": "Start development work (Open → In Development)"},
                "dev": {"from": "Open", "to": "In Development", "description": "Start development work (Open → In Development)"},
                "review": {"from": "In Development", "to": "Ready For Codereview", "description": "Submit for code review (In Development → Ready For Codereview)"},
                "pr": {"from": "In Development", "to": "Ready For Codereview", "description": "Submit for code review (In Development → Ready For Codereview)"},
                "qa": {"from": "Ready For Codereview", "to": "Ready for Validation", "description": "Move to QA testing (Ready For Codereview → Ready for Validation)"},
                "test": {"from": "Ready For Codereview", "to": "Ready for Validation", "description": "Move to QA testing (Ready For Codereview → Ready for Validation)"},
                "done": {"from": "In Validation", "to": "Resolved", "description": "Mark as complete (In Validation → Resolved)"}
            }
            
            # Check if from_status is a preset shortcut
            if from_status.lower() in workflow_presets:
                if to_status:
                    return {
                        "type": "preset_with_override",
                        "message": f"Note: '{from_status}' is a preset shortcut. Using preset path instead of override.",
                        "preset_used": from_status.lower(),
                        "preset_description": workflow_presets[from_status.lower()]["description"],
                        "from_status": workflow_presets[from_status.lower()]["from"],
                        "to_status": workflow_presets[from_status.lower()]["to"],
                        "warning": f"Ignoring to_status='{to_status}' in favor of preset path"
                    }
                
                preset = workflow_presets[from_status.lower()]
                from_status = preset["from"]
                to_status = preset["to"]
                
                logger.info(f"Using preset '{from_status.lower()}': {preset['description']}")
                return {
                    "type": "preset_shortcut",
                    "preset_name": list(workflow_presets.keys())[list(workflow_presets.values()).index(preset)],
                    "preset_description": preset["description"],
                    "from_status": from_status,
                    "to_status": to_status,
                    "message": f"Using preset workflow: {preset['description']}",
                    "continue_with_normal_processing": True
                }
            
            # Validate to_status is provided for non-preset requests
            if not to_status:
                available_presets = list(workflow_presets.keys())
                return {
                    "type": "missing_to_status",
                    "message": "to_status is required when not using preset shortcuts",
                    "available_presets": available_presets,
                    "preset_examples": {
                        name: preset["description"] for name, preset in workflow_presets.items()
                    },
                    "error": "Either provide to_status or use a preset shortcut (start, dev, review, pr, qa, test, done)"
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
            
            # Status aliases for flexible input
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
            
            # Resolve status aliases
            resolved_from = from_status
            resolved_to = to_status
            
            for status, aliases in status_aliases.items():
                if from_status.lower() in [alias.lower() for alias in aliases]:
                    resolved_from = status
                if to_status.lower() in [alias.lower() for alias in aliases]:
                    resolved_to = status
            
            # Check if already at target
            if resolved_from == resolved_to:
                result = {
                    "type": "no_transition_needed",
                    "message": f"Already at target status: {resolved_to}",
                    "from_status": resolved_from,
                    "to_status": resolved_to,
                    "transitions": []
                }
                if preset_used:
                    result["preset"] = preset_used
                    result["message"] = f"Preset '{preset_used['name']}' applied: Already at target status {resolved_to}"
                return result
            
            # Check for direct transition
            if resolved_from in workflow_transitions:
                if resolved_to in workflow_transitions[resolved_from]:
                    transition_name = workflow_transitions[resolved_from][resolved_to]
                    result = {
                        "type": "direct_transition",
                        "message": f"Direct transition available: {resolved_from} → {resolved_to}",
                        "from_status": resolved_from,
                        "to_status": resolved_to,
                        "transitions": [{
                            "from": resolved_from,
                            "to": resolved_to,
                            "transition_name": transition_name
                        }],
                        "atlassian_command": f'mcp__atlassian__transitionJiraIssue(cloudId="credify.atlassian.net", issueIdOrKey="[TICKET_ID]", transition={{"name": "{transition_name}"}})'
                    }
                    if preset_used:
                        result["preset"] = preset_used
                        result["message"] = f"Preset '{preset_used['name']}' ({preset_used['description']}): Direct transition available"
                    return result
            
            # Check for multi-step transition path
            def find_path(start, target):
                """Find multi-step transition path using BFS to avoid deep recursion"""
                if start == target:
                    return []
                
                # Use BFS for multi-step path finding
                queue = deque([(start, [])])
                visited = set([start])
                
                while queue:
                    current, path = queue.popleft()
                    
                    if current in workflow_transitions:
                        for next_status, transition_name in workflow_transitions[current].items():
                            new_path = path + [{"from": current, "to": next_status, "transition_name": transition_name}]
                            
                            if next_status == target:
                                return new_path  # Found complete path
                            
                            if next_status not in visited:
                                visited.add(next_status)
                                queue.append((next_status, new_path))
                
                return None  # No path found
            
            multi_step_path = find_path(resolved_from, resolved_to)
            if multi_step_path:
                result = {
                    "type": "multi_step_transition",
                    "message": f"Multi-step transition path: {resolved_from} → {resolved_to} ({len(multi_step_path)} steps)",
                    "from_status": resolved_from,
                    "to_status": resolved_to,
                    "transitions": multi_step_path,
                    "atlassian_commands": [
                        f'mcp__atlassian__transitionJiraIssue(cloudId="credify.atlassian.net", issueIdOrKey="[TICKET_ID]", transition={{"name": "{step["transition_name"]}"}})'
                        for step in multi_step_path
                    ],
                    "path_summary": " → ".join([step["to"] for step in multi_step_path])
                }
                if preset_used:
                    result["preset"] = preset_used
                    result["message"] = f"Preset '{preset_used['name']}' ({preset_used['description']}): {len(multi_step_path)}-step transition path"
                return result
            
            # No path found
            available_transitions = []
            if resolved_from in workflow_transitions:
                available_transitions = list(workflow_transitions[resolved_from].keys())
            
            result = {
                "type": "no_transition_path",
                "message": f"No transition path found from '{resolved_from}' to '{resolved_to}'",
                "from_status": resolved_from,
                "to_status": resolved_to,
                "transitions": [],
                "available_from_current": available_transitions,
                "suggestion": f"Available next steps: {', '.join(available_transitions)}" if available_transitions else "No transitions available from current status"
            }
            if preset_used:
                result["preset"] = preset_used
                result["message"] = f"Preset '{preset_used['name']}' ({preset_used['description']}): No transition path found"
            return result
            
        except Exception as e:
            logger.error(f"Error calculating JIRA transitions: {e}")
            return {
                "type": "error",
                "message": f"Failed to calculate transition path: {str(e)}",
                "error": str(e),
                "error_type": type(e).__name__
            }