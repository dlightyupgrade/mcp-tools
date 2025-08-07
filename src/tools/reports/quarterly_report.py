#!/usr/bin/env python3
"""
Quarterly Team Performance Reporting Tool with 3-Agent Coordination

PREREQUISITES: Run `setup_prerequisites` tool to validate all required tools and services.
This tool depends on GitHub CLI, Atlassian MCP, JIRA access, and command-line utilities.

This tool generates comprehensive quarterly team performance reports with anonymized metrics,
development velocity analysis, and technical achievement summaries using the proven 3-agent
coordination system for enhanced JIRA→GitHub PR bridging and comprehensive analysis.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from fastmcp import FastMCP
from .base import ToolBase, get_context_fallback
from .coordinator import JiraGithubReportCoordinator

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
        
        **Natural Language Triggers:**
        - "quarterly team report for [team] Q[#] [year]" 
        - "generate [team] quarterly report [year] Q[#]"
        - "team performance analysis [team] [quarter] [year]"
        - "SI quarterly report Q2 2025"
        - "PLAT team performance Q1 2024" 
        - "create quarterly report for CORE team Q3 2025"
        
        **What this tool does:**
        Returns comprehensive instructions for analyzing team performance including JIRA ticket 
        completion, GitHub commits, technical focus areas, and development velocity. Uses real 
        JIRA MCP and GitHub CLI commands - does NOT execute analysis directly.
        
        **Perfect for:** Team retrospectives, performance reviews, quarterly planning, 
        velocity tracking, technical achievement summaries, management reporting.
        
        Args:
            team_prefix: Team/project prefix ("SI", "PLAT", "CORE", "INFRA", etc.)
            year: Year for the quarter (2020-2030)
            quarter: Quarter number (1-4: Q1=Jan-Mar, Q2=Apr-Jun, Q3=Jul-Sep, Q4=Oct-Dec)
            description: Optional focus ("performance analysis", "technical achievements", etc.)
            
        Returns:
            Comprehensive team analysis instructions with JIRA MCP and GitHub CLI commands
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
            
            # Get team-specific customizations for 3-agent coordination
            team_customizations = JiraGithubReportCoordinator.create_team_quarterly_customizations()
            
            # Generate 3-agent coordination instructions
            subagent_1 = JiraGithubReportCoordinator.generate_base_subagent_1_instructions(
                "team_quarterly",
                team_prefix,
                start_date,
                end_date,
                team_customizations["jira_query_customizer"]
            )
            
            subagent_2 = JiraGithubReportCoordinator.generate_base_subagent_2_instructions(
                "team_quarterly", 
                team_prefix,
                start_date,
                end_date,
                team_customizations["github_query_customizer"]
            )
            
            # Custom analysis steps for team quarterly reports
            team_analysis_steps = [
                "## Team Data Synthesis",
                "# Combine Subagent 1 JIRA analysis with Subagent 2 GitHub metrics",
                "# Cross-reference team JIRA activity with GitHub repository contributions",
                "# Calculate team-wide productivity and collaboration metrics",
                "",
                "## Enhanced Team Performance Metrics", 
                "# Team productivity: JIRA tickets + GitHub PRs with proper attribution",
                "# Collaboration indicators: Cross-repository work and code review patterns",
                "# Technical focus: Team specialization areas from combined dataset",
                "# Development velocity: Team throughput and delivery metrics",
                "",
                "## Team Attribution and Privacy",
                "# Identify team member contributions while maintaining anonymization",
                "# Generate team-level insights without individual performance data",
                "# Calculate team velocity and productivity patterns",
                "# Ensure privacy-compliant reporting with aggregate metrics only",
                "",
                "## Team Development Insights",
                "# Generate team-level recommendations for improved productivity",
                "# Identify team strengths and collaboration opportunities",
                "# Suggest technical focus areas for enhanced team performance",
                "# Create actionable team improvement strategies"
            ]
            
            subagent_3 = JiraGithubReportCoordinator.generate_base_subagent_3_instructions(
                "team_quarterly",
                f"{team_prefix} Team Quarterly Report - {quarter_name}",
                team_analysis_steps,
                ["comprehensive_team_report", "team_attribution_analysis", "team_performance_recommendations", "team_improvement_opportunities"]
            )
            
            # Generate comprehensive coordination instructions
            coordination_instructions = JiraGithubReportCoordinator.generate_coordination_instructions(
                "quarterly_team_report",
                f"Team Quarterly Performance Report - {quarter_name}",
                subagent_1,
                subagent_2, 
                subagent_3,
                [
                    "Subagent 1 discovers team JIRA activity and establishes team member identification",
                    "Subagent 2 uses team data for comprehensive GitHub analysis with PR linking",
                    "Subagent 3 synthesizes team data while maintaining anonymization requirements",
                    "All subagents coordinate for team-level insights without individual attribution",
                    "Enhanced team productivity analysis with cross-source validation"
                ]
            )
            
            # Load external context for quarterly reporting
            context_content = ToolBase.load_external_context(
                "/Users/dlighty/code/llm-context/QUARTERLY-REPORT-CONTEXT.md",
                get_context_fallback("quarterly_report")
            )
            
            # Return detailed analysis instructions with 3-agent coordination
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
                    "overview": f"Generate comprehensive quarterly team performance report for {team_prefix} team covering {quarter_name} using 3-subagent coordination system. Focus: {description or 'comprehensive team performance analysis with anonymized metrics and enhanced JIRA→GitHub PR bridging'}.",
                    
                    
                    "coordination_instructions": coordination_instructions,
                    
                    "enhanced_analysis_requirements": [
                        "**Enhanced Team JIRA Analysis (Subagent 1):**",
                        "- Total team tickets completed in quarter with PR link discovery",
                        "- Team issue type distribution and technical focus areas",
                        "- Team priority distribution and completion patterns",
                        "- PR link extraction from descriptions and comments for attribution",
                        "- Cross-reference team ticket completion with actual code delivery",
                        "",
                        "**Enhanced Team GitHub Analysis (Subagent 2):**", 
                        "- Detailed team PR metrics using JIRA-discovered links",
                        "- Team code contribution quality (review feedback, merge rates)", 
                        "- Repository diversity and team contribution complexity evolution",
                        "- Commit patterns within JIRA-linked PRs vs standalone team development",
                        "- Team technical growth indicators from code change analysis",
                        "",
                        "**Cross-Reference Team Attribution Analysis (Subagent 3):**",
                        "- Team JIRA ticket completion vs GitHub PR delivery alignment",
                        "- Team work attribution accuracy and process improvement opportunities",
                        "- Team productivity metrics with enhanced accuracy and anonymization",
                        "- Team learning velocity based on technical complexity progression",
                        "",
                        "**Team Performance Insights (Subagent 3):**",
                        "- Team strength areas from consistent high-performance patterns",
                        "- Team growth opportunities identified from contribution gap analysis", 
                        "- Team technical skill development trajectory with evidence",
                        "- Team collaboration and development recommendations based on data patterns",
                        "",
                        "**Privacy and Team Anonymization:**",
                        "- Individual contributor names anonymized in final team report",
                        "- Team-level aggregate metrics only (no individual performance data)",
                        "- Focus on team patterns and collaboration, not individual attribution",
                        "- Team insights while maintaining individual privacy requirements"
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
                
                "enhanced_success_criteria": {
                    "subagent_coordination": "All 3 subagents executed successfully with proper data handoff for team analysis",
                    "jira_pr_bridging": "PR links successfully extracted from team JIRA tickets with high attribution accuracy",
                    "github_enhancement": "Team GitHub metrics collected using JIRA-discovered PR links for improved accuracy", 
                    "cross_reference_analysis": "Team JIRA work completion validated against GitHub PR delivery",
                    "team_insights": "Enhanced team performance insights generated from coordinated analysis",
                    "attribution_accuracy": "Team work attribution accuracy >= 85% between JIRA and GitHub data",
                    "privacy_compliance": "Individual contributor data anonymized while maintaining team-level insights"
                },
                
                "enhanced_troubleshooting": {
                    "subagent_coordination_issues": "Verify all 3 subagents can execute in coordinated sequence without conflicts for team analysis",
                    "jira_pr_extraction_issues": "Check team JIRA ticket descriptions and comments contain GitHub PR URLs",
                    "github_pr_access_issues": "Verify GitHub CLI can access discovered PR URLs from team JIRA tickets",
                    "attribution_accuracy_low": "Review team JIRA ticket PR linking practices and suggest improvements",
                    "cross_reference_failures": "Validate team JIRA ticket completion dates align with PR merge dates",
                    "team_data_issues": "Verify team has sufficient JIRA assignments and GitHub contributions in specified period",
                    "rate_limit_coordination": "Implement proper rate limiting across all 3 subagents for team data collection",
                    "anonymization_issues": "Ensure team reporting maintains individual privacy while providing team insights"
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