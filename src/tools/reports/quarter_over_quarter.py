#!/usr/bin/env python3
"""
Quarter-over-Quarter Performance Analysis Tools - ENHANCED 3-AGENT APPROACH

PREREQUISITES: Run `setup_prerequisites` tool to validate all required tools and services.
This tool depends on GitHub CLI, Atlassian MCP, JIRA access, and command-line utilities.

Generate comprehensive multi-quarter team performance trend analysis with team size tracking,
velocity changes, and comparative metrics across time periods using the proven 3-agent
coordination approach: JIRA Analysis → GitHub Metrics → Report Generation.
Returns INSTRUCTIONS for Claude Code to execute actual API calls rather than performing analysis directly.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

from fastmcp import FastMCP
from .base import ToolBase
from .coordinator import JiraGithubReportCoordinator

logger = logging.getLogger(__name__)


def register_quarter_over_quarter_tool(mcp: FastMCP):
    """Register quarter-over-quarter analysis tool with the FastMCP server"""
    
    @mcp.tool
    def quarter_over_quarter_analysis(
        team_prefix: str,
        period: str,
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Generate comprehensive quarter-over-quarter team performance analysis with team size tracking - INSTRUCTIONS ONLY.
        
        **Natural Language Triggers:**
        - "quarter over quarter analysis for [team] [period]"
        - "team performance trends [team] [year] vs [year]" 
        - "QoQ analysis for [team] team covering [period]"
        - "compare SI team performance 2024 vs 2023"
        - "PLAT team quarter-over-quarter trends 2023-2025"
        - "analyze team growth patterns [team] [multi-year period]"
        - "team velocity changes over multiple quarters"
        - "retention analysis [team] team [period]"
        
        **What this tool does:**
        Returns comprehensive instructions for multi-quarter team performance trend analysis 
        including team size evolution, velocity patterns, retention rates, and comparative 
        metrics across time periods. Uses real JIRA MCP and GitHub CLI commands - does NOT 
        execute analysis directly.
        
        **Perfect for:** Team growth analysis, velocity trend tracking, retention monitoring, 
        multi-quarter planning, performance pattern identification, team stability assessment, 
        strategic resource planning, comparative quarterly reviews.
        
        Provides detailed step-by-step instructions for Claude Code to perform comprehensive 
        multi-quarter team performance trend analysis including team size evolution, velocity
        patterns, and comparative metrics using actual API calls. Does NOT execute analysis 
        directly - returns structured instructions for external execution.
        
        Args:
            team_prefix: Team/project prefix (e.g., "SI", "PLAT", "CORE")
            period: Analysis period like "2024" or "2023-2025"
            description: Optional description of analysis focus
            
        Returns:
            Dictionary containing detailed processing instructions for Claude Code execution
        """
        logger.info(f"Quarter-over-quarter analysis requested: {team_prefix} {period}")
        
        try:
            # Validate inputs
            if not team_prefix or not team_prefix.isalpha():
                return ToolBase.create_error_response(
                    "Invalid team_prefix. Must be alphabetic (e.g., 'SI', 'PLAT')",
                    error_type="validation_error"
                )
            
            # Parse period configuration
            try:
                if '-' in period:
                    start_year, end_year = map(int, period.split('-'))
                else:
                    start_year = end_year = int(period)
                    
                if not 2020 <= start_year <= 2030 or not 2020 <= end_year <= 2030:
                    raise ValueError("Years must be between 2020-2030")
                    
            except (ValueError, IndexError):
                return ToolBase.create_error_response(
                    "Invalid period format. Expected format: 'YYYY' or 'YYYY-YYYY'",
                    error_type="validation_error"
                )
            
            # Generate quarter list
            quarters = []
            for year in range(start_year, end_year + 1):
                for q in [1, 2, 3, 4]:
                    # Calculate quarter date ranges
                    quarter_starts = {1: (1, 1), 2: (4, 1), 3: (7, 1), 4: (10, 1)}
                    quarter_ends = {1: (3, 31), 2: (6, 30), 3: (9, 30), 4: (12, 31)}
                    
                    start_month, start_day = quarter_starts[q]
                    end_month, end_day = quarter_ends[q]
                    
                    start_date = f"{year}-{start_month:02d}-{start_day:02d}"
                    end_date = f"{year}-{end_month:02d}-{end_day:02d}"
                    
                    quarters.append({
                        "quarter_name": f"Q{q} {year}",
                        "year": year,
                        "quarter": q,
                        "start_date": start_date,
                        "end_date": end_date
                    })
            
            if len(quarters) < 2:
                return ToolBase.create_error_response(
                    "Analysis requires at least 2 quarters. Extend period or use quarterly_team_report for single quarters.",
                    error_type="validation_error"
                )
            
            # Load external context
            context_content = ToolBase.load_external_context(
                "/Users/dlighty/code/llm-context/QOQ-ANALYSIS-CONTEXT.md",
                get_context_fallback("quarter_over_quarter")
            )
            
            # Generate 3-agent coordination instructions using JiraGithubReportCoordinator
            customizations = JiraGithubReportCoordinator.create_quarter_over_quarter_customizations()
            
            # Generate subagent instructions for the analysis period
            subagent_1 = JiraGithubReportCoordinator.generate_base_subagent_1_instructions(
                analysis_type="quarter_over_quarter_analysis",
                team_prefix=team_prefix,
                start_date=quarters[0]["start_date"],
                end_date=quarters[-1]["end_date"],
                jira_query_customizer=f"Extended date range for trend analysis. Order by created ASC for chronological pattern analysis.",
                additional_steps=[
                    "## Multi-Quarter Team Composition Tracking",
                    "# Track unique assignees per quarter for team size evolution analysis",
                    "# Calculate quarter-over-quarter contributor retention rates",
                    "# Identify new team members joining and departing contributors by quarter",
                    "# Generate team stability metrics and turnover impact assessment"
                ]
            )
            
            subagent_2 = JiraGithubReportCoordinator.generate_base_subagent_2_instructions(
                analysis_type="quarter_over_quarter_analysis", 
                team_prefix=team_prefix,
                start_date=quarters[0]["start_date"],
                end_date=quarters[-1]["end_date"],
                github_query_customizer=customizations["github_query_customizer"],
                additional_steps=[
                    "## Quarter-by-Quarter GitHub Activity Analysis",
                    "# For each quarter, collect GitHub commit activity and contributor data",
                    "# Track commit frequency patterns and code contribution velocity changes",
                    "# Analyze repository activity diversity and technical focus evolution",
                    "# Calculate commits-per-contributor ratios for productivity trend analysis",
                    "# Cross-reference commit authors with JIRA assignees for team boundary accuracy"
                ]
            )
            
            subagent_3 = JiraGithubReportCoordinator.generate_base_subagent_3_instructions(
                analysis_type="quarter_over_quarter_analysis",
                report_name=f"{team_prefix} Quarter-over-Quarter Performance Analysis ({period})",
                additional_steps=[
                    "## Multi-Quarter Trend Analysis",
                    "# Calculate linear trend progressions for key performance metrics",
                    "# Perform statistical significance assessment for trend reliability",
                    "# Generate quarter-over-quarter percentage change calculations", 
                    "# Identify performance pattern changes and directional trends",
                    "",
                    "## Team Composition Evolution Analysis", 
                    "# Track team size changes across all analyzed quarters",
                    "# Calculate contributor retention rates and team stability metrics",
                    "# Analyze new contributor onboarding and departure patterns",
                    "# Generate team maturity and continuity assessment",
                    "",
                    "## Comparative Performance Insights",
                    "# Compare first quarter vs final quarter performance metrics",
                    "# Identify highest and lowest performing quarters with context",
                    "# Generate weighted velocity scores combining tickets and commits",
                    "# Provide strategic recommendations for team optimization"
                ],
                custom_output_sections=[
                    "executive_summary",
                    "team_size_evolution_analysis", 
                    "performance_trend_analysis",
                    "quarter_by_quarter_breakdown",
                    "strategic_insights_and_recommendations",
                    "comparative_analysis_summary",
                    "methodology_and_data_sources"
                ]
            )
            
            coordination_instructions = JiraGithubReportCoordinator.generate_coordination_instructions(
                tool_name="quarter_over_quarter_analysis",
                analysis_context=f"Quarter-over-Quarter Team Performance Analysis - {period}",
                subagent_1=subagent_1,
                subagent_2=subagent_2,
                subagent_3=subagent_3,
                coordination_notes=[
                    "Subagent 1 analyzes JIRA tickets across all quarters to extract team composition and assignment patterns",
                    "Subagent 2 uses discovered PR links to collect GitHub metrics with quarter-by-quarter breakdown",
                    "Subagent 3 performs comprehensive trend analysis and generates quarter-over-quarter comparisons",
                    "Extended analysis period requires careful data segmentation by quarter for accurate trend calculations",
                    "Team size tracking must maintain contributor privacy while providing meaningful aggregate insights",
                    "Statistical significance testing validates trend reliability for strategic decision making"
                ]
            )

            # Return detailed analysis instructions
            qoq_instructions = {
                "tool_name": "quarter_over_quarter_analysis",
                "analysis_context": f"Quarter-over-Quarter Team Performance Analysis - {period}",
                "timestamp": ToolBase.create_success_response({})["timestamp"],
                "team_prefix": team_prefix,
                "period": period,
                "start_year": start_year,
                "end_year": end_year,
                "total_quarters": len(quarters),
                "quarters": quarters,
                "description": description,
                
                # Include 3-agent coordination instructions
                **coordination_instructions,
                
                "legacy_processing_instructions": {
                    "overview": f"Generate comprehensive quarter-over-quarter team performance analysis for {team_prefix} team covering {len(quarters)} quarters from {start_year} to {end_year}. Focus: {description or 'team performance trends, size changes, and velocity patterns across multiple quarters'}.",
                    
                    
                    "multi_quarter_data_collection": [
                        "## Quarter-by-Quarter Data Collection",
                        "For each quarter in the analysis period, execute the following data collection steps:",
                        ""
                    ],
                    
                    "quarter_data_collection_template": [
                        "### {quarter_name} Data Collection",
                        "# JIRA Data for {quarter_name}",
                        "Execute: mcp__atlassian__searchJiraIssuesUsingJql(cloudId='credify.atlassian.net', jql='project = \\\"{team_prefix}\\\" AND created >= \\\"{start_date}\\\" AND created <= \\\"{end_date}\\\" ORDER BY created DESC', fields=['summary', 'description', 'status', 'issuetype', 'priority', 'created', 'assignee', 'components'], maxResults=250)",
                        "",
                        "# GitHub Data for {quarter_name}",
                        "Execute: gh search repos 'org:credify topic:{team_prefix_lower} OR {team_prefix_lower} in:name' --json name,url,defaultBranch",
                        "# For each repository, collect commit data:",
                        "Execute: gh api 'search/commits?q=author-date:{start_date}..{end_date}+org:credify+repo:REPO_NAME' --paginate",
                        "# Alternative if repo-specific search fails:",
                        "Execute: gh api 'repos/credify/REPO_NAME/commits?since={start_date}T00:00:00Z&until={end_date}T23:59:59Z' --paginate",
                        "",
                        "# Team Member Identification for {quarter_name}",
                        "# Extract unique GitHub commit authors and JIRA assignees for team size tracking",
                        "# Build anonymized contributor mapping while preserving privacy",
                        ""
                    ],
                    
                    "analysis_requirements": [
                        "**Multi-Quarter Team Size Analysis:**",
                        "- Track unique contributors per quarter (GitHub authors + JIRA assignees)",
                        "- Calculate quarter-over-quarter team size changes",
                        "- Identify new contributors joining and departing each quarter",
                        "- Calculate contributor retention rates across quarters",
                        "- Analyze team stability patterns and turnover impact",
                        "",
                        "**Performance Trend Analysis:**", 
                        "- Track total tickets completed per quarter",
                        "- Monitor total commits and repository activity trends",
                        "- Calculate tickets-per-contributor and commits-per-contributor ratios",
                        "- Generate weighted velocity scores combining tickets and commits",
                        "- Identify performance pattern changes and trend directions",
                        "",
                        "**Quarter-over-Quarter Comparisons:**",
                        "- Linear trend analysis for key metrics (increasing/decreasing/stable)",
                        "- Percentage change calculations between first and last quarters",
                        "- Statistical significance assessment (high/medium/low impact)",
                        "- Cross-validation between JIRA activity and GitHub contributions",
                        "",
                        "**Technical Focus Evolution:**",
                        "- Track changes in technical focus areas across quarters",
                        "- Analyze component/label distribution evolution in JIRA tickets",
                        "- Monitor repository activity patterns and technology adoption",
                        "- Identify shifts in development priorities and team expertise",
                        "",
                        "**Team Collaboration Patterns:**",
                        "- Cross-repository collaboration trends",
                        "- Team knowledge sharing and cross-functional work evolution",
                        "- Contributor overlap between different technical areas",
                        "- Team maturity indicators from workflow and process improvements"
                    ],
                    
                    "required_output_format": f"""
# Quarter-over-Quarter Analysis: {team_prefix} Team ({start_year}-{end_year})

⚠️ **ALPHA DEVELOPMENT STAGE - NOT FOR PUBLIC USE** ⚠️

> **Development Notice**: This report is generated by MCP-Tools in alpha stage development.
> - **Accuracy**: Data interpretation should be manually validated
> - **Completeness**: Report accuracy and completeness are not guaranteed
> - **Intended Use**: Development testing and internal feedback only
> - **Not Suitable For**: Official reporting, performance reviews, or team evaluations  
> - **Status**: Active development - format and content may change without notice

## Executive Summary
*Analysis period: {start_year} to {end_year} ({len(quarters)} quarters)*
*⚠️ Alpha development version - manual validation required*

{{executive_summary_with_key_findings_and_recommendations}}

## Key Findings

### Team Size Evolution
- **Team Size Change**: {{start_size}} → {{end_size}} contributors ({{size_change_percentage:+.0f}}%)
- **Average Retention Rate**: {{avg_retention_rate:.1f}}%
- **Total New Contributors**: {{total_new_contributors}}
- **Total Departures**: {{total_departures}}

### Performance Trends Overview
{{performance_trends_summary_with_direction_indicators}}

## Detailed Quarter-by-Quarter Analysis

### Team Composition Changes
| Quarter | Team Size | New Contributors | Departed | Retention Rate |
|---------|-----------|------------------|----------|----------------|
{{team_size_metrics_table}}

### Performance Metrics Progression  
| Quarter | Total Tickets | Total Commits | Tickets/Contributor | Commits/Contributor | Velocity Score |
|---------|---------------|---------------|---------------------|---------------------|----------------|
{{performance_metrics_table}}

## Trend Analysis

{{trend_analysis_for_each_key_metric}}

### Total Tickets Trend
- **Direction**: {{tickets_trend_direction}} ({{tickets_change_percentage:+.1f}}% change)
- **Significance**: {{tickets_trend_significance}}
- **Data Points**: {{tickets_quarterly_data}}

### Team Velocity Trend
- **Direction**: {{velocity_trend_direction}} ({{velocity_change_percentage:+.1f}}% change)
- **Significance**: {{velocity_trend_significance}}
- **Analysis**: {{velocity_trend_interpretation}}

### Team Size Trend
- **Direction**: {{team_size_trend_direction}} ({{team_size_change_percentage:+.1f}}% change)
- **Stability Assessment**: {{team_stability_assessment}}

## Strategic Insights

### Team Stability Assessment
{{team_stability_analysis_based_on_retention_rates}}

### Velocity and Productivity Patterns
{{velocity_analysis_with_contributing_factors}}

### Technical Focus Evolution
{{technical_focus_changes_across_quarters}}

## Recommendations

### Continue Leveraging
{{areas_of_strength_to_maintain}}

### Areas for Improvement  
{{improvement_opportunities_with_specific_actions}}

### Next Quarter Priorities
1. **{{priority_1}}**: {{rationale_and_approach}}
2. **{{priority_2}}**: {{rationale_and_approach}} 
3. **{{priority_3}}**: {{rationale_and_approach}}

## Comparative Analysis Summary

**Analysis Period**: {start_year} to {end_year} ({len(quarters)} quarters)
**Team**: {team_prefix} project team
**Analysis Focus**: Team composition changes, productivity trends, and velocity patterns

### Key Metrics Summary
- **Team Size Range**: {{min_contributors}} - {{max_contributors}} contributors
- **Overall Retention**: {{overall_retention_rate:.1f}}%
- **Total Tickets Processed**: {{total_tickets_all_quarters}} tickets
- **Total Commits**: {{total_commits_all_quarters}} commits
- **Velocity Trend**: {{overall_velocity_trend}} with {{velocity_significance}} significance

## Data Sources and Methodology

### Data Collection Period
- **Start Date**: {quarters[0]['start_date']}
- **End Date**: {quarters[-1]['end_date']}
- **Quarters Analyzed**: {len(quarters)}

### Data Sources
- **JIRA Analysis**: Project {team_prefix} ticket completion and workflow data across all quarters
- **GitHub Analysis**: Commit patterns, repository activity, and contributor identification
- **Team Metrics**: Contributor tracking with join/departure analysis and retention calculations

### Methodology Notes
- **Team Size**: Based on unique GitHub commit authors + JIRA assignees per quarter
- **Velocity Calculation**: Weighted combination of (tickets/contributor * 2) + (commits/contributor * 0.5)
- **Trend Analysis**: Linear progression analysis with statistical significance assessment
- **Retention Rate**: Quarter-over-quarter contributor overlap percentage
- **Anonymization**: Individual contributors aggregated for privacy compliance

### Quality Assurance
- **Cross-Source Validation**: JIRA tickets cross-referenced with GitHub commit messages
- **Bot Filtering**: Automated commits and bot PRs excluded from contributor counts
- **Data Consistency**: Multiple quarters analyzed with consistent methodology
- **Trend Validation**: Statistical significance testing for all trend calculations

---

### ⚠️ Alpha Development Disclaimer

**This report was generated by MCP-Tools in alpha development stage:**
- **Not for official use**: Manual validation of all data and conclusions required
- **Development status**: Features and accuracy are not production-ready
- **Data limitations**: Report may contain incomplete or inaccurate analysis
- **Internal use only**: Not suitable for external reporting or team evaluations

*Generated using MCP Tools Quarter-over-Quarter Analysis (Alpha Development Version) with multi-quarter trend tracking*
""",
                },
                
                "external_context": context_content,
                
                "success_criteria": {
                    "multi_quarter_data_collection": "JIRA tickets and GitHub commits successfully retrieved for all quarters in the specified period",
                    "team_size_tracking": "Team composition changes and contributor retention rates calculated accurately across quarters", 
                    "trend_analysis": "Performance trends and velocity patterns identified with statistical significance",
                    "comparative_metrics": "Quarter-over-quarter comparisons generated with meaningful insights",
                    "strategic_recommendations": "Actionable insights and recommendations based on multi-quarter data patterns",
                    "report_generation": "Comprehensive markdown report with all required sections and data transparency"
                },
                
                "troubleshooting": {
                    "insufficient_quarters": "Verify period spans at least 2 quarters for meaningful trend analysis",
                    "data_gaps": "Some quarters may have limited activity - focus analysis on quarters with sufficient data",
                    "team_identification": "Cross-reference JIRA assignees with GitHub authors for accurate team size tracking",
                    "trend_calculation": "Ensure consistent data collection methodology across all quarters for valid comparisons",
                    "retention_analysis": "Handle contributor name variations and email changes for accurate retention calculations"
                }
            }
            
            logger.info(f"Quarter-over-quarter analysis instructions generated for: {team_prefix} {period}")
            return qoq_instructions
            
        except Exception as e:
            logger.error(f"Error generating quarter-over-quarter analysis instructions: {str(e)}")
            return ToolBase.create_error_response(
                f"Failed to generate quarter-over-quarter analysis instructions: {str(e)}",
                error_type=type(e).__name__
            )


def get_context_fallback(context_type: str) -> str:
    """Get fallback context content for quarter-over-quarter analysis"""
    
    if context_type == "quarter_over_quarter":
        return """# Quarter-over-Quarter Team Performance Analysis Guidelines

## Multi-Quarter Analysis Strategy
- **Period Planning**: Minimum 2 quarters required for meaningful trend analysis
- **Team Size Tracking**: Monitor contributor changes, retention rates, and team growth patterns
- **Performance Metrics**: Track velocity changes, productivity patterns, and comparative analysis
- **Trend Analysis**: Statistical analysis with significance testing and direction indicators

## Key Metrics Framework
- **Team Composition**: Unique contributors, new joiners, departures, retention rates
- **Productivity Trends**: Quarter-to-quarter changes in tickets and commits per contributor
- **Velocity Scoring**: Weighted combination of ticket completion and code contribution metrics
- **Technical Focus**: Evolution of development areas and technology adoption patterns
- **Collaboration Patterns**: Cross-functional work and team knowledge sharing trends

## Trend Analysis Methods
- **Linear Progression**: Calculate percentage changes and trend directions (increasing/decreasing/stable)
- **Statistical Significance**: Assess impact levels (high/medium/low) for trend reliability
- **Comparative Analysis**: Quarter-over-quarter performance with contextual interpretation
- **Retention Analysis**: Team stability patterns and contributor continuity assessment

## Report Structure
1. **Executive Summary**: Multi-quarter overview with strategic findings
2. **Team Size Evolution**: Contributor tracking with retention and growth analysis
3. **Performance Metrics**: Quarter-by-quarter progression with trend indicators
4. **Strategic Insights**: Team stability, velocity patterns, and technical evolution
5. **Recommendations**: Data-driven suggestions for team optimization and growth
6. **Methodology**: Complete data collection and analysis transparency

## Privacy and Team Analytics
- **Aggregate Metrics**: Team-level analysis with individual contributor anonymization
- **Retention Focus**: Team stability assessment without individual performance evaluation
- **Trend Emphasis**: Focus on team patterns rather than individual contribution tracking
- **Strategic Value**: Insights for team development, resource planning, and process improvement

## Quality Validation
- **Multi-Source Cross-Validation**: JIRA activity correlated with GitHub contributions
- **Consistent Methodology**: Uniform data collection and analysis across all quarters
- **Trend Significance Testing**: Statistical validation of performance pattern changes
- **Team Boundary Accuracy**: Proper contributor attribution and team membership verification"""
    
    return ""