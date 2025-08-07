#!/usr/bin/env python3
"""
JIRA-GitHub Report Coordinator - Specialized 3-Agent Orchestration System

Specialized coordination system for JIRA→GitHub reporting tools using the proven 3-agent pattern:
- Subagent 1: JIRA Analysis & PR Discovery 
- Subagent 2: GitHub Metrics Collection & Cross-Reference
- Subagent 3: Report Generation & Synthesis with JIRA-GitHub Bridging

This coordinator is specifically designed for reports that require cross-referencing
JIRA ticket data with GitHub contribution data (PRs, commits) to provide enhanced
attribution accuracy and comprehensive development insights.

Use this for: team quarterly reports, quarter-over-quarter analysis, personal performance reports
Not suitable for: pure technical reviews, design analysis, or non-development reports
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable

logger = logging.getLogger(__name__)


class JiraGithubReportCoordinator:
    """
    Specialized 3-Subagent coordination system for JIRA-GitHub integrated reporting.
    
    Provides proven architecture for development-focused reports that require:
    - JIRA ticket analysis with PR link extraction
    - GitHub metrics collection using discovered PR links
    - Cross-referenced analysis for enhanced attribution accuracy
    
    Each report type can customize queries and analysis steps while maintaining
    the core coordination pattern that ensures high-quality data integration.
    """
    
    @staticmethod
    def generate_base_subagent_1_instructions(
        analysis_type: str,
        team_prefix: str, 
        start_date: str, 
        end_date: str,
        jira_query_customizer: Optional[str] = None,
        additional_steps: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate instructions for Subagent 1: JIRA Analysis & Data Discovery
        
        Args:
            analysis_type: Type of analysis (e.g., "team_quarterly", "personal_quarterly")
            team_prefix: Team/project prefix for JIRA queries
            start_date: Analysis start date (YYYY-MM-DD)
            end_date: Analysis end date (YYYY-MM-DD)
            jira_query_customizer: Optional string to customize/extend base JIRA query
            additional_steps: Optional list of custom analysis steps specific to report type
        """
        
        base_jira_query = f'project = "{team_prefix}" AND created >= "{start_date}" AND created <= "{end_date}" ORDER BY created DESC'
        
        # Allow customization of JIRA query per report type
        jira_query = f"{base_jira_query}. {jira_query_customizer}" if jira_query_customizer else base_jira_query
            
        return {
            "subagent": "1_jira_analysis_data_discovery",
            "purpose": f"Process JIRA tickets for {analysis_type} to extract PR links and analyze assignments",
            "execution_steps": [
                "## User Identity Verification",
                "Execute: git config --global user.name",
                "Execute: git config --global user.email", 
                "Execute: gh api user --jq '.login'",
                "Execute: mcp__atlassian__lookupJiraAccountId(cloudId='credify.atlassian.net', searchString='{user_email}')",
                "",
                "## JIRA Ticket Collection",
                f"Execute: mcp__atlassian__searchJiraIssuesUsingJql(cloudId='credify.atlassian.net', jql='{jira_query}', fields=['summary', 'description', 'status', 'issuetype', 'priority', 'created', 'assignee', 'components', 'timeoriginalestimate', 'timespent', 'comment'], maxResults=500)",
                "",
                "## PR Link Extraction from JIRA",
                "# Parse ticket descriptions and comments for GitHub PR URLs",
                "# Extract patterns: 'PR: https://github.com/...', 'Resolves #123', '/pull/' URLs",
                "# Build JIRA ticket → GitHub PR mapping for accurate attribution",
                "# Store extracted PR URLs for Subagent 2 processing",
                "",
                "## Assignment and Activity Analysis",
                "# Analyze ticket assignment patterns and team activity",
                "# Track assignment distribution and completion rates",
                "# Identify technical focus areas from components and descriptions",
                "# Generate comprehensive JIRA metrics summary",
                "",
                "## Team Composition Analysis (if applicable)",
                "# Extract assignee information for team size tracking",
                "# Identify unique contributors and their activity patterns",
                "# Track new contributors and retention patterns",
                "",
                "## Report-Specific Analysis Steps",
                *(additional_steps or [])
            ],
            "output_format": {
                "jira_metrics_summary": "Comprehensive ticket analysis with assignment patterns",
                "extracted_pr_links": "List of GitHub PR URLs found in JIRA tickets", 
                "jira_pr_mapping": "Dictionary mapping JIRA ticket IDs to PR URLs",
                "technical_focus_areas": "Primary areas of work from ticket analysis",
                "team_composition_data": "Team member activity and contribution patterns (if applicable)"
            }
        }
    
    @staticmethod
    def generate_base_subagent_2_instructions(
        analysis_type: str,
        team_prefix: str,
        start_date: str, 
        end_date: str,
        github_query_customizer: Optional[Callable] = None,
        additional_steps: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate instructions for Subagent 2: GitHub Metrics Collection & Cross-Reference
        
        Args:
            analysis_type: Type of analysis (e.g., "team_quarterly", "personal_quarterly")
            team_prefix: Team/project prefix for filtering
            start_date: Analysis start date (YYYY-MM-DD)
            end_date: Analysis end date (YYYY-MM-DD)
            github_query_customizer: Optional function to customize GitHub queries per report type
            additional_steps: Optional list of custom analysis steps specific to report type
        """
        
        base_github_queries = [
            f"gh api 'search/commits?q=author-date:{start_date}..{end_date}+org:credify' --paginate",
            f"gh search prs 'org:credify created:{start_date}..{end_date}' --json number,title,url,author,createdAt,mergedAt"
        ]
        
        # Allow customization of GitHub queries per report type  
        if github_query_customizer:
            github_queries = github_query_customizer(base_github_queries, team_prefix, start_date, end_date)
        else:
            github_queries = base_github_queries
            
        return {
            "subagent": "2_github_metrics_cross_reference",
            "purpose": f"Collect detailed GitHub PR and commit data for {analysis_type} using discovered PR links",
            "execution_steps": [
                "## Use PR Links from Subagent 1",
                "# Process PR URLs discovered by Subagent 1 from JIRA tickets",
                "# For each discovered PR URL, extract detailed metrics",
                "",
                "## Enhanced PR Data Collection", 
                "# For each PR URL from Subagent 1:",
                "Execute: gh pr view {pr_url} --json number,title,state,createdAt,mergedAt,additions,deletions,commits,changedFiles,reviewDecision,author",
                "Execute: gh pr diff {pr_url} --name-only | wc -l  # Files changed count",
                "Execute: gh pr view {pr_url} --json comments --jq '.comments | length'  # Comment count",
                "",
                "## Comprehensive Commit Analysis",
                *[f"Execute: {query}" for query in github_queries],
                "# Cross-reference commits with PR URLs from Subagent 1",
                "# Identify commits that are part of JIRA-linked PRs vs standalone work",
                "",
                "## Repository Contribution Mapping",
                "Execute: gh search repos 'org:credify' --json name,fullName | head -30",
                "# For key repositories, get contribution statistics",
                f"Execute: gh api 'repos/credify/{{repo_name}}/stats/contributors'",
                "# Filter contributors active during analysis period",
                "",
                "## PR→JIRA Cross-Reference Enhancement",
                "# Use Subagent 1's JIRA→PR mapping to enhance GitHub metrics", 
                "# Calculate PR completion rates vs JIRA ticket completion",
                "# Identify work attribution gaps between JIRA and GitHub",
                "# Generate comprehensive cross-reference analysis",
                "",
                "## Report-Specific GitHub Analysis Steps",
                *(additional_steps or [])
            ],
            "output_format": {
                "enhanced_pr_metrics": "Detailed PR statistics with JIRA attribution",
                "commit_statistics": "Commit frequency, authors, repository diversity", 
                "cross_reference_analysis": "JIRA work vs GitHub contributions alignment",
                "contribution_quality_metrics": "PR size, review feedback, merge success rates",
                "repository_activity_summary": "Cross-repository contribution patterns"
            }
        }
    
    @staticmethod
    def generate_base_subagent_3_instructions(
        analysis_type: str,
        report_name: str,
        additional_steps: Optional[List[str]] = None,
        custom_output_sections: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate instructions for Subagent 3: Report Generation & Synthesis
        
        Args:
            analysis_type: Type of analysis (e.g., "team_quarterly", "personal_quarterly")
            report_name: Name of the report being generated
            additional_steps: Optional custom analysis steps for specific report types
            custom_output_sections: Optional custom output sections for specific report types
        """
        
        default_analysis_steps = [
            "## Data Synthesis",
            "# Combine Subagent 1 JIRA analysis with Subagent 2 GitHub metrics",
            "# Cross-reference JIRA ticket completion with actual merged PRs",
            "# Calculate accurate contribution attribution across data sources",
            "",
            "## Enhanced Performance Metrics", 
            "# Productivity analysis: JIRA tickets + GitHub PRs with proper attribution",
            "# Code quality indicators: PR review feedback, merge success rates",
            "# Technical growth: Complexity evolution in both JIRA and GitHub data",
            "# Learning velocity: New technologies/frameworks from commit analysis",
            "",
            "## Gap Analysis",
            "# Identify JIRA tickets without corresponding GitHub PRs (process work)",
            "# Identify GitHub PRs without corresponding JIRA tickets (maintenance)",
            "# Calculate work attribution accuracy and identify improvement areas",
            "",
            "## Comprehensive Insights Generation",
            "# Generate recommendations based on combined dataset",
            "# Identify patterns and trends from coordinated analysis",
            "# Provide actionable insights for improvement and growth"
        ]
        
        default_output_sections = [
            "comprehensive_report",
            "attribution_analysis", 
            "performance_recommendations",
            "improvement_opportunities"
        ]
        
        analysis_steps = additional_steps or default_analysis_steps
        output_sections = custom_output_sections or default_output_sections
        
        return {
            "subagent": "3_report_generation_synthesis",
            "purpose": f"Synthesize all data into comprehensive {analysis_type} report",
            "execution_steps": analysis_steps,
            "output_format": {
                section: f"Generated {section} for {report_name}" 
                for section in output_sections
            }
        }
    
    @staticmethod
    def generate_coordination_instructions(
        tool_name: str,
        analysis_context: str,
        subagent_1: Dict[str, Any],
        subagent_2: Dict[str, Any], 
        subagent_3: Dict[str, Any],
        coordination_notes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive coordination instructions for all 3 subagents
        
        Args:
            tool_name: Name of the tool using coordination
            analysis_context: Context description for the analysis
            subagent_1: Subagent 1 instructions
            subagent_2: Subagent 2 instructions
            subagent_3: Subagent 3 instructions
            coordination_notes: Optional custom coordination notes
        """
        
        default_coordination_notes = [
            "Subagent 1 runs first to discover JIRA→PR mappings and establish data foundation",
            "Subagent 2 uses Subagent 1's PR links for enhanced GitHub analysis",
            "Subagent 3 synthesizes both datasets for comprehensive report generation",
            "All subagents work independently on their domain expertise",
            "Data handoff via structured interim results ensures consistency",
            "Cross-reference validation maintains attribution accuracy"
        ]
        
        coordination_notes = coordination_notes or default_coordination_notes
        
        return {
            "subagent_coordination": {
                "execution_strategy": "Execute all 3 subagents in coordinated sequence for maximum efficiency and data accuracy",
                "subagent_1": subagent_1,
                "subagent_2": subagent_2, 
                "subagent_3": subagent_3,
                "coordination_notes": coordination_notes
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
                "# Generate accurate contribution metrics with enhanced precision",
                "# Produce actionable insights based on coordinated analysis"
            ],
            
            "success_criteria": {
                "subagent_coordination": "All 3 subagents executed successfully with proper data handoff",
                "jira_pr_bridging": "PR links successfully extracted from JIRA tickets with high attribution accuracy",
                "github_enhancement": "GitHub metrics collected using JIRA-discovered PR links for improved accuracy", 
                "cross_reference_analysis": "JIRA work completion validated against GitHub PR delivery",
                "comprehensive_insights": "Enhanced insights generated from coordinated multi-source analysis",
                "attribution_accuracy": "Work attribution accuracy >= 85% between JIRA and GitHub data"
            },
            
            "troubleshooting": {
                "subagent_coordination_issues": "Verify all 3 subagents can execute in coordinated sequence without conflicts",
                "jira_pr_extraction_issues": "Check JIRA ticket descriptions and comments contain GitHub PR URLs",
                "github_pr_access_issues": "Verify GitHub CLI can access discovered PR URLs from JIRA",
                "attribution_accuracy_low": "Review JIRA ticket PR linking practices and suggest improvements",
                "cross_reference_failures": "Validate JIRA ticket completion dates align with PR merge dates",
                "rate_limit_coordination": "Implement proper rate limiting across all 3 subagents"
            }
        }
    
    @staticmethod
    def create_team_quarterly_customizations() -> Dict[str, Callable]:
        """Customization functions for quarterly team reports"""
        
        def team_jira_query_customizer(base_query: str, team_prefix: str, start_date: str, end_date: str) -> str:
            # Team reports need broader assignee data, not just current user
            return f'project = "{team_prefix}" AND created >= "{start_date}" AND created <= "{end_date}" ORDER BY created DESC'
        
        def team_github_query_customizer(base_queries: List[str], team_prefix: str, start_date: str, end_date: str) -> List[str]:
            # Team reports need organization-wide data, not user-specific
            return [
                f"gh api 'search/commits?q=author-date:{start_date}..{end_date}+org:credify' --paginate",
                f"gh search prs 'org:credify created:{start_date}..{end_date}' --json number,title,url,author,createdAt,mergedAt",
                f"gh api 'search/users?q=type:user+org:credify' --paginate"  # Team member discovery
            ]
        
        return {
            "jira_query_customizer": team_jira_query_customizer,
            "github_query_customizer": team_github_query_customizer
        }
    
    @staticmethod
    def create_personal_quarterly_customizations() -> Dict[str, Callable]:
        """Customization functions for personal quarterly reports"""
        
        def personal_jira_query_customizer(base_query: str, team_prefix: str, start_date: str, end_date: str) -> str:
            # Personal reports need user-specific assignee filtering
            return f'project = "{team_prefix}" AND assignee = "{{user_account_id}}" AND created >= "{start_date}" AND created <= "{end_date}" ORDER BY created DESC'
        
        def personal_github_query_customizer(base_queries: List[str], team_prefix: str, start_date: str, end_date: str) -> List[str]:
            # Personal reports need user-specific filtering
            return [
                f"gh api 'search/commits?q=author:{{github_username}}+author-date:{start_date}..{end_date}+org:credify' --paginate",
                f"gh search prs 'org:credify author:{{github_username}} created:{start_date}..{end_date}' --json number,title,url,author,createdAt,mergedAt"
            ]
        
        return {
            "jira_query_customizer": personal_jira_query_customizer,
            "github_query_customizer": personal_github_query_customizer
        }
    
    @staticmethod 
    def create_quarter_over_quarter_customizations() -> Dict[str, Callable]:
        """Customization functions for quarter-over-quarter analysis"""
        
        def qoq_jira_query_customizer(base_query: str, team_prefix: str, start_date: str, end_date: str) -> str:
            # QoQ analysis needs extended date ranges and team evolution tracking
            return f'project = "{team_prefix}" AND created >= "{start_date}" AND created <= "{end_date}" ORDER BY created ASC'  # ASC for trend analysis
        
        def qoq_github_query_customizer(base_queries: List[str], team_prefix: str, start_date: str, end_date: str) -> List[str]:
            # QoQ analysis needs historical data with trend analysis focus
            return [
                f"gh api 'search/commits?q=author-date:{start_date}..{end_date}+org:credify+sort:author-date-asc' --paginate",
                f"gh search prs 'org:credify created:{start_date}..{end_date} sort:created-asc' --json number,title,url,author,createdAt,mergedAt",
                f"gh api 'search/users?q=type:user+org:credify+created:<{end_date}' --paginate"  # Historical team composition
            ]
        
        return {
            "jira_query_customizer": qoq_jira_query_customizer,
            "github_query_customizer": qoq_github_query_customizer
        }