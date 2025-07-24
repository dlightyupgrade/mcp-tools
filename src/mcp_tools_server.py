#!/usr/bin/env python3
"""
MCP Tools Server - FastMCP Implementation

A production-ready Model Context Protocol (MCP) server built with FastMCP Python framework,
featuring HTTP Streaming transport and comprehensive development workflow tools.

Tools:
- pr_violations: Analyze PR violations and review threads  
- code_review: Comprehensive code quality review
- echo: Simple echo for testing
- get_system_info: System information and diagnostics

Architecture:
- FastMCP Python framework with auto-generated schemas
- HTTP Streaming transport (MCP Guidelines compliant)
- uvicorn ASGI server for production deployment
- Comprehensive error handling and logging
- Type-safe tool definitions with validation
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import psutil
import uvicorn
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse
from starlette.routing import Route

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration class for centralized settings
class Config:
    DEFAULT_PORT = int(os.getenv("MCP_SERVER_PORT", "8002"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    TOOL_TIMEOUT = int(os.getenv("TOOL_TIMEOUT", "300"))  # 5 minutes
    RATE_LIMIT = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    
    # Tool script paths
    PR_VIOLATIONS_SCRIPT = os.getenv("PR_VIOLATIONS_SCRIPT", "pr-violations-claude")
    CODE_REVIEW_SCRIPT = os.getenv("CODE_REVIEW_SCRIPT", "code-review-claude")

# Initialize FastMCP server
mcp = FastMCP("MCP Tools Server")

# SHELL AUTHENTICATION LAYER
#
# Provides OAuth-like endpoints for MCP client authentication without browser interaction.
# Auto-approves all requests for headless/containerized environments.
#

async def oauth_authorization_server(request: Request):
    """
    OAuth authorization server discovery endpoint.
    
    Provides OAuth 2.0 server metadata for MCP client discovery.
    This is a shell/fake OAuth implementation for headless environments.
    """
    return JSONResponse({
        "issuer": f"http://localhost:{Config.DEFAULT_PORT}",
        "authorization_endpoint": f"http://localhost:{Config.DEFAULT_PORT}/auth",
        "token_endpoint": f"http://localhost:{Config.DEFAULT_PORT}/token",
        "registration_endpoint": f"http://localhost:{Config.DEFAULT_PORT}/register",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "scopes_supported": ["mcp"],
        "code_challenge_methods_supported": ["S256"],
        "headless_supported": True,
        "shell_auth": True,
        "auto_approve": True
    })

async def oauth_authorization_server_mcp(request: Request):
    """
    MCP-specific OAuth authorization server discovery endpoint.
    
    Same as oauth_authorization_server but specifically for MCP clients.
    """
    return JSONResponse({
        "issuer": f"http://localhost:{Config.DEFAULT_PORT}",
        "authorization_endpoint": f"http://localhost:{Config.DEFAULT_PORT}/auth",
        "token_endpoint": f"http://localhost:{Config.DEFAULT_PORT}/token",
        "registration_endpoint": f"http://localhost:{Config.DEFAULT_PORT}/register",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "scopes_supported": ["mcp"],
        "code_challenge_methods_supported": ["S256"],
        "headless_supported": True,
        "shell_auth": True,
        "auto_approve": True
    })

async def oauth_protected_resource(request: Request):
    """OAuth protected resource discovery endpoint."""
    return JSONResponse({
        "resource_server": f"http://localhost:{Config.DEFAULT_PORT}",
        "authorization_servers": [f"http://localhost:{Config.DEFAULT_PORT}"],
        "scopes_supported": ["mcp"],
        "bearer_methods_supported": ["header", "query"]
    })

async def register_client(request: Request):
    """Dynamic client registration endpoint."""
    try:
        client_data = await request.json()
        
        # Generate fake client credentials
        client_id = f"mcp_tools_client_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        client_secret = f"secret_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Shell auth: Registered client {client_id}")
        
        return JSONResponse({
            "client_id": client_id,
            "client_secret": client_secret,
            "client_id_issued_at": int(datetime.now().timestamp()),
            "client_secret_expires_at": 0,  # Never expires
            "redirect_uris": client_data.get("redirect_uris", []),
            "grant_types": ["authorization_code"],
            "response_types": ["code"],
            "scope": "mcp",
            "token_endpoint_auth_method": "client_secret_post"
        })
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return JSONResponse(
            {"error": "invalid_client_metadata", "error_description": str(e)},
            status_code=400
        )

async def authorize(request: Request):
    """Authorization endpoint - auto-approve and redirect to callback."""
    query_params = dict(request.query_params)
    
    # Generate authorization code
    auth_code = f"mcp_tools_auth_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    logger.info(f"Shell auth: Generated authorization code {auth_code} (AUTO-REDIRECT)")
    
    state = query_params.get("state", "")
    redirect_uri = query_params.get("redirect_uri", "")
    
    if redirect_uri:
        # Build callback URL with auth code and state
        callback_params = {
            "code": auth_code,
            "state": state
        }
        
        callback_url = f"{redirect_uri}?{urlencode(callback_params)}"
        
        logger.info(f"Shell auth: Redirecting to callback URL: {callback_url}")
        
        # Return redirect response (critical for OAuth compliance)
        return RedirectResponse(url=callback_url, status_code=302)
    else:
        # Fallback: return JSON if no redirect_uri provided
        logger.warning("Shell auth: No redirect_uri provided, returning JSON response")
        return JSONResponse({
            "code": auth_code,
            "state": state,
            "authorization_granted": True,
            "message": "Authorization granted but no redirect_uri specified"
        })

async def token_endpoint(request: Request):
    """Token endpoint - issue access tokens."""
    try:
        form_data = await request.form()
        
        # Generate access token
        access_token = f"mcp_tools_access_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Shell auth: Issued access token {access_token}")
        
        return JSONResponse({
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 3600,  # 1 hour
            "scope": "mcp",
            "refresh_token": f"mcp_tools_refresh_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        })
        
    except Exception as e:
        logger.error(f"Token error: {e}")
        return JSONResponse(
            {"error": "invalid_grant", "error_description": str(e)},
            status_code=400
        )

@mcp.tool
def echo(text: str) -> Dict[str, Any]:
    """
    Echo the provided text back to verify MCP connectivity.
    
    This tool is useful for testing MCP server connectivity and basic functionality.
    
    Args:
        text: The text to echo back
        
    Returns:
        Dictionary containing the echoed text and server information
    """
    logger.info(f"Echo tool called with text: {text}")
    
    return {
        "echoed_text": text,
        "timestamp": datetime.now().isoformat(),
        "server": "mcp-tools-fastmcp",
        "status": "success"
    }

@mcp.tool
def get_system_info(include_processes: bool = False) -> Dict[str, Any]:
    """
    Get comprehensive system information and server diagnostics.
    
    Provides detailed system metrics useful for monitoring and debugging.
    
    Args:
        include_processes: Whether to include running process information
        
    Returns:
        Dictionary containing system information and server status
    """
    logger.info("System info tool called")
    
    try:
        # Basic system info
        system_info = {
            "server": {
                "name": "mcp-tools-fastmcp",
                "version": "1.0.0",
                "port": Config.DEFAULT_PORT,
                "timestamp": datetime.now().isoformat(),
                "transport": "http-streaming"
            },
            "system": {
                "platform": sys.platform,
                "python_version": sys.version,
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent
            },
            "environment": {
                "log_level": Config.LOG_LEVEL,
                "tool_timeout": Config.TOOL_TIMEOUT,
                "rate_limit": Config.RATE_LIMIT
            }
        }
        
        # Add process information if requested
        if include_processes:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            system_info["processes"] = processes[:10]  # Top 10 processes
        
        logger.info("System info retrieved successfully")
        return system_info
        
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return {
            "error": f"Failed to get system info: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "status": "error"
        }


@mcp.tool
def pr_violations(pr_url: str, description: str = "") -> Dict[str, Any]:
    """
    Analyze PR violations, open review threads, CI failures, and merge conflicts - INSTRUCTIONS ONLY.
    
    Provides detailed step-by-step instructions for Claude Code to perform comprehensive PR violations
    analysis including open review threads, CI status, merge conflicts, and actionable solutions.
    Does NOT execute analysis directly - returns structured instructions for external execution.
    
    Args:
        pr_url: GitHub PR URL to analyze
        description: Optional description of analysis focus
        
    Returns:
        Dictionary containing detailed processing instructions for Claude Code execution
    """
    logger.info(f"pr_violations tool called for: {pr_url}")
    
    try:
        # Validate PR URL format
        if not pr_url.startswith("https://github.com/") or "/pull/" not in pr_url:
            return {
                "error": "Invalid GitHub PR URL format",
                "expected_format": "https://github.com/owner/repo/pull/number",
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }
        
        # Parse PR URL to extract components
        import re
        url_match = re.match(r'https://github\.com/([^/]+)/([^/]+)/pull/([0-9]+)', pr_url)
        if not url_match:
            return {
                "error": "Failed to parse PR URL components",
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }
        
        owner, repo, pr_number = url_match.groups()
        
        # Load external context for PR violations analysis
        context_content = ""
        context_file = "/Users/dlighty/code/llm-context/PR-VIOLATIONS-CONTEXT.md"
        try:
            with open(context_file, 'r') as f:
                context_content = f.read()
        except FileNotFoundError:
            # Fallback context for PR violations analysis
            context_content = """# PR Violations Analysis Guidelines

## Review Thread Analysis
- Focus on open threads (not resolved, collapsed, or outdated)
- Categorize by urgency: blocking, important, suggestion
- Identify action items vs discussion threads

## Violation Classification
- **Blocking**: Merge conflicts, failed CI, security issues
- **High Priority**: Code quality violations, missing tests
- **Medium Priority**: Style issues, suggestions for improvement  
- **Low Priority**: Discussions, clarifications

## Output Format
```
Violation Summary:
- Open Threads: X (Y blocking, Z important)
- CI Failures: X failed checks
- Merge Status: [READY|CONFLICTS|BLOCKED]
- Action Items: Prioritized list with file:line references
```

## Action Item Prioritization
1. Fix blocking issues first (merge conflicts, CI failures)
2. Address reviewer concerns in order of thread creation
3. Handle style/quality issues
4. Respond to discussion threads

## Thread Resolution Strategies
- **Simple threads**: Direct explanation or code comment
- **Medium threads**: Code analysis and logic explanation
- **Complex threads**: Architectural discussion or design pattern changes

## Quality Confidence Scoring
- **A+**: Comprehensive analysis with actionable solutions
- **A**: Solid analysis with clear next steps
- **B+**: Good analysis with minor gaps
- **B**: Adequate analysis, some areas need attention
- **C**: Basic analysis, significant improvements needed
"""
        
        # Return detailed analysis instructions matching code_review pattern
        violations_analysis = {
            "tool_name": "pr_violations",
            "analysis_context": "PR Violations Analysis - Generate Structured Violation Report",
            "timestamp": datetime.now().isoformat(),
            "pr_url": pr_url,
            "pr_owner": owner,
            "pr_repo": repo,
            "pr_number": pr_number,
            "description": description,
            
            "processing_instructions": {
                "overview": f"Extract PR data and generate comprehensive violations analysis with open review threads, CI failures, and merge conflicts. Focus: {description or 'comprehensive violation detection with actionable solutions'}.",
                
                "data_extraction_steps": [
                    f"Execute: gh api \"repos/{owner}/{repo}/pulls/{pr_number}\" (PR details)",
                    f"Execute: gh api graphql -f query='{{repository(owner:\\\"{owner}\\\", name:\\\"{repo}\\\"){{pullRequest(number:{pr_number}){{reviewThreads(first:100){{nodes{{id isResolved isCollapsed isOutdated path line startLine originalLine originalStartLine diffSide comments(first:20){{nodes{{id author{{login}} body createdAt outdated}}}}}}}}}}}}}}' (review threads)",
                    f"Execute: gh api \"repos/{owner}/{repo}/commits/$(gh api \\\"repos/{owner}/{repo}/pulls/{pr_number}\\\" --jq '.head.sha')/check-runs\" (CI status)",
                    f"Execute: gh api \"repos/{owner}/{repo}/pulls/{pr_number}/comments\" (inline comments)",
                    f"Execute: gh pr view {pr_number} --repo {owner}/{repo} --json mergeable,mergeStateStatus (merge status)",
                    "Extract JIRA ticket from PR title/body (SI-XXXX pattern)",
                    "Get code context for each thread location using GitHub Contents API"
                ],
                
                "required_output_format": """
## 🔍 PR Violation Analysis: [ACTUAL_PR_TITLE]

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
                    "Provide actionable solutions with specific file:line references",
                    "Generate quality confidence score (0.0-1.0) and grade (A+ to C)",
                    "Include JIRA ticket detection and compliance checking",
                    "Scale output appropriately: 1-3 threads = detailed, 4-10 = terse, 10+ = essential only"
                ]
            },
            
            "violation_categories": {
                "blocking": {
                    "description": "Issues that prevent merge (conflicts, failed CI, security)",
                    "priority": "immediate",
                    "examples": "merge conflicts, failing tests, security vulnerabilities"
                },
                "high_priority": {
                    "description": "Code quality violations requiring attention",
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
                "violation_classification": "All violations categorized by priority with actionable solutions",
                "thread_analysis": "Open threads analyzed with complexity assessment and solutions",
                "quality_scoring": "Confidence score and quality grade assigned based on analysis completeness",
                "actionable_output": "Structured report with file:line references and next steps provided"
            }
        }
        
        logger.info(f"PR violations orchestration instructions generated for: {pr_url}")
        return violations_analysis
        
    except Exception as e:
        logger.error(f"Error generating PR violations orchestration: {str(e)}")
        return {
            "error": f"Failed to generate PR violations orchestration: {str(e)}",
            "status": "error",
            "pr_url": pr_url,
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool
def code_review(pr_url: str, focus: str = "", max_diff_lines: int = 2000) -> Dict[str, Any]:
    """
    Perform comprehensive code quality review of pull requests - ANALYSIS ONLY.
    
    Provides step-by-step instructions for external agents to analyze code quality, security, 
    performance, and maintainability aspects. Does NOT make changes - only reviews and provides 
    insights. Emphasizes deep thinking about code simplification and standards compliance.
    
    Args:
        pr_url: GitHub PR URL to review
        focus: Optional focus area (e.g., "security", "performance", "tests")
        max_diff_lines: Maximum diff lines to include (default: 2000)
        
    Returns:
        Dictionary containing detailed instructions for comprehensive analysis
    """
    logger.info(f"code_review tool called for: {pr_url}")
    
    try:
        # Validate PR URL format
        if not pr_url.startswith("https://github.com/") or "/pull/" not in pr_url:
            return {
                "error": "Invalid GitHub PR URL format",
                "expected_format": "https://github.com/owner/repo/pull/number",
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }
        
        # Parse PR URL to extract components
        import re
        url_match = re.match(r'https://github\.com/([^/]+)/([^/]+)/pull/([0-9]+)', pr_url)
        if not url_match:
            return {
                "error": "Failed to parse PR URL components",
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }
        
        owner, repo, pr_number = url_match.groups()
        
        # Load external context file
        context_content = ""
        context_file = "/Users/dlighty/code/llm-context/CODE-REVIEW-CONTEXT.md"
        try:
            with open(context_file, 'r') as f:
                context_content = f.read()
        except FileNotFoundError:
            # Fallback context
            context_content = """# Code Review Guidelines

## Comprehensive Assessment Areas

### 1. VIOLATIONS ANALYSIS
- Check for "DO NOT MERGE" labels or blocking issues
- Analyze CI status and test failures
- Review merge conflicts or branch protection issues
- Check PR approval status and review requirements

### 2. CODE QUALITY ASSESSMENT
- Review code changes for adherence to Java standards
- Check import organization and unused imports
- Verify Lombok usage patterns and code structure
- Assess error handling and validation patterns
- Review database query optimization
- Check for hardcoded values vs proper constants/fixtures

### 3. TEST COVERAGE VERIFICATION
- Analyze test changes and new test coverage
- Check for proper test fixtures usage vs hardcoded values
- Verify unit tests focus on error scenarios (90% rule)
- Validate integration tests cover valid scenarios plus complex errors
- Review test naming and structure patterns

### 4. SECURITY REVIEW
- Check for exposed sensitive data in logs or errors
- Verify input validation and sanitization
- Review authentication/authorization changes
- Check for hardcoded secrets or credentials

### 5. BUSINESS LOGIC COMPLIANCE
- Verify adherence to business constants and patterns
- Check GraphQL schema changes and enum synchronization
- Review service integration patterns and error codes
- Validate field naming conventions and type standards

### 6. JIRA TICKET COMPLIANCE
- Does implementation match ticket requirements exactly?
- Are acceptance criteria fulfilled?
- Is scope appropriate (not over/under-engineered)?

## Output Format

Provide comprehensive analysis with:
- Severity-prioritized findings
- Specific file references and line numbers
- Concrete improvement suggestions
- Overall quality assessment and recommendation

## Assessment Criteria
- **APPROVE**: High quality, no blocking issues, meets requirements
- **REQUEST CHANGES**: Critical issues that block merge
- **COMMENT**: Quality suggestions but no blockers"""
        
        # Return detailed analysis instructions matching the sample format
        comprehensive_review = {
            "tool_name": "code_review",
            "analysis_context": "Comprehensive PR Code Review - Generate Structured Analysis",
            "timestamp": datetime.now().isoformat(),
            "pr_url": pr_url,
            "pr_owner": owner,
            "pr_repo": repo,
            "pr_number": pr_number,
            "focus": focus,
            "max_diff_lines": max_diff_lines,
            
            "processing_instructions": {
                "overview": f"Extract PR data and generate comprehensive ANALYSIS-ONLY code review in structured format. Focus: {focus or 'comprehensive quality assessment'}. Apply deep thinking about simplification opportunities and standards compliance.",
                
                "data_extraction_steps": [
                    f"Execute: gh api \"repos/{owner}/{repo}/pulls/{pr_number}\" (PR details)",
                    f"Execute: gh pr diff {pr_number} --repo {owner}/{repo} | head -n {max_diff_lines} (code changes)",
                    f"Execute: gh api \"repos/{owner}/{repo}/pulls/{pr_number}/files\" (files changed)",
                    f"Execute: gh api \"repos/{owner}/{repo}/pulls/{pr_number}/commits\" | jq -r '.[].sha' | tail -1 | xargs -I {{}} gh api \"repos/{owner}/{repo}/commits/{{}}/check-runs\" (CI status)",
                    f"Execute: gh api \"repos/{owner}/{repo}/pulls/{pr_number}/reviews\" (existing reviews)",
                    "Extract JIRA ticket from PR title/body (SI-XXXX pattern)"
                ],
                
                "required_output_format": """
# 🔍 **Code Review Analysis: [PR_TITLE]**

**Repository**: [OWNER]/[REPO] #[NUMBER]  
**PR Title**: [ACTUAL_PR_TITLE]  
**Overall Assessment**: [APPROVE|REQUEST_CHANGES|COMMENT]  
**Author**: [USERNAME]  
**JIRA**: [SI-XXXX or none]  
**Focus Area**: [FOCUS or comprehensive]  
**Review Date**: [TIMESTAMP]  

---

## 🚨 **CRITICAL VIOLATIONS ANALYSIS**

### Blocking Issues
- [ ] **[Issue Description]** - [file.java:line] 
  *Resolution: [Specific actionable solution]*

### Merge Readiness
- **CI Status**: [X passed, Y failed, Z pending]  
- **Merge Conflicts**: [None|Present in file.java]  
- **Branch Protection**: [Compliant|Violations found]  

---

## 📋 **CODE QUALITY ASSESSMENT**

### Java Standards Compliance
- [ ] **Import Organization**: [Compliant|Issues found in file.java:line]  
- [ ] **Lombok Usage**: [Appropriate|@RequiredArgsConstructor needed in file.java:line]  
- [ ] **Error Handling**: [Robust|Missing validation in file.java:line]  
- [ ] **Constants vs Hardcoded Values**: [Good|Replace hardcoded values in file.java:line]  

### Code Simplification Opportunities
- **Complexity Assessment**: [Simple|Medium|Complex] 
- **Simplification Potential**: [Analysis of whether code could be simpler]
- **Pattern Adherence**: [Follows established patterns|Deviates in file.java:line]

---

## ✅ **TEST COVERAGE VERIFICATION**

### New Test Analysis
- **Test Files Added/Modified**: [List test files]  
- **Coverage Type**: [Unit tests for errors|Integration for valid flows]  
- **Test Fixtures**: [Proper usage|Hardcoded values found in test.java:line]  
- **Naming Conventions**: [Clear|Unclear in test.java:line]  

### Testing Strategy Assessment
- **90% Rule Compliance**: [Unit tests focus on error scenarios: Yes|No]  
- **Integration Coverage**: [Valid scenarios + complex errors covered: Yes|No]  

---

## 🔒 **SECURITY REVIEW**

### Data Protection
- [ ] **Sensitive Data Exposure**: [None found|Issues in file.java:line]  
- [ ] **Input Validation**: [Appropriate|Missing in file.java:line]  
- [ ] **Authentication Changes**: [None|Requires review in file.java:line]  

---

## 🏢 **BUSINESS LOGIC COMPLIANCE**

### Standards Adherence
- **Business Constants**: [Used appropriately|Hardcoded values in file.java:line]  
- **GraphQL Schema**: [No changes|Changes require enum sync in schema.graphql:line]  
- **Field Naming**: [Consistent|Issues in file.java:line]  

---

## 🎫 **JIRA TICKET COMPLIANCE**

### Requirements Analysis
- **Ticket**: [SI-XXXX: Brief description]  
- **Implementation Match**: [Exact match|Over-engineered|Under-engineered]  
- **Acceptance Criteria**: [All fulfilled|Missing: specific criteria]  
- **Scope Appropriateness**: [Appropriate|Scope creep detected]  

---

## 🎯 **ACTIONABLE FEEDBACK**

### High Priority Actions
1. **[Specific action required]** - [file.java:line]  
   *Suggestion: [Concrete improvement with reasoning]*

2. **[Another action]** - [file.java:line]  
   *Suggestion: [Specific guidance]*

### Code Simplification Recommendations
- **Architecture**: [Analysis of whether current approach is optimal]  
- **Abstraction Opportunities**: [Specific suggestions for better abstractions]  
- **Pattern Improvements**: [Recommendations for following established patterns]  

### Quality Improvements
- **Standards**: [Specific code quality improvements needed]  
- **Maintainability**: [Suggestions for long-term code health]  
- **Performance**: [Any performance considerations identified]  

---

## 📊 **OVERALL RECOMMENDATION**

**Decision**: [APPROVE|REQUEST CHANGES|COMMENT]  

**Reasoning**: [Clear explanation of the decision based on findings]  

**Next Steps**: [Specific actions for PR author]  

**Confidence Level**: [High|Medium|Low] - [Brief justification]  

---

*Review completed with deep analysis of code simplification opportunities and standards compliance.*
""",
                
                "analysis_requirements": [
                    "CRITICAL: Generate analysis in the EXACT format above",
                    "Use actual PR data (title, files, lines) - no placeholders",
                    "Focus on ANALYSIS ONLY - no code changes or implementations",
                    "Apply deep thinking about simplification opportunities",
                    "Assess whether implementation matches JIRA ticket requirements",
                    "Provide specific file:line references for all findings",
                    "Ensure all sections are completed with actual analysis",
                    "Replace ALL bracketed placeholders with real data/analysis"
                ]
            },
            
            "quality_standards": {
                "focus_areas": [
                    "Code Simplification: Could this be simpler? Are there unnecessary complexities?",
                    "Standards Compliance: Does this follow established patterns and quality standards?",
                    "Architectural Coherence: Does this fit well with existing design patterns?",
                    "Business Logic Alignment: Do the changes properly match the ticket specification?",
                    "Test Strategy: Are tests comprehensive and following best practices?"
                ],
                "assessment_depth": "Comprehensive analysis covering violations, quality, tests, security, business logic, and JIRA compliance",
                "output_specificity": "All findings must include specific file:line references and actionable solutions"
            },
            
            "external_context": context_content,
            
            "success_criteria": {
                "format_compliance": "Output matches the required structured format exactly",
                "data_accuracy": "All PR information extracted successfully with real file:line references",
                "analysis_completeness": "All sections completed with thorough analysis (no placeholders remaining)",
                "actionable_output": "Specific, thoughtful recommendations provided (analysis only, no code changes)",
                "deep_insights": "Meaningful assessment of code simplification and standards compliance",
                "ticket_alignment": "Thorough analysis of whether implementation matches JIRA ticket specification"
            }
        }
        
        logger.info(f"Code review comprehensive analysis instructions generated for PR: {pr_url}")
        return comprehensive_review
        
    except Exception as e:
        logger.error(f"Code review instruction generation error: {str(e)}")
        return {
            "error": f"Code review instruction generation failed: {str(e)}",
            "pr_url": pr_url,
            "type": type(e).__name__,
            "suggestion": "Check PR URL format and try again"
        }



# TEMPLATE PATTERN: Start the MCP Server over HTTP
# This allows persistent server deployment with HTTP endpoint
# Much more efficient than stdio for containerized deployment
def main():
    """Main function to start the MCP Tools server"""
    logger.info("Starting MCP Tools Server...")
    logger.info(f"Server configuration: Port {Config.DEFAULT_PORT}, Log Level {Config.LOG_LEVEL}")
    
    try:
        # Get the FastAPI app from FastMCP
        app = mcp.http_app()
        
        # Health endpoint for container health checks
        async def health_check(request):
            return JSONResponse({
                "status": "healthy",
                "service": "mcp-tools",
                "version": "1.0.0",
                "transport": "FastMCP HTTP Streaming",
                "timestamp": datetime.now().isoformat(),
                "port": Config.DEFAULT_PORT
            })
        
        # Add shell authentication routes for Claude Code compatibility
        auth_routes = [
            Route('/health', health_check, methods=['GET']),
            Route('/.well-known/oauth-authorization-server', oauth_authorization_server, methods=['GET']),
            Route('/.well-known/oauth-authorization-server-mcp', oauth_authorization_server_mcp, methods=['GET']),
            Route('/.well-known/oauth-protected-resource', oauth_protected_resource, methods=['GET']),
            Route('/register', register_client, methods=['POST']),
            Route('/auth', authorize, methods=['GET']),
            Route('/token', token_endpoint, methods=['POST']),
        ]
        
        for route in auth_routes:
            app.routes.append(route)
        
        logger.info("FastMCP HTTP Streaming server initialized with shell authentication")
        logger.info("Available tools: echo, get_system_info, pr_violations, code_review")
        logger.info("Authentication endpoints: /.well-known/oauth-authorization-server, /register, /auth, /token")
        
        # Run with uvicorn
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=Config.DEFAULT_PORT,
            log_level=Config.LOG_LEVEL.lower()
        )
        
    except Exception as e:
        logger.error(f"Failed to start MCP Tools server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()