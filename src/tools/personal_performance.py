#!/usr/bin/env python3
"""
Personal Performance Analysis Tools

PREREQUISITES - MUST BE CONFIGURED BEFORE USE:
• GitHub CLI: `brew install gh` + `gh auth login`
• Atlassian MCP Server: Authentication and cloud ID configuration required
• JIRA Access: User must have access to JIRA project with appropriate permissions
• Git Configuration: `git config --global user.name` and `git config --global user.email` must be set
• JQ: `brew install jq` for JSON processing

Generate personal performance analysis for individual contributors with personal development
tracking and growth assessment by RETURNING INSTRUCTIONS for Claude Code to execute 
actual API calls rather than performing analysis directly.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from fastmcp import FastMCP
from .base import ToolBase, get_context_fallback

logger = logging.getLogger(__name__)


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
                    "overview": f"Generate personal quarterly performance report for {quarter_name}. Focus: {description or 'individual contributor performance analysis and development guidance'}.",
                    
                    "prerequisite_validation": [
                        "Verify GitHub CLI authentication: `gh auth status`",
                        "Verify Atlassian MCP server connection and cloud ID access",
                        "Get current user identity from git config: `git config --global user.name` and `git config --global user.email`",
                        "Ensure `jq` is available for JSON processing"
                    ],
                    
                    "user_identification_steps": [
                        "## Current User Identification",
                        "Execute: git config --global user.name",
                        "Execute: git config --global user.email",
                        "Execute: gh api user --jq '.login' (GitHub username)",
                        "# Use these identifiers to filter personal contributions from team data"
                    ],
                    
                    "data_collection_steps": [
                        "## Personal JIRA Data Collection",
                        "# First get current user's Atlassian account ID",
                        f"Execute: mcp__atlassian__lookupJiraAccountId(cloudId='credify.atlassian.net', searchString='{{user_email_from_git_config}}')",
                        "# Then search for personal tickets",
                        f"Execute: mcp__atlassian__searchJiraIssuesUsingJql(cloudId='credify.atlassian.net', jql='project = \"{team_prefix}\" AND assignee = \"{{user_account_id}}\" AND created >= \"{start_date}\" AND created <= \"{end_date}\" ORDER BY created DESC', fields=['summary', 'description', 'status', 'issuetype', 'priority', 'created', 'assignee', 'components', 'timeoriginalestimate', 'timespent'], maxResults=250)",
                        "",
                        "## Personal GitHub Data Collection",
                        "# Search for personal commits using GitHub username",
                        f"Execute: gh api 'search/commits?q=author:{{github_username}}+author-date:{start_date}..{end_date}+org:credify' --paginate",
                        "# Alternative: Search specific repositories",
                        f"Execute: gh search repos 'org:credify topic:{team_prefix.lower()} OR {team_prefix.lower()} in:name' --json name",
                        "# For each repository, get personal commits:",
                        f"Execute: gh api 'repos/credify/{{repo_name}}/commits?author={{github_username}}&since={start_date}T00:00:00Z&until={end_date}T23:59:59Z' --paginate",
                        "",
                        "## Personal Pull Request Analysis",
                        f"Execute: gh search prs 'org:credify author:{{github_username}} created:{start_date}..{end_date}' --json number,title,url,state,createdAt,mergedAt,additions,deletions"
                    ],
                    
                    "analysis_requirements": [
                        "**Personal JIRA Analysis:**",
                        "- Total tickets assigned and completed personally",
                        "- Personal issue type distribution and preferences",
                        "- Average completion time for personal tickets",
                        "- Areas of technical focus based on ticket components",
                        "- Time estimation accuracy (estimated vs actual time spent)",
                        "",
                        "**Personal GitHub Analysis:**", 
                        "- Total personal commits in the quarter",
                        "- Personal code contribution metrics (lines added/deleted)",
                        "- Repository diversity (how many different repos contributed to)",
                        "- Pull request creation and merge rate",
                        "- Commit message quality and patterns",
                        "",
                        "**Personal Productivity Analysis:**",
                        "- Personal velocity trends within the quarter",
                        "- Balance between feature work, bug fixes, and technical debt",
                        "- Collaboration patterns (code reviews, pair programming indicators)",
                        "- Learning and growth indicators from commit/ticket patterns",
                        "",
                        "**Development Focus Analysis:**",
                        "- Primary technical areas worked on (from ticket components and commit paths)",
                        "- Skill development trajectory based on increasing complexity",
                        "- Cross-functional contributions and learning scope"
                    ],
                    
                    "required_output_format": f"""
# Personal Performance Report - {quarter_name}

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

*Generated using MCP Tools Personal Performance Analysis with privacy-focused data collection*
""",
                },
                
                "external_context": context_content,
                
                "success_criteria": {
                    "user_identification": "Current user identity successfully determined from git config and GitHub auth",
                    "personal_data_collection": "Personal JIRA tickets and GitHub commits successfully retrieved",
                    "productivity_analysis": "Personal productivity metrics calculated accurately",
                    "growth_analysis": "Personal skill development and learning opportunities identified",
                    "report_generation": "Comprehensive personal development report generated",
                    "privacy_compliance": "Only personal data included, no team comparisons or individual rankings"
                },
                
                "troubleshooting": {
                    "user_identity_issues": "Verify git config is set and GitHub CLI is authenticated with correct account",
                    "jira_access_issues": "Ensure JIRA access and verify account ID lookup works correctly",
                    "github_rate_limits": "Use authenticated GitHub CLI to increase API rate limits",
                    "empty_personal_data": "Verify user has contributed to specified team prefix during the quarter"
                }
            }
            
            logger.info(f"Personal quarterly report instructions generated for: {quarter_name}")
            return personal_instructions
            
        except Exception as e:
            logger.error(f"Error generating personal quarterly report instructions: {str(e)}")
            return ToolBase.create_error_response(
                f"Failed to generate personal quarterly report instructions: {str(e)}",
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
                    ] + [
                        f"## {quarter} Data Collection",
                        f"# JIRA data for {quarter}",
                        f"Execute: mcp__atlassian__searchJiraIssuesUsingJql(...) # with appropriate date ranges for {quarter}",
                        f"# GitHub data for {quarter}",
                        f"Execute: gh api 'search/commits?q=author:{{github_username}}+author-date:{{quarter_start}}..{{quarter_end}}+org:credify'",
                        f"# Pull request data for {quarter}",
                        f"Execute: gh search prs 'org:credify author:{{github_username}} created:{{quarter_start}}..{{quarter_end}}'",
                        ""
                        for quarter in quarters
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

## Personal Growth Executive Summary
*Analysis period: {start_year} to {end_year} ({len(quarters)} quarters)*

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

*Generated using MCP Tools Personal Performance Analysis with multi-quarter growth tracking*
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