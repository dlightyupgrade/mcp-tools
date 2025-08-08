#!/usr/bin/env python3
"""
Code Review Analysis Tool

Perform comprehensive code quality review of pull requests.
Provides step-by-step instructions for external agents to analyze code quality, 
security, performance, and maintainability aspects.
"""

import logging
from typing import Dict, Any

from fastmcp import FastMCP
from common.base import ToolBase, get_context_fallback
from common.config.settings import Config

logger = logging.getLogger(__name__)


def register_code_review_tool(mcp: FastMCP):
    """Register the code_review tool with the FastMCP server"""
    
    @mcp.tool
    def code_review(pr_url: str, focus: str = "", max_diff_lines: int = 2000) -> Dict[str, Any]:
        """
        Comprehensive code quality review of pull requests - ANALYSIS INSTRUCTIONS ONLY.
        
        **Natural Language Triggers:**
        - "code review [PR_URL]"
        - "review this PR [PR_URL]" 
        - "analyze code quality in [PR_URL]"
        - "check code standards [PR_URL]"
        - "security review [PR_URL]"
        - "performance review [PR_URL]"
        - "review pr for [focus] [PR_URL]"
        
        **What this tool does:**
        Returns comprehensive instructions for analyzing code quality, security, performance, and 
        maintainability. Focuses on deep code analysis, standards compliance, and identifying 
        improvement opportunities. Does NOT execute review - provides detailed analysis framework.
        
        **Perfect for:** Code quality assessment, security audits, performance optimization, 
        standards compliance checking, mentoring feedback, pre-merge review.
        
        Args:
            pr_url: GitHub PR URL to review (e.g., https://github.com/owner/repo/pull/123)
            focus: Optional focus area ("security", "performance", "tests", "maintainability")
            max_diff_lines: Maximum diff lines to analyze (default: 2000)
            
        Returns:
            Detailed instructions for Claude Code to perform comprehensive code review
        """
        logger.info(f"code_review tool called for: {pr_url}")
        
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
            
            # Load external context file
            context_content = ToolBase.load_external_context(
                "/Users/dlighty/code/llm-context/CODE-REVIEW-CONTEXT.md",
                get_context_fallback("code_review")
            )
            
            # Return detailed analysis instructions
            comprehensive_review = {
                "tool_name": "code_review",
                "analysis_context": "Comprehensive PR Code Review - Generate Structured Analysis",
                "timestamp": ToolBase.create_success_response({})["timestamp"],
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
                        "Extract JIRA ticket from PR title/body (SI-XXXX pattern)",
                        "If JIRA ticket found, execute: mcp__atlassian__getJiraIssue(cloudId='credify.atlassian.net', issueIdOrKey='TICKET_ID', fields=['summary', 'description', 'status', 'assignee', 'priority']) to get ticket details for compliance analysis"
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

### Standards Compliance
- [ ] **Import Organization**: [Compliant|Issues found in file.java:line]  
- [ ] **Pattern Usage**: [Appropriate|Issues needed in file.java:line]  
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
- **Schema Changes**: [No changes|Changes require sync in schema.graphql:line]  
- **Field Naming**: [Consistent|Issues in file.java:line]  

---

## 🎫 **JIRA TICKET COMPLIANCE**

### Requirements Analysis
- **Ticket**: [SI-XXXX: Title from Atlassian MCP or "Not found"]  
- **JIRA Status**: [Current status from Atlassian MCP or "N/A"]  
- **Priority**: [Priority from Atlassian MCP or "N/A"]  
- **Assignee**: [Assignee from Atlassian MCP or "Unassigned"]  
- **Implementation Match**: [Exact match|Over-engineered|Under-engineered]  
- **Acceptance Criteria**: [All fulfilled|Missing: specific criteria from JIRA description]  
- **Scope Appropriateness**: [Appropriate|Scope creep detected]  

### JIRA Integration Details
- **Ticket Retrieved**: [Yes|No - provide JIRA link if manual lookup needed]  
- **Description Match**: [PR changes align with JIRA description: Yes|No|Partial]  
- **Status Consistency**: [PR status aligns with JIRA workflow: Yes|No]  

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
                        "Extract JIRA ticket ID from PR title/body using regex pattern: SI-\\d+",
                        "If JIRA ticket found, execute Atlassian MCP command to retrieve ticket details",
                        "Use JIRA ticket data (summary, description, status, assignee, priority) for compliance analysis",
                        "Assess whether implementation matches JIRA ticket requirements based on retrieved data",
                        "Provide specific file:line references for all findings",
                        "Ensure all sections are completed with actual analysis",
                        "Replace ALL bracketed placeholders with real data/analysis",
                        "Include JIRA integration status in analysis even if ticket not found"
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
                    "jira_integration": "JIRA ticket extracted from PR and Atlassian MCP called if ticket found",
                    "jira_compliance": "JIRA ticket data (if available) used for requirements and compliance analysis",
                    "ticket_alignment": "Thorough analysis of whether implementation matches JIRA ticket specification using retrieved data"
                }
            }
            
            logger.info(f"Code review comprehensive analysis instructions generated for PR: {pr_url}")
            return comprehensive_review
            
        except Exception as e:
            logger.error(f"Code review instruction generation error: {str(e)}")
            return ToolBase.create_error_response(
                f"Code review instruction generation failed: {str(e)}",
                pr_url,
                type(e).__name__
            )