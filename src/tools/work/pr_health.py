#!/usr/bin/env python3
"""
PR Health Analysis Tool

Analyze PR health including open review threads, CI status, merge conflicts, and overall readiness.
Provides detailed step-by-step instructions for Claude Code to perform comprehensive 
PR health assessment with actionable solutions for blocking issues.
"""

import logging
from typing import Dict, Any

from fastmcp import FastMCP
from .base import ToolBase, get_context_fallback
from config.settings import Config

logger = logging.getLogger(__name__)


def register_pr_health_tool(mcp: FastMCP):
    """Register the pr_health tool with the FastMCP server"""
    
    @mcp.tool
    def pr_health(pr_url: str, description: str = "") -> Dict[str, Any]:
        """
        Analyze PR health including open review threads, CI status, merge conflicts, and readiness - INSTRUCTIONS ONLY.
        
        **Natural Language Triggers:**
        - "check pr health for [PR_URL]"
        - "analyze pr status in [PR_URL]" 
        - "what's blocking this PR [PR_URL]"
        - "pr health analysis [PR_URL]"
        - "check review threads in [PR_URL]"
        - "pr readiness check [PR_URL]"
        
        **What this tool does:**
        Provides comprehensive step-by-step instructions for analyzing PR health including open review 
        threads, CI status, merge conflicts, and overall readiness. Returns detailed GitHub API 
        commands for Claude Code to execute - does NOT run analysis directly.
        
        **Perfect for:** PR health assessment, code review cleanup, merge readiness evaluation, 
        identifying and resolving blocking issues.
        
        Args:
            pr_url: GitHub PR URL to analyze (e.g., https://github.com/owner/repo/pull/123)
            description: Optional focus area (e.g., "review threads", "merge readiness")
            
        Returns:
            Comprehensive instructions for Claude Code to perform PR health analysis
        """
        logger.info(f"pr_health tool called for: {pr_url}")
        
        try:
            # Validate PR URL format
            is_valid, components = ToolBase.validate_github_pr_url(pr_url)
            if not is_valid:
                return ToolBase.create_error_response(
                    "Invalid GitHub PR URL format",
                    pr_url,
                    "validation_error"
                )
            
            owner = components["owner"]
            repo = components["repo"]
            pr_number = components["pr_number"]
            
            # Load external context for PR health analysis
            context_content = ToolBase.load_external_context(
                "/Users/dlighty/code/llm-context/PR-HEALTH-CONTEXT.md",
                get_context_fallback("pr_health")
            )
            
            # Return detailed analysis instructions
            health_analysis = {
                "tool_name": "pr_health",
                "analysis_context": "PR Health Analysis - Generate Comprehensive Health Assessment",
                "timestamp": ToolBase.create_success_response({})["timestamp"],
                "pr_url": pr_url,
                "pr_owner": owner,
                "pr_repo": repo,
                "pr_number": pr_number,
                "description": description,
                
                "processing_instructions": {
                    "overview": f"Extract PR data and generate comprehensive health assessment with review threads, CI status, merge readiness, and blocking issue resolution. Focus: {description or 'comprehensive health evaluation with actionable recommendations'}.",
                    
                    "data_extraction_steps": [
                        f"Execute: gh api \"repos/{owner}/{repo}/pulls/{pr_number}\" (PR details)",
                        f"Execute: gh api graphql -f query='{{repository(owner:\\\"{owner}\\\", name:\\\"{repo}\\\"){{pullRequest(number:{pr_number}){{reviewThreads(first:100){{nodes{{id isResolved isCollapsed isOutdated path line startLine originalLine originalStartLine diffSide comments(first:20){{nodes{{id author{{login}} body createdAt outdated}}}}}}}}}}}}}}' (review threads)",
                        f"Execute: gh api \"repos/{owner}/{repo}/commits/$(gh api \\\"repos/{owner}/{repo}/pulls/{pr_number}\\\" --jq '.head.sha')/check-runs\" (CI status)",
                        f"Execute: gh api \"repos/{owner}/{repo}/pulls/{pr_number}/comments\" (inline comments)",
                        f"Execute: gh pr view {pr_number} --repo {owner}/{repo} --json mergeable,mergeStateStatus (merge status)",
                        "Extract JIRA ticket from PR title/body (SI-XXXX pattern)",
                        "If JIRA ticket found, execute: mcp__atlassian__getJiraIssue(cloudId='credify.atlassian.net', issueIdOrKey='TICKET_ID', fields=['summary', 'description', 'status']) to get ticket context for health analysis",
                        "Get code context for each thread location using GitHub Contents API"
                    ],
                    
                    "required_output_format": """
## 🏥 PR Health Analysis: [ACTUAL_PR_TITLE]

**Repository**: [REPO] #[NUMBER]
**PR Title**: [ACTUAL_PR_TITLE]
**Overall Status**: [READY|NEEDS_ATTENTION|BLOCKED]
**Author**: [username]
**JIRA**: [SI-XXXX or none]
**Confidence Score**: [0.0-1.0]
**Quality Grade**: [A+/A/B+/B/C]

### 🚨 Blocking Issues ([count])
- [ ] Issue description with file:line reference
- [ ] Issue description with file:line reference

### ⚡ High Priority ([count])  
- [ ] Issue description with file:line reference

### 📝 Medium Priority ([count])
- [ ] Issue description with file:line reference

### 💬 Discussion Threads ([count])

#### Thread 1: [file:line] - Complexity: [SIMPLE|MEDIUM|HARD]
**Question**: [reviewer's question/comment]
**Solution**: [terse 1-2 sentence solution]

#### Thread 2: [file:line] - Complexity: [SIMPLE|MEDIUM|HARD]
**Question**: [reviewer's question/comment]
**Solution**: [terse 1-2 sentence solution]

### 📊 Status Summary
- **Open Threads**: X total (Y simple, Z medium, W hard)
- **CI Status**: X passed, Y failed, Z pending
- **Merge Status**: [READY|CONFLICTS|PENDING_CHECKS]
- **JIRA Ticket**: [SI-XXXX or none]
- **Last Updated**: [timestamp]

### 🎯 Next Actions
1. **Address [complexity] thread**: [specific action with proposed solution]
2. **Implement solution**: [concrete implementation steps]
3. **Follow up**: [verification or additional steps needed]

Thread Complexity Assessment:
• SIMPLE: Straightforward explanation, code comment, or minor clarification
• MEDIUM: Requires code analysis, logic explanation, or minor refactoring  
• HARD: Complex architectural decision, major refactoring, or design pattern change

Scaling Rules:
• 1-3 threads: Brief analysis + solution
• 4-10 threads: Terse solutions only (1-2 sentences)
• 10+ threads: Essential solutions, group by complexity
""",
                    
                    "analysis_requirements": [
                        "Filter review threads to ONLY open threads (not resolved, collapsed, or outdated)",
                        "Analyze ONLY open threads (not resolved, collapsed, or outdated)",
                        "Extract code context around each thread location (±10 lines)",
                        "Classify thread complexity: SIMPLE (explanation), MEDIUM (code analysis), HARD (architectural)",
                        "Extract JIRA ticket ID from PR title/body using regex pattern: SI-\\d+",
                        "If JIRA ticket found, execute Atlassian MCP command to retrieve ticket details for context",
                        "Use JIRA ticket data (if available) to understand the intended changes and assess violations",
                        "Provide actionable solutions with specific file:line references",
                        "Generate quality confidence score (0.0-1.0) and grade (A+ to C)",
                        "Include JIRA ticket detection and compliance checking",
                        "Scale output appropriately: 1-3 threads = detailed, 4-10 = terse, 10+ = essential only"
                    ]
                },
                
                "health_categories": {
                    "blocking": {
                        "description": "Issues that prevent merge (conflicts, failed CI, security)",
                        "priority": "immediate",
                        "examples": "merge conflicts, failing tests, security vulnerabilities"
                    },
                    "high_priority": {
                        "description": "Code quality issues requiring attention",
                        "priority": "urgent", 
                        "examples": "missing tests, code quality issues, performance problems"
                    },
                    "medium_priority": {
                        "description": "Style and improvement suggestions",
                        "priority": "moderate",
                        "examples": "style issues, refactoring suggestions, documentation"
                    },
                    "discussion": {
                        "description": "Questions and clarifications from reviewers",
                        "priority": "responsive",
                        "examples": "clarifying questions, design discussions, approach validation"
                    }
                },
                
                "external_context": context_content,
                
                "success_criteria": {
                    "data_extraction": "PR details, threads, CI status, and code context successfully extracted",
                    "health_classification": "All health issues categorized by priority with actionable solutions",
                    "thread_analysis": "Open threads analyzed with complexity assessment and solutions",
                    "jira_integration": "JIRA ticket extracted from PR and Atlassian MCP called if ticket found",
                    "jira_context": "JIRA ticket data (if available) used to understand intended changes and assess health issues",
                    "quality_scoring": "Confidence score and quality grade assigned based on analysis completeness",
                    "actionable_output": "Structured report with file:line references and next steps provided"
                }
            }
            
            logger.info(f"PR health orchestration instructions generated for: {pr_url}")
            return health_analysis
            
        except Exception as e:
            logger.error(f"Error generating PR health orchestration: {str(e)}")
            return ToolBase.create_error_response(
                f"Failed to generate PR health orchestration: {str(e)}",
                pr_url,
                type(e).__name__
            )