#!/usr/bin/env python3
"""
Personal Performance Analysis Tools with 3-Subagent Coordination

PREREQUISITES: Run `setup_prerequisites` tool to validate all required tools and services.
This tool depends on GitHub CLI, Atlassian MCP, JIRA access, Git configuration, and command-line utilities.

Generate enhanced personal performance analysis using a 3-subagent coordination system:
- Subagent 1: JIRA Analysis & PR Discovery
- Subagent 2: GitHub PR Metrics Collection 
- Subagent 3: Report Generation & Analysis

Returns INSTRUCTIONS for Claude Code to execute coordinated analysis with improved
JIRA→GitHub PR bridging and enhanced personal performance metrics.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

from fastmcp import FastMCP
from .base import ToolBase, get_context_fallback

logger = logging.getLogger(__name__)


class PersonalPerformanceCoordinator:
    """3-Subagent coordination system for enhanced personal performance analysis"""
    
    @staticmethod
    def generate_subagent_1_instructions(team_prefix: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Generate instructions for Subagent 1: JIRA Analysis & PR Discovery"""
        return {
            "subagent": "1_jira_analysis_pr_discovery",
            "purpose": "Process JIRA tickets to extract PR links and analyze personal assignments",
            "execution_steps": [
                "## User Identity Verification",
                "Execute: git config --global user.name",
                "Execute: git config --global user.email", 
                "Execute: gh api user --jq '.login'",
                "Execute: mcp__atlassian__lookupJiraAccountId(cloudId='credify.atlassian.net', searchString='{user_email}')",
                "",
                "## Personal JIRA Ticket Collection",
                f"Execute: mcp__atlassian__searchJiraIssuesUsingJql(cloudId='credify.atlassian.net', jql='project = \"{team_prefix}\" AND assignee = \"{{user_account_id}}\" AND created >= \"{start_date}\" AND created <= \"{end_date}\" ORDER BY created DESC', fields=['summary', 'description', 'status', 'issuetype', 'priority', 'created', 'assignee', 'components', 'timeoriginalestimate', 'timespent', 'comment'], maxResults=250)",
                "",
                "## PR Link Extraction from JIRA",
                "# Parse ticket descriptions and comments for GitHub PR URLs",
                "# Extract patterns: 'PR: https://github.com/...', 'Resolves #123', '/pull/' URLs",
                "# Build JIRA ticket → GitHub PR mapping for accurate attribution",
                "# Store extracted PR URLs for Subagent 2 processing",
                "",
                "## Personal Assignment Analysis",
                "# Analyze ticket assignment patterns and completion rates",
                "# Track personal time estimation vs actual completion",
                "# Identify technical focus areas from components and descriptions",
                "# Generate personal JIRA metrics summary"
            ],
            "output_format": {
                "personal_jira_metrics": "Total tickets, completion rate, time accuracy",
                "extracted_pr_links": "List of GitHub PR URLs found in JIRA tickets",
                "jira_pr_mapping": "Dictionary mapping JIRA ticket IDs to PR URLs",
                "technical_focus_areas": "Primary areas of work from ticket analysis"
            }
        }
    
    @staticmethod
    def generate_subagent_2_instructions(team_prefix: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Generate instructions for Subagent 2: GitHub PR Metrics Collection"""
        return {
            "subagent": "2_github_pr_metrics",
            "purpose": "Collect detailed GitHub PR and commit data using discovered PR links",
            "execution_steps": [
                "## Use PR Links from Subagent 1",
                "# Process PR URLs discovered by Subagent 1 from JIRA tickets",
                "# For each discovered PR URL, extract detailed metrics",
                "",
                "## Enhanced PR Data Collection", 
                "# For each PR URL from Subagent 1:",
                "Execute: gh pr view {pr_url} --json number,title,state,createdAt,mergedAt,additions,deletions,commits,changedFiles,reviewDecision",
                "Execute: gh pr diff {pr_url} --name-only | wc -l  # Files changed count",
                "Execute: gh pr view {pr_url} --json comments --jq '.comments | length'  # Comment count",
                "",
                "## Personal Commit Analysis",
                f"Execute: gh api 'search/commits?q=author:{{github_username}}+author-date:{start_date}..{end_date}+org:credify' --paginate",
                "# Cross-reference commits with PR URLs from Subagent 1",
                "# Identify commits that are part of JIRA-linked PRs vs standalone work",
                "",
                "## Repository Contribution Mapping",
                "Execute: gh search repos 'org:credify' --json name,fullName | head -20",
                "# For key repositories, get personal contribution stats",
                f"Execute: gh api 'repos/credify/{{repo_name}}/stats/contributors' | jq '.[] | select(.author.login == \"{{github_username}}\")'",
                "",
                "## PR→JIRA Cross-Reference",
                "# Use Subagent 1's JIRA→PR mapping to enhance GitHub metrics",
                "# Calculate PR completion rates vs JIRA ticket completion",
                "# Identify work attribution gaps between JIRA and GitHub"
            ],
            "output_format": {
                "enhanced_pr_metrics": "Detailed PR statistics with JIRA attribution",
                "personal_commit_stats": "Commit frequency, lines changed, repository diversity",
                "cross_reference_analysis": "JIRA work vs GitHub contributions alignment",
                "contribution_quality_metrics": "PR size, review feedback, merge success rates"
            }
        }
    
    @staticmethod
    def generate_subagent_3_instructions(team_prefix: str, quarter_name: str) -> Dict[str, Any]:
        """Generate instructions for Subagent 3: Report Generation & Analysis"""
        return {
            "subagent": "3_report_generation", 
            "purpose": "Synthesize all data into comprehensive personal performance report",
            "execution_steps": [
                "## Data Synthesis",
                "# Combine Subagent 1 JIRA analysis with Subagent 2 GitHub metrics",
                "# Cross-reference JIRA ticket completion with actual merged PRs",
                "# Calculate accurate personal contribution attribution",
                "",
                "## Enhanced Performance Metrics",
                "# Personal productivity: JIRA tickets + GitHub PRs with proper attribution",
                "# Code quality indicators: PR review feedback, merge success rates",
                "# Technical growth: Complexity evolution in both JIRA and GitHub data",
                "# Learning velocity: New technologies/frameworks from commit analysis",
                "",
                "## Gap Analysis",
                "# Identify JIRA tickets without corresponding GitHub PRs (process work)",
                "# Identify GitHub PRs without corresponding JIRA tickets (maintenance)",
                "# Calculate work attribution accuracy and identify improvement areas",
                "",
                "## Personal Development Insights",
                "# Generate growth recommendations based on combined dataset",
                "# Identify strength areas from consistent high performance patterns",
                "# Suggest learning opportunities based on contribution gaps",
                "# Create actionable development plan for next quarter"
            ],
            "output_format": {
                "comprehensive_report": f"Full personal performance report for {quarter_name}",
                "attribution_analysis": "JIRA vs GitHub work attribution accuracy",
                "development_recommendations": "Personalized growth and learning suggestions",
                "next_quarter_goals": "Data-driven objectives for continued development"
            }
        }


def register_personal_performance_tools(mcp: FastMCP):
    """Register personal performance analysis tools with the FastMCP server"""
    
    @mcp.tool
    def personal_quarterly_report(
        team_prefix: str,
        year: int,
        quarter: int,
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Generate personal performance report for a single quarter - INSTRUCTIONS ONLY.

        **Natural Language Triggers:**
        - "personal performance report Q[#] [year]"
        - "my quarterly report [team] Q[#] [year]"
        - "individual performance analysis Q[#] [year]"
        - "personal contribution report SI Q2 2025"
        - "my development report for Q3 2024"
        - "generate personal quarterly performance [team] [quarter] [year]"
        - "how did I perform this quarter?"
        - "personal growth analysis [quarter]"

        **What this tool does:**
        Returns comprehensive instructions for analyzing your personal contributions, productivity 
        patterns, and technical focus areas for a specific quarter. Includes personal development 
        guidance and growth recommendations. Uses real JIRA MCP and GitHub CLI commands - does NOT 
        execute analysis directly.

        **Perfect for:** Personal performance reviews, self-assessment, career development planning,
        skill development tracking, productivity analysis, quarterly self-reflection, goal setting,
        individual growth monitoring, professional development planning.

        Analyzes your individual contributions, productivity patterns, and technical focus
        areas for the specified quarter with personal insights and development guidance
        by returning detailed instructions for Claude Code execution.

        Args:
            team_prefix: Team/project prefix (e.g., "SI", "PLAT", "CORE")
            year: Year for the quarter (e.g., 2025)
            quarter: Quarter number (1-4)
            description: Optional description of analysis focus
            
        Returns:
            Dictionary containing detailed processing instructions for Claude Code execution
        """
        logger.info(f"Personal quarterly report requested: {team_prefix} Q{quarter} {year}")
        
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
            quarter_starts = {1: (1, 1), 2: (4, 1), 3: (7, 1), 4: (10, 1)}
            quarter_ends = {1: (3, 31), 2: (6, 30), 3: (9, 30), 4: (12, 31)}
            
            start_month, start_day = quarter_starts[quarter]
            end_month, end_day = quarter_ends[quarter]
            
            start_date = f"{year}-{start_month:02d}-{start_day:02d}"
            end_date = f"{year}-{end_month:02d}-{end_day:02d}"
            quarter_name = f"Q{quarter} {year}"
            
            # Load external context
            context_content = ToolBase.load_external_context(
                "/Users/dlighty/code/llm-context/PERSONAL-PERFORMANCE-CONTEXT.md",
                get_context_fallback("personal_performance")
            )
            
            # Return detailed analysis instructions
            personal_instructions = {
                "tool_name": "personal_quarterly_report",
                "analysis_context": f"Personal Quarterly Performance Report - {quarter_name}",
                "timestamp": ToolBase.create_success_response({})["timestamp"],
                "team_prefix": team_prefix,
                "year": year,
                "quarter": quarter,
                "quarter_name": quarter_name,
                "start_date": start_date,
                "end_date": end_date,
                "description": description,
                
                "processing_instructions": {
                    "overview": f"Generate enhanced personal quarterly performance report for {quarter_name} using 3-subagent coordination system. Focus: {description or 'comprehensive personal performance analysis with JIRA→GitHub PR bridging'}.",
                    
                    "prerequisite_validation": [
                        "Verify GitHub CLI authentication: `gh auth status`",
                        "Verify Atlassian MCP server connection and cloud ID access",
                        "Get current user identity from git config: `git config --global user.name` and `git config --global user.email`",
                        "Ensure `jq` is available for JSON processing",
                        "Prepare for 3-subagent parallel execution coordination"
                    ],
                    
                    "subagent_coordination": {
                        "execution_strategy": "Execute all 3 subagents in parallel for maximum efficiency",
                        "subagent_1": PersonalPerformanceCoordinator.generate_subagent_1_instructions(team_prefix, start_date, end_date),
                        "subagent_2": PersonalPerformanceCoordinator.generate_subagent_2_instructions(team_prefix, start_date, end_date), 
                        "subagent_3": PersonalPerformanceCoordinator.generate_subagent_3_instructions(team_prefix, quarter_name),
                        "coordination_notes": [
                            "Subagent 1 runs first to discover JIRA→PR mappings",
                            "Subagent 2 uses Subagent 1's PR links for enhanced GitHub analysis",
                            "Subagent 3 synthesizes both datasets for comprehensive report",
                            "All subagents work independently on their domain expertise",
                            "Data handoff via structured interim results"
                        ]
                    },
                    
                    "enhanced_jira_github_bridging": [
                        "## JIRA→GitHub PR Link Extraction (Subagent 1)",
                        "# Parse JIRA ticket descriptions for GitHub PR URLs",
                        "# Search patterns: 'PR: https://github.com/', 'Resolves #123', '/pull/' URLs",
                        "# Extract PR numbers from ticket comments and descriptions", 
                        "# Build accurate mapping between JIRA work and GitHub code contributions",
                        "# Cross-reference JIRA ticket completion with actual merged PRs",
                        "",
                        "## Enhanced GitHub Analysis (Subagent 2)",
                        "# Use discovered PR URLs for detailed metrics collection",
                        "# Collect PR review feedback, merge success rates, change complexity",
                        "# Analyze commit patterns within JIRA-linked PRs vs standalone work",
                        "# Calculate repository diversity and contribution patterns",
                        "",
                        "## Cross-Reference Analysis (Subagent 3)", 
                        "# Validate JIRA ticket completion against actual merged PRs",
                        "# Identify work attribution gaps and process improvements",
                        "# Generate accurate personal contribution metrics",
                        "# Produce actionable insights for personal development"
                    ],
                    
                    "enhanced_analysis_requirements": [
                        "**Enhanced Personal JIRA Analysis (Subagent 1):**",
                        "- Total tickets assigned and completed personally with PR link discovery",
                        "- Personal issue type distribution and technical focus areas",
                        "- Time estimation accuracy (estimated vs actual completion)",
                        "- PR link extraction from descriptions and comments for attribution",
                        "- Cross-reference ticket completion with actual code delivery",
                        "",
                        "**Enhanced Personal GitHub Analysis (Subagent 2):**", 
                        "- Detailed PR metrics using JIRA-discovered links",
                        "- Personal code contribution quality (review feedback, merge rates)", 
                        "- Repository diversity and contribution complexity evolution",
                        "- Commit patterns within JIRA-linked PRs vs standalone development",
                        "- Technical growth indicators from code change analysis",
                        "",
                        "**Cross-Reference Attribution Analysis (Subagent 3):**",
                        "- JIRA ticket completion vs GitHub PR delivery alignment",
                        "- Work attribution accuracy and process improvement opportunities",
                        "- Personal productivity metrics with enhanced accuracy",
                        "- Learning velocity based on technical complexity progression",
                        "",
                        "**Personal Development Insights (Subagent 3):**",
                        "- Strength areas from consistent high-performance patterns",
                        "- Growth opportunities identified from contribution gap analysis", 
                        "- Technical skill development trajectory with evidence",
                        "- Personalized learning recommendations based on data patterns"
                    ],
                    
                    "enhanced_output_format": f"""
# Enhanced Personal Performance Report - {quarter_name}
*Generated using 3-Subagent Coordination System with JIRA→GitHub PR Bridging*

## Personal Summary
*Report generated on {{timestamp}} for personal contributions during {quarter_name} ({{start_date}} to {{end_date}})*

{{personal_summary_paragraph_with_key_achievements}}

## Personal JIRA Contributions

### Personal Issue Metrics
- **Total Issues Assigned**: {{total_personal_tickets}}
- **Issues Completed**: {{completed_personal_tickets}}
- **Completion Rate**: {{completion_percentage}}%

### Personal Issue Type Focus
- **Stories**: {{personal_story_count}} ({{story_percentage}}%)
- **Bugs**: {{personal_bug_count}} ({{bug_percentage}}%)
- **Tasks**: {{personal_task_count}} ({{task_percentage}}%)
- **Epics**: {{personal_epic_count}} ({{epic_percentage}}%)

### Personal Time Management
- **Average Resolution Time**: {{avg_personal_resolution_days}} days
- **Time Estimation Accuracy**: {{estimation_accuracy_percentage}}%
- **Time Spent vs Estimated**: {{actual_vs_estimated_ratio}}

## Personal GitHub Activity

### Personal Development Activity
- **Total Personal Commits**: {{personal_commits}}
- **Active Repositories**: {{personal_active_repos}}
- **Lines Changed**: +{{personal_lines_added}} / -{{personal_lines_deleted}}

### Personal Pull Request Metrics
- **PRs Created**: {{personal_prs_created}}
- **PRs Merged**: {{personal_prs_merged}}
- **Average PR Size**: {{avg_pr_size}} lines changed
- **PR Merge Rate**: {{pr_merge_rate}}%

## Personal Technical Contributions

Based on personal JIRA tickets and GitHub commits:

### Primary Focus Areas
1. **{{personal_focus_area_1}}**: {{personal_contribution_description}}
2. **{{personal_focus_area_2}}**: {{personal_contribution_description}}
3. **{{personal_focus_area_3}}**: {{personal_contribution_description}}

### Technical Skill Development
- **New Technologies/Frameworks**: {{new_tech_learned}}
- **Code Quality Improvements**: {{quality_improvements}}
- **Architecture Contributions**: {{architecture_work}}

## Personal Productivity Assessment

### Personal Velocity Metrics
- **Personal Tickets per Week**: {{tickets_per_week}}
- **Personal Commits per Week**: {{commits_per_week}}
- **Personal Productivity Score**: {{personal_productivity_calculation}} (weighted metric)

### Work Distribution
- **Feature Development**: {{personal_feature_percentage}}%
- **Bug Resolution**: {{personal_bug_percentage}}%
- **Technical Debt**: {{personal_tech_debt_percentage}}%
- **Documentation/Testing**: {{personal_docs_testing_percentage}}%

## Personal Growth Analysis

### Quarter Achievements
- {{personal_achievement_1}}
- {{personal_achievement_2}}
- {{personal_achievement_3}}

### Skills Developed
- {{skill_development_1}}
- {{skill_development_2}}

### Learning Opportunities Identified
- {{learning_opportunity_1}}
- {{learning_opportunity_2}}

## Personal Development Recommendations

### Strength Areas
- {{strength_area_1}}: Continue leveraging expertise in this area
- {{strength_area_2}}: Consider mentoring others in this domain

### Growth Opportunities
- {{growth_area_1}}: Suggested learning path and resources
- {{growth_area_2}}: Potential projects or collaborations

### Next Quarter Focus Suggestions
1. **{{next_quarter_focus_1}}**: {{rationale_and_approach}}
2. **{{next_quarter_focus_2}}**: {{rationale_and_approach}}
3. **{{next_quarter_focus_3}}**: {{rationale_and_approach}}

## Methodology and Data Privacy

### Data Collection Period
- **Start Date**: {start_date}
- **End Date**: {end_date}
- **Quarter**: {quarter_name}

### Personal Data Sources
- **JIRA**: Personal ticket assignments and completion data
- **GitHub**: Personal commit and PR history  
- **User Identity**: Git config and GitHub authentication

### Privacy Notes
- **Individual Focus**: This report contains only your personal contributions
- **No Comparative Data**: No team member comparisons or rankings included
- **Self-Assessment Purpose**: Designed for personal development planning
- **Data Retention**: Personal analysis data not stored beyond report generation

### Methodology
- **Personal Attribution**: All metrics filtered by personal user identifiers
- **Productivity Calculation**: Based on personal completion rates and contribution patterns
- **Growth Analysis**: Derived from complexity and scope evolution in personal contributions
- **Recommendation Generation**: Based on personal patterns and industry best practices

---

### ⚠️ Alpha Development Disclaimer

**This report was generated by MCP-Tools in alpha development stage:**
- **Not for official use**: Manual validation of all data and conclusions required
- **Development status**: Features and accuracy are not production-ready
- **Data limitations**: Report may contain incomplete or inaccurate analysis
- **Internal use only**: Not suitable for external reporting or personal evaluations

*Generated using MCP Tools Personal Performance Analysis (Alpha Development Version) with privacy-focused data collection*
""",
                },
                
                "external_context": context_content,
                
                "enhanced_success_criteria": {
                    "subagent_coordination": "All 3 subagents executed successfully with proper data handoff",
                    "jira_pr_bridging": "PR links successfully extracted from JIRA tickets with high attribution accuracy",
                    "github_enhancement": "GitHub metrics collected using JIRA-discovered PR links for improved accuracy", 
                    "cross_reference_analysis": "JIRA work completion validated against GitHub PR delivery",
                    "personal_insights": "Enhanced personal development insights generated from coordinated analysis",
                    "attribution_accuracy": "Work attribution accuracy >= 85% between JIRA and GitHub data",
                    "privacy_compliance": "Only personal data analyzed, no team member comparisons"
                },
                
                "enhanced_troubleshooting": {
                    "subagent_coordination_issues": "Verify all 3 subagents can execute in parallel without conflicts",
                    "jira_pr_extraction_issues": "Check JIRA ticket descriptions and comments contain GitHub PR URLs",
                    "github_pr_access_issues": "Verify GitHub CLI can access discovered PR URLs from JIRA",
                    "attribution_accuracy_low": "Review JIRA ticket PR linking practices and suggest improvements",
                    "cross_reference_failures": "Validate JIRA ticket completion dates align with PR merge dates",
                    "empty_personal_data": "Verify user has JIRA assignments and GitHub contributions in specified period",
                    "rate_limit_coordination": "Implement proper rate limiting across all 3 subagents"
                }
            }
            
            logger.info(f"Enhanced personal quarterly report with 3-subagent coordination generated for: {quarter_name}")
            return personal_instructions
            
        except Exception as e:
            logger.error(f"Error generating enhanced personal quarterly report instructions: {str(e)}")
            return ToolBase.create_error_response(
                f"Failed to generate enhanced personal quarterly report instructions: {str(e)}",
                error_type=type(e).__name__
            )

    @mcp.tool
    def personal_quarter_over_quarter(
        team_prefix: str,
        period: str,
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Generate personal quarter-over-quarter performance analysis - INSTRUCTIONS ONLY.

        **Natural Language Triggers:**
        - "personal quarter over quarter analysis [period]"
        - "my performance trends [team] [period]"
        - "personal growth analysis over multiple quarters"
        - "track my development [team] [year] vs [year]"
        - "personal QoQ analysis [period]"
        - "how have I improved over [period]?"
        - "my productivity trends across quarters"
        - "personal skill development timeline [period]"

        **What this tool does:**
        Returns comprehensive instructions for tracking your individual performance trends,
        growth patterns, and skill development across multiple quarters. Includes personalized
        insights and development recommendations based on your historical contribution patterns.
        Uses real JIRA MCP and GitHub CLI commands - does NOT execute analysis directly.

        **Perfect for:** Personal development tracking, career growth analysis, skill progression
        monitoring, long-term goal assessment, learning velocity analysis, professional development
        planning, performance trend identification, personal productivity optimization.

        Tracks your individual performance trends, growth patterns, and skill development
        across multiple quarters with personalized insights and recommendations by
        returning detailed instructions for Claude Code execution.

        Args:
            team_prefix: Team/project prefix (e.g., "SI", "PLAT", "CORE") 
            period: Analysis period like "2024" or "2023-2025"
            description: Optional description of analysis focus
            
        Returns:
            Dictionary containing detailed processing instructions for Claude Code execution
        """
        logger.info(f"Personal quarter-over-quarter analysis requested: {team_prefix} {period}")
        
        try:
            # Validate inputs
            if not team_prefix or not team_prefix.isalpha():
                return ToolBase.create_error_response(
                    "Invalid team_prefix. Must be alphabetic (e.g., 'SI', 'PLAT')",
                    error_type="validation_error"
                )
            
            # Parse period input
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
                    quarters.append(f"Q{q} {year}")
            
            if len(quarters) < 2:
                return ToolBase.create_error_response(
                    "Analysis requires at least 2 quarters. Extend period or use personal_quarterly_report for single quarters.",
                    error_type="validation_error"
                )
            
            # Load external context
            context_content = ToolBase.load_external_context(
                "/Users/dlighty/code/llm-context/PERSONAL-QOQ-CONTEXT.md",
                get_context_fallback("personal_quarter_over_quarter")
            )
            
            # Return detailed analysis instructions
            qoq_instructions = {
                "tool_name": "personal_quarter_over_quarter",
                "analysis_context": f"Personal Quarter-over-Quarter Analysis - {period}",
                "timestamp": ToolBase.create_success_response({})["timestamp"],
                "team_prefix": team_prefix,
                "period": period,
                "start_year": start_year,
                "end_year": end_year,
                "quarters": quarters,
                "description": description,
                
                "processing_instructions": {
                    "overview": f"Generate personal quarter-over-quarter performance analysis for {period}. Focus: {description or 'personal growth tracking and performance trend analysis'}.",
                    
                    "prerequisite_validation": [
                        "Verify GitHub CLI authentication: `gh auth status`",
                        "Verify Atlassian MCP server connection and cloud ID access",
                        "Get current user identity: `git config --global user.name` and `git config --global user.email`",
                        "Ensure `jq` is available for JSON processing"
                    ],
                    
                    "multi_quarter_data_collection": [
                        "## Personal Identity Setup",
                        "Execute: git config --global user.name",
                        "Execute: git config --global user.email", 
                        "Execute: gh api user --jq '.login'",
                        "Execute: mcp__atlassian__lookupJiraAccountId(cloudId='credify.atlassian.net', searchString='{{user_email}}')",
                        "",
                        "## Quarter-by-Quarter Data Collection",
                        "For each quarter in the analysis period:",
                        "### Quarter Data Collection Loop",
                    ],
                    
                    "quarter_data_collection_template": [
                        "## {quarter} Data Collection",
                        "# JIRA data for {quarter}",
                        "Execute: mcp__atlassian__searchJiraIssuesUsingJql(...) # with appropriate date ranges for {quarter}",
                        "# GitHub data for {quarter}",
                        "Execute: gh api 'search/commits?q=author:{{github_username}}+author-date:{{quarter_start}}..{{quarter_end}}+org:credify'",
                        "# Pull request data for {quarter}",
                        "Execute: gh search prs 'org:credify author:{{github_username}} created:{{quarter_start}}..{{quarter_end}}'",
                        ""
                    ],
                    
                    "trend_analysis_requirements": [
                        "**Personal Productivity Trends:**",
                        "- Track tickets completed per quarter over time",
                        "- Monitor personal commit frequency trends",
                        "- Analyze code contribution volume changes",
                        "- Identify productivity pattern changes",
                        "",
                        "**Personal Skill Development Tracking:**",
                        "- Track complexity evolution of assigned tickets",
                        "- Monitor expansion into new technical areas",
                        "- Analyze learning curve indicators",
                        "- Identify mastery development patterns",
                        "",
                        "**Personal Growth Indicators:**",
                        "- Leadership and mentorship activity growth",
                        "- Cross-team collaboration expansion",
                        "- Technical architecture contribution evolution",
                        "- Documentation and knowledge sharing trends",
                        "",
                        "**Personal Performance Consistency:**",
                        "- Quarter-to-quarter velocity stability",
                        "- Quality metrics consistency (PR reviews, bug rates)",
                        "- Time management improvement patterns",
                        "- Work-life balance indicators from commit patterns"
                    ],
                    
                    "required_output_format": f"""
# Personal Quarter-over-Quarter Analysis - {period}

⚠️ **ALPHA DEVELOPMENT STAGE - NOT FOR PUBLIC USE** ⚠️

> **Development Notice**: This report is generated by MCP-Tools in alpha stage development.
> - **Accuracy**: Data interpretation should be manually validated
> - **Completeness**: Report accuracy and completeness are not guaranteed  
> - **Intended Use**: Development testing and internal feedback only
> - **Not Suitable For**: Official reporting, performance reviews, or personal evaluations
> - **Status**: Active development - format and content may change without notice

## Personal Growth Executive Summary
*Analysis period: {start_year} to {end_year} ({len(quarters)} quarters)*
*⚠️ Alpha development version - manual validation required*

{{personal_growth_summary_with_key_achievements}}

## Personal Performance Trend Analysis

### Productivity Evolution
| Quarter | Tickets Completed | Commits | Lines Changed | Velocity Score |
|---------|-------------------|---------|---------------|----------------|
{{quarter_by_quarter_personal_metrics_table}}

### Personal Growth Trajectory
- **Productivity Trend**: {{productivity_direction}} ({{productivity_change_percentage}}% change)
- **Technical Scope**: {{technical_scope_expansion}}
- **Leadership Growth**: {{leadership_indicators}}
- **Learning Velocity**: {{learning_acceleration_metrics}}

## Personal Skill Development Timeline

### Technical Evolution
{{quarter}} → {{quarter}}: {{technical_growth_description}}
{{technical_skill_progression_summary}}

### Complexity Handling Growth
- **Early Period**: {{early_complexity_level}}
- **Recent Period**: {{recent_complexity_level}}  
- **Growth Indicator**: {{complexity_handling_improvement}}

## Personal Contribution Patterns

### Work Distribution Evolution
- **Feature Development**: {{feature_trend}} ({{feature_change}}% change)
- **Bug Resolution**: {{bug_trend}} ({{bug_change}}% change)
- **Technical Leadership**: {{leadership_trend}} ({{leadership_change}}% change)
- **Documentation**: {{docs_trend}} ({{docs_change}}% change)

### Collaboration Pattern Growth
- **Cross-Repository Work**: {{cross_repo_evolution}}
- **Code Review Participation**: {{code_review_growth}}
- **Mentorship Activities**: {{mentorship_development}}

## Personal Development Insights

### Strength Areas (Consistent Excellence)
1. **{{consistent_strength_1}}**: {{strength_evidence_and_impact}}
2. **{{consistent_strength_2}}**: {{strength_evidence_and_impact}}

### Growth Areas (Significant Improvement)
1. **{{growth_area_1}}**: {{improvement_evidence}} ({{improvement_percentage}}% improvement)
2. **{{growth_area_2}}**: {{improvement_evidence}} ({{improvement_percentage}}% improvement)

### Emerging Capabilities
1. **{{emerging_skill_1}}**: {{evidence_of_emergence}}
2. **{{emerging_skill_2}}**: {{evidence_of_emergence}}

## Personal Performance Recommendations

### Continue Leveraging
- **{{leverage_area_1}}**: {{how_to_maximize}} 
- **{{leverage_area_2}}**: {{how_to_maximize}}

### Development Priorities
- **{{priority_1}}**: {{specific_development_plan}}
- **{{priority_2}}**: {{specific_development_plan}}

### Next Quarter Opportunities
1. **{{opportunity_1}}**: {{opportunity_details_and_approach}}
2. **{{opportunity_2}}**: {{opportunity_details_and_approach}}
3. **{{opportunity_3}}**: {{opportunity_details_and_approach}}

## Personal Data Analysis Methodology

### Analysis Period
- **Start**: Q1 {start_year}
- **End**: Q4 {end_year}
- **Quarters Analyzed**: {len(quarters)}

### Personal Data Sources
- **JIRA**: Personal ticket assignment and completion history
- **GitHub**: Personal commit and PR history across all quarters
- **Identity**: Git config and GitHub username for attribution

### Growth Calculation Methods
- **Trend Analysis**: Linear regression on quarterly metrics
- **Skill Development**: Complexity scoring of tickets and code contributions
- **Learning Velocity**: Rate of new technology/framework adoption
- **Leadership Growth**: Mentorship and cross-team collaboration indicators

### Privacy and Ethics
- **Individual Focus**: Only personal performance data included
- **No Comparative Rankings**: Analysis focuses on personal growth patterns
- **Development Oriented**: Insights aimed at personal skill development
- **Confidential**: Personal performance data not shared beyond individual

---

### ⚠️ Alpha Development Disclaimer

**This report was generated by MCP-Tools in alpha development stage:**
- **Not for official use**: Manual validation of all data and conclusions required
- **Development status**: Features and accuracy are not production-ready  
- **Data limitations**: Report may contain incomplete or inaccurate analysis
- **Internal use only**: Not suitable for external reporting or personal evaluations

*Generated using MCP Tools Personal Performance Analysis (Alpha Development Version) with multi-quarter growth tracking*
""",
                },
                
                "external_context": context_content,
                
                "success_criteria": {
                    "multi_quarter_collection": "Personal data successfully collected for all quarters in the specified period",
                    "trend_identification": "Personal performance trends and growth patterns identified accurately",
                    "skill_development_tracking": "Personal skill evolution and learning velocity calculated",
                    "growth_recommendations": "Personalized development recommendations generated based on trends",
                    "privacy_compliance": "Only personal data analyzed, no comparative rankings or team member data included"
                },
                
                "troubleshooting": {
                    "data_gaps": "Some quarters may have limited data - focus analysis on quarters with sufficient contribution data",
                    "identity_consistency": "Verify git config and GitHub username consistency across the analysis period",
                    "jira_access_historical": "Historical JIRA data may require different query approaches for older quarters",
                    "github_rate_limits": "Large period analysis may hit rate limits - consider breaking into smaller periods if needed"
                }
            }
            
            logger.info(f"Personal quarter-over-quarter instructions generated for: {period}")
            return qoq_instructions
            
        except Exception as e:
            logger.error(f"Error generating personal quarter-over-quarter instructions: {str(e)}")
            return ToolBase.create_error_response(
                f"Failed to generate personal quarter-over-quarter instructions: {str(e)}",
                error_type=type(e).__name__
            )


def get_context_fallback(context_type: str) -> str:
    """Get fallback context content for personal performance analysis"""
    
    fallbacks = {
        "personal_performance": """# Personal Performance Analysis Guidelines

## Personal Data Collection Strategy
- **JIRA Analysis**: Focus on personally assigned tickets and completion patterns
- **GitHub Analysis**: Personal commit history and contribution patterns
- **Identity Management**: Use git config and GitHub authentication to identify personal contributions
- **Privacy First**: Only analyze personal data, no team member comparisons

## Personal Metrics Framework
- **Individual Productivity**: Personal tickets completed, commits made, code contributions
- **Personal Growth**: Skill development indicators, complexity handling evolution  
- **Learning Velocity**: Adoption of new technologies and frameworks over time
- **Contribution Patterns**: Balance between feature work, bug fixes, and technical contributions

## Personal Development Focus
- **Strength Identification**: Areas of consistent high performance
- **Growth Opportunities**: Skills and areas for development based on personal patterns
- **Learning Recommendations**: Personalized development paths based on contribution history
- **Career Development**: Growth trajectory analysis for professional development

## Privacy and Ethics
- **Individual Only**: Analysis limited to personal contributions and growth
- **No Team Comparisons**: No ranking or comparison with other team members
- **Self-Assessment**: Designed for personal reflection and development planning
- **Confidential**: Personal performance data not shared beyond the individual""",
        
        "personal_quarter_over_quarter": """# Personal Quarter-over-Quarter Analysis Guidelines

## Multi-Quarter Personal Data Strategy
- **Consistent Identity**: Track personal contributions across multiple quarters using consistent user identifiers
- **Growth Pattern Analysis**: Identify trends in personal productivity, skill development, and contribution complexity
- **Learning Velocity**: Measure rate of skill acquisition and technology adoption over time
- **Personal Evolution**: Track career and skill development trajectory across quarters

## Trend Analysis Methods
- **Productivity Trends**: Quarter-to-quarter changes in ticket completion and code contribution volume
- **Skill Development**: Evolution of technical complexity and scope of personal contributions
- **Learning Indicators**: Adoption of new technologies, frameworks, and development practices
- **Leadership Growth**: Mentorship, code review, and cross-team collaboration evolution

## Personal Growth Assessment
- **Consistency Analysis**: Identify stable performance patterns and areas of variability
- **Improvement Areas**: Quarters showing significant personal growth or skill development
- **Challenge Periods**: Quarters with lower productivity and analysis of contributing factors
- **Development Recommendations**: Personalized growth plans based on historical patterns

## Long-Term Career Development
- **Skill Trajectory**: Multi-quarter view of technical skill development and specialization
- **Career Growth**: Leadership and influence development patterns over time
- **Learning Path**: Optimal development areas based on personal growth history
- **Goal Setting**: Data-driven personal development goals for future quarters"""
    }
    
    return fallbacks.get(context_type, "")