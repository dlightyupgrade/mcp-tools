#!/usr/bin/env python3
"""
Quarterly Team Performance Reporting Tool

PREREQUISITES - MUST BE CONFIGURED BEFORE USE:
• GitHub CLI: `brew install gh` + `gh auth login`
• Atlassian MCP Server: Authentication and cloud ID configuration required
• JIRA Access: Team must have access to JIRA project with appropriate permissions
• JQ: `brew install jq` for JSON processing

This tool generates comprehensive quarterly team performance reports with anonymized metrics,
development velocity analysis, and technical achievement summaries by RETURNING INSTRUCTIONS
for Claude Code to execute actual API calls rather than performing analysis directly.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from fastmcp import FastMCP
from .base import ToolBase, get_context_fallback

logger = logging.getLogger(__name__)


def register_quarterly_team_report_tool(mcp: FastMCP):
    """Register quarterly team report tool with the FastMCP server"""
    
    @mcp.tool
    def quarterly_team_report(
        team_prefix: str,
        year: int,
        quarter: int,
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Generate comprehensive quarterly team performance report with anonymized metrics - INSTRUCTIONS ONLY.
        
        Provides detailed step-by-step instructions for Claude Code to perform comprehensive team
        performance analysis including JIRA tickets, GitHub commits, technical focus areas, and
        development velocity using actual API calls. Does NOT execute analysis directly - returns
        structured instructions for external execution.
        
        Args:
            team_prefix: Team/project prefix (e.g., "SI", "PLAT", "CORE")
            year: Year for the quarter (e.g., 2025)
            quarter: Quarter number (1-4)
            description: Optional description of analysis focus
            
        Returns:
            Dictionary containing detailed processing instructions for Claude Code execution
        """
        logger.info(f"Quarterly team report requested: {team_prefix} Q{quarter} {year}")
        
        try:
            # Validate inputs
            if not team_prefix or not team_prefix.isalpha():
                return ToolBase.create_error_response(
                    "Invalid team_prefix. Must be alphabetic (e.g., 'SI', 'PLAT')",
                    error_type="validation_error"
                )
            
            if not 1 <= quarter <= 4:
                return ToolBase.create_error_response(
                    "Invalid quarter. Must be 1-4",
                    error_type="validation_error"
                )
            
            if not 2020 <= year <= 2030:
                return ToolBase.create_error_response(
                    "Invalid year. Must be between 2020-2030",
                    error_type="validation_error"
                )
            
            # Calculate quarter date ranges
            quarter_starts = {
                1: (1, 1),   # Q1: Jan 1 - Mar 31
                2: (4, 1),   # Q2: Apr 1 - Jun 30
                3: (7, 1),   # Q3: Jul 1 - Sep 30
                4: (10, 1),  # Q4: Oct 1 - Dec 31
            }
            
            quarter_ends = {
                1: (3, 31),
                2: (6, 30), 
                3: (9, 30),
                4: (12, 31)
            }
            
            start_month, start_day = quarter_starts[quarter]
            end_month, end_day = quarter_ends[quarter]
            
            start_date = f"{year}-{start_month:02d}-{start_day:02d}"
            end_date = f"{year}-{end_month:02d}-{end_day:02d}"
            quarter_name = f"Q{quarter} {year}"
            
            # Load external context for quarterly reporting
            context_content = ToolBase.load_external_context(
                "/Users/dlighty/code/llm-context/QUARTERLY-REPORT-CONTEXT.md",
                get_context_fallback("quarterly_report")
            )
            
            # Return detailed analysis instructions
            quarterly_instructions = {
                "tool_name": "quarterly_team_report",
                "analysis_context": f"Quarterly Team Performance Report - {quarter_name}",
                "timestamp": ToolBase.create_success_response({})["timestamp"],
                "team_prefix": team_prefix,
                "year": year,
                "quarter": quarter,
                "quarter_name": quarter_name,
                "start_date": start_date,
                "end_date": end_date,
                "description": description,
                
                "processing_instructions": {
                    "overview": f"Generate comprehensive quarterly team performance report for {team_prefix} team covering {quarter_name}. Focus: {description or 'comprehensive team performance analysis with anonymized metrics'}.",
                    
                    "prerequisite_validation": [
                        "Verify GitHub CLI authentication: `gh auth status`",
                        "Verify Atlassian MCP server connection and cloud ID access",
                        "Confirm JIRA project access for team prefix queries",
                        "Ensure `jq` is available for JSON processing"
                    ],
                    
                    "data_collection_steps": [
                        "## JIRA Data Collection",
                        f"Execute: mcp__atlassian__searchJiraIssuesUsingJql(cloudId='credify.atlassian.net', jql='project = \"{team_prefix}\" AND created >= \"{start_date}\" AND created <= \"{end_date}\" ORDER BY created DESC', fields=['summary', 'description', 'status', 'issuetype', 'priority', 'created', 'assignee', 'components'], maxResults=250)",
                        "",
                        "## GitHub Data Collection", 
                        "# Find repositories for team using GitHub search",
                        f"Execute: gh search repos 'org:credify topic:{team_prefix.lower()} OR {team_prefix.lower()} in:name' --json name,url,defaultBranch",
                        "# For each repository found, collect commit data:",
                        f"Execute: gh api 'search/commits?q=author-date:{start_date}..{end_date}+org:credify+repo:REPO_NAME' --paginate",
                        "# Alternative if repo-specific search fails:",
                        f"Execute: gh api 'repos/credify/REPO_NAME/commits?since={start_date}T00:00:00Z&until={end_date}T23:59:59Z' --paginate",
                        "",
                        "## Team Member Identification",
                        "# Extract unique GitHub commit authors (anonymize in final report)",
                        "# Cross-reference JIRA assignees with GitHub authors",
                        "# Build contributor mapping while preserving privacy"
                    ],
                    
                    "analysis_requirements": [
                        "**JIRA Metrics Analysis:**",
                        "- Total tickets completed in quarter",
                        "- Issue type distribution (Story, Bug, Task, Epic, etc.)",
                        "- Priority distribution (Critical, High, Medium, Low)",
                        "- Average completion time by issue type",
                        "- Sprint velocity trends (if sprint data available)",
                        "",
                        "**GitHub Metrics Analysis:**", 
                        "- Total commits by team members",
                        "- Active repository count",
                        "- Lines of code changes (additions/deletions)",
                        "- Pull request metrics (if accessible)",
                        "- Repository activity patterns",
                        "",
                        "**Team Velocity Calculation:**",
                        "- Tickets per contributor ratio",
                        "- Commits per contributor ratio", 
                        "- Cross-functional collaboration indicators",
                        "- Technical focus area identification from ticket summaries",
                        "",
                        "**Privacy and Anonymization:**",
                        "- Individual contributor names anonymized in final report",
                        "- Aggregate metrics only (no individual performance data)",
                        "- Focus on team patterns, not individual attribution"
                    ],
                    
                    "required_output_format": f"""
# {team_prefix} Team Quarterly Performance Report - {quarter_name}

## Executive Summary
*Report generated on {{timestamp}} for {team_prefix} team covering {quarter_name} ({{start_date}} to {{end_date}})*

{{executive_summary_paragraph_with_key_achievements}}

## JIRA Analysis

### Issue Completion Metrics
- **Total Issues Completed**: {{total_tickets}}
- **Issue Type Breakdown**:
  - Stories: {{story_count}} ({{story_percentage}}%)
  - Bugs: {{bug_count}} ({{bug_percentage}}%)
  - Tasks: {{task_count}} ({{task_percentage}}%)
  - Epics: {{epic_count}} ({{epic_percentage}}%)

### Priority Distribution
- **Critical**: {{critical_count}} issues
- **High**: {{high_count}} issues  
- **Medium**: {{medium_count}} issues
- **Low**: {{low_count}} issues

### Completion Patterns
- **Average Resolution Time**: {{avg_resolution_days}} days
- **Sprint Velocity**: {{sprint_velocity}} (if applicable)

## GitHub Analysis

### Development Activity
- **Total Commits**: {{total_commits}}
- **Active Repositories**: {{active_repo_count}}
- **Lines Changed**: +{{lines_added}} / -{{lines_deleted}}

### Collaboration Metrics
- **Unique Contributors**: {{unique_contributors}} (anonymized)
- **Cross-Repository Work**: {{cross_repo_percentage}}%
- **Commit Frequency**: {{commits_per_week}} commits/week average

## Technical Focus Areas

Based on JIRA ticket summaries and GitHub commit messages:

1. **{{focus_area_1}}**: {{description_and_impact}}
2. **{{focus_area_2}}**: {{description_and_impact}}  
3. **{{focus_area_3}}**: {{description_and_impact}}

## Team Velocity Assessment

### Productivity Metrics
- **Tickets per Contributor**: {{tickets_per_contributor}}
- **Commits per Contributor**: {{commits_per_contributor}}
- **Velocity Score**: {{velocity_calculation}} (weighted metric)

### Development Velocity
- **Code Quality Focus**: {{code_quality_indicators}}%
- **Feature Development**: {{feature_work_percentage}}%
- **Bug Resolution**: {{bug_resolution_percentage}}%
- **Technical Debt**: {{tech_debt_percentage}}%

## Quarter Achievements

### Key Accomplishments
- {{achievement_1}}
- {{achievement_2}}
- {{achievement_3}}

### Technical Improvements
- {{technical_improvement_1}}
- {{technical_improvement_2}}

## Data Sources and Methodology

### Data Collection Period
- **Start Date**: {start_date}
- **End Date**: {end_date}
- **Quarter**: {quarter_name}

### Data Sources
- **JIRA**: Project {team_prefix} ticket completion and workflow data
- **GitHub**: Credify organization repositories with {team_prefix} team involvement
- **Analysis Tools**: MCP Atlassian integration + GitHub CLI + JQL queries

### Privacy Compliance
- **Individual Attribution**: Removed from final report
- **Aggregate Metrics**: Team-level analysis only
- **Anonymization**: Contributor identification replaced with role-based references
- **Data Retention**: Analysis data not persisted beyond report generation

### Methodology Notes
- **Team Identification**: Based on JIRA project assignment and GitHub repository access
- **Velocity Calculation**: Weighted combination of ticket completion rate and commit frequency
- **Technical Focus**: Derived from ticket summary keyword analysis and commit message patterns
- **Quality Metrics**: Cross-validated between JIRA labels and GitHub PR review data where available

*Generated using MCP Tools Quarterly Reporting with real-time data collection*
""",
                },
                
                "external_context": context_content,
                
                "success_criteria": {
                    "data_collection": "JIRA tickets and GitHub commits successfully retrieved for the specified quarter",
                    "team_identification": "Team members identified through JIRA assignments and GitHub contributions",
                    "metrics_calculation": "Productivity and velocity metrics calculated with appropriate anonymization",
                    "technical_analysis": "Technical focus areas identified from ticket summaries and commit messages", 
                    "report_generation": "Comprehensive markdown report generated with all required sections",
                    "privacy_compliance": "Individual contributor data anonymized in final output"
                },
                
                "troubleshooting": {
                    "jira_access_issues": "Verify Atlassian MCP server configuration and cloud ID permissions",
                    "github_rate_limits": "Use GitHub CLI authentication to increase API rate limits",
                    "empty_results": "Verify team prefix exists in JIRA projects and GitHub repositories",
                    "permission_errors": "Ensure sufficient JIRA project permissions and GitHub organization access"
                }
            }
            
            logger.info(f"Quarterly team report instructions generated for: {team_prefix} Q{quarter} {year}")
            return quarterly_instructions
            
        except Exception as e:
            logger.error(f"Error generating quarterly team report instructions: {str(e)}")
            return ToolBase.create_error_response(
                f"Failed to generate quarterly team report instructions: {str(e)}",
                error_type=type(e).__name__
            )


def get_context_fallback(context_type: str) -> str:
    """Get fallback context content for quarterly report"""
    
    if context_type == "quarterly_report":
        return """# Quarterly Team Performance Analysis Guidelines

## Data Collection Strategy
- **JIRA Analysis**: Focus on completed tickets within quarter boundaries
- **GitHub Analysis**: Team repository activity and commit patterns  
- **Team Identification**: Cross-reference JIRA assignees with GitHub contributors
- **Privacy First**: Anonymize individual contributors in final reporting

## Key Metrics Framework
- **Productivity**: Tickets completed, commits made, lines changed
- **Velocity**: Work completion rate, cross-functional collaboration
- **Technical Focus**: Areas of development emphasis from ticket analysis
- **Quality Indicators**: Bug resolution patterns, technical debt management

## Report Structure
1. **Executive Summary**: Quarter overview with key achievements
2. **JIRA Analysis**: Issue metrics, priority distribution, completion patterns
3. **GitHub Analysis**: Development activity, collaboration metrics
4. **Technical Focus Areas**: Primary development areas derived from data
5. **Team Velocity Assessment**: Productivity and development velocity metrics
6. **Data Sources and Methodology**: Transparency and reproducibility information

## Privacy and Ethics
- **No Individual Performance Reviews**: Focus on team-level metrics only
- **Anonymized Reporting**: Individual contributor names not included in final output
- **Aggregate Analysis**: All metrics presented as team totals or averages
- **Data Retention**: Analysis data not stored beyond report generation

## Quality Validation
- **Cross-Source Verification**: JIRA tickets cross-referenced with GitHub activity
- **Date Range Accuracy**: Strict quarter boundary enforcement
- **Team Boundary Validation**: Verify contributors belong to specified team prefix
- **Metric Consistency**: Ensure all calculations use consistent data sets"""
    
    return ""