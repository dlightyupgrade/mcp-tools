#!/usr/bin/env python3
"""
Epic Status Tool

Epic status tracking and reporting for project management.
Analyzes sub-tasks, identifies progress, lagging items, and generates actionable status reports.
"""

import logging
from typing import Dict, Any

from fastmcp import FastMCP

logger = logging.getLogger(__name__)


def register_epic_status_tool(mcp: FastMCP):
    """Register the epic_status tool with the FastMCP server"""
    
    @mcp.tool
    def epic_status_report(epic_id: str, focus: str = "status_report") -> Dict[str, Any]:
        """
        Generate comprehensive epic status report with sub-task analysis.
        
        **Natural Language Triggers:**
        - "epic status for [EPIC-ID]" - Generate status report
        - "check epic [EPIC-ID] progress" - Progress analysis 
        - "epic report [EPIC-ID]" - Comprehensive status
        - "analyze epic [EPIC-ID]" - Sub-task analysis
        - "epic dashboard [EPIC-ID]" - Status dashboard
        - "team status for epic [EPIC-ID]" - Team communication format
        - "ping list for [EPIC-ID]" - Generate assignee action items
        
        **Focus Areas:**
        - "status_report" - Full epic status with all sections (default)
        - "current_sprint" - Focus on active sprint items only
        - "lagging_items" - Identify at-risk tickets needing attention
        - "team_communication" - Generate team lead summary
        - "assignee_actions" - Create ping list and action items
        
        **What this tool does:**
        Analyzes epic and all sub-tasks to provide:
        - Current sprint progress identification
        - Lagging item detection (stalled/overdue tickets)
        - Remaining work breakdown
        - Assignee action items and ping lists
        - Team lead executive summary
        - Progress metrics and completion estimates
        
        **Perfect for:**
        - Epic owners tracking delivery progress
        - Team leads needing status updates
        - Stand-up meeting preparation
        - Sprint planning and risk assessment
        - Stakeholder communication
        
        Args:
            epic_id: JIRA epic ticket ID (e.g., "SI-9038", "PROJ-123")
            focus: Analysis focus area for targeted reporting
            
        Returns:
            Comprehensive epic status analysis with actionable insights
        """
        
        try:
            logger.info(f"Generating epic status report for {epic_id} with focus: {focus}")
            
            # Create instructions for Claude Code to execute the analysis
            instructions = {
                "tool_name": "epic_status_report",
                "epic_id": epic_id,
                "focus": focus,
                "analysis_type": "comprehensive_epic_status",
                "processing_steps": [
                    "Extract epic details and metadata",
                    "Gather all sub-tasks and stories under epic", 
                    "Analyze sub-task status and progress",
                    "Identify current sprint items",
                    "Detect lagging and at-risk tickets",
                    "Calculate progress metrics",
                    "Generate assignee action items",
                    "Create team communication summary"
                ],
                "output_sections": _get_output_sections(focus),
                "jira_queries": _get_jira_queries(epic_id),
                "analysis_criteria": _get_analysis_criteria(),
                "claude_processing_instructions": _get_processing_instructions(epic_id, focus)
            }
            
            return {
                "success": True,
                "epic_id": epic_id,
                "focus": focus,
                "instructions": instructions,
                "message": f"Epic status analysis instructions generated for {epic_id}",
                "next_step": "Execute analysis using Atlassian MCP tools and JIRA data"
            }
            
        except Exception as e:
            logger.error(f"Error generating epic status instructions: {e}")
            return {
                "success": False,
                "error": str(e),
                "epic_id": epic_id,
                "focus": focus
            }


def _get_output_sections(focus: str) -> Dict[str, Any]:
    """Define output sections based on focus area"""
    
    base_sections = {
        "executive_summary": {
            "progress_percentage": "Completion percentage based on closed tickets",
            "current_sprint_count": "Number of tickets in active sprint",
            "at_risk_count": "Number of tickets needing attention",
            "estimated_completion": "Completion date based on velocity"
        },
        "current_sprint_progress": {
            "in_progress_tickets": "Tickets currently being worked on",
            "in_review_tickets": "Tickets awaiting review/approval", 
            "blocked_tickets": "Tickets with impediments",
            "status_indicators": "Visual status for each ticket"
        },
        "items_needing_attention": {
            "stalled_tickets": "No updates in 3+ days",
            "overdue_tickets": "Past due date",
            "unassigned_tickets": "Missing assignee",
            "priority_indicators": "Risk level for each item"
        },
        "remaining_work": {
            "backlog_count": "Planned but not started",
            "work_breakdown": "Categories of remaining work",
            "dependency_mapping": "Critical path items"
        },
        "action_items": {
            "assignee_pings": "Who to follow up with",
            "escalation_items": "Items needing team lead attention", 
            "blocker_resolution": "Steps to unblock tickets"
        }
    }
    
    # Focus-specific section filtering
    focus_sections = {
        "current_sprint": ["executive_summary", "current_sprint_progress"],
        "lagging_items": ["items_needing_attention", "action_items"],
        "team_communication": ["executive_summary", "action_items"],
        "assignee_actions": ["action_items", "items_needing_attention"]
    }
    
    if focus in focus_sections:
        return {k: v for k, v in base_sections.items() if k in focus_sections[focus]}
    
    return base_sections


def _get_jira_queries(epic_id: str) -> Dict[str, str]:
    """Generate JIRA queries for epic analysis"""
    
    return {
        "epic_details": f"key = {epic_id}",
        "epic_subtasks": f"'Epic Link' = {epic_id} OR parent = {epic_id}",
        "current_sprint": f"('Epic Link' = {epic_id} OR parent = {epic_id}) AND sprint in openSprints()",
        "in_progress": f"('Epic Link' = {epic_id} OR parent = {epic_id}) AND status IN ('In Progress', 'In Development', 'In Review')",
        "blocked_items": f"('Epic Link' = {epic_id} OR parent = {epic_id}) AND status = 'Blocked'",
        "overdue_items": f"('Epic Link' = {epic_id} OR parent = {epic_id}) AND duedate < now() AND status NOT IN ('Done', 'Resolved', 'Closed')",
        "unassigned": f"('Epic Link' = {epic_id} OR parent = {epic_id}) AND assignee is EMPTY AND status NOT IN ('Done', 'Resolved', 'Closed')"
    }


def _get_analysis_criteria() -> Dict[str, Any]:
    """Define criteria for epic analysis"""
    
    return {
        "stale_threshold_days": 3,
        "priority_mapping": {
            "Highest": "🔴",
            "High": "🟠", 
            "Medium": "🟡",
            "Low": "🟢",
            "Lowest": "🔵"
        },
        "status_indicators": {
            "In Progress": "✅",
            "In Development": "✅",
            "In Review": "👀",
            "Ready for Validation": "🧪", 
            "Blocked": "🚫",
            "Done": "✔️",
            "To Do": "📋"
        },
        "completion_states": ["Done", "Resolved", "Closed"],
        "active_states": ["In Progress", "In Development", "In Review"],
        "risk_indicators": {
            "overdue": "🔴",
            "stale": "🟠",
            "unassigned": "⚠️",
            "blocked": "🚫"
        }
    }


def _get_processing_instructions(epic_id: str, focus: str) -> str:
    """Generate Claude processing instructions"""
    
    return f"""
## Epic Status Report Processing Instructions

**Epic ID**: {epic_id}
**Focus**: {focus}

### Step 1: Data Extraction
Use Atlassian MCP tools to gather:
1. Epic details: `mcp__atlassian__getJiraIssue` with issueIdOrKey="{epic_id}"
2. Sub-tasks: `mcp__atlassian__searchJiraIssuesUsingJql` with JQL from jira_queries
3. Sprint information for current sprint items
4. Update history for stale detection

### Step 2: Analysis Processing
- **Current Sprint Items**: Identify tickets in active sprints
- **Progress Calculation**: (Completed tickets / Total tickets) * 100
- **Stale Detection**: Last update > 3 days ago
- **Risk Assessment**: Overdue, blocked, unassigned tickets
- **Velocity Estimation**: Based on recent completion rate

### Step 3: Report Generation
Create structured report with sections based on focus area:

```markdown
# Epic Status Report: {epic_id}

## Executive Summary
- **Progress**: X% complete (Y/Z tickets)
- **Current Sprint**: N tickets in progress
- **At Risk**: R tickets need attention  
- **Estimated Completion**: [Date based on velocity]

## Current Sprint Progress
[List active tickets with status indicators]

## Items Needing Attention  
[Stalled, overdue, blocked tickets with specific issues]

## Action Items
- **Ping**: [Assignee names] about [specific tickets]
- **Follow-up**: [Tickets needing status updates]  
- **Escalate**: [Blocked items for team lead]

## Remaining Work
[Backlog breakdown by category]
```

### Step 4: Actionable Output
Focus on generating:
- Specific assignee names to ping
- Clear action items with ticket numbers
- Team lead summary for executive reporting
- Copy/paste ready status for team communication

### Error Handling
If JIRA data access fails:
1. Provide fallback analysis structure
2. Suggest manual data collection steps
3. Include template for manual status tracking
"""


def register_epic_status_tools(mcp: FastMCP):
    """Register all epic status related tools"""
    register_epic_status_tool(mcp)