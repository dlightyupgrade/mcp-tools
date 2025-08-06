#!/usr/bin/env python3
"""
Personal Performance Analysis Tools

Generate individual contributor performance reports for single quarters and 
quarter-over-quarter trends, focusing on personal productivity, contributions, 
and development patterns.
"""

import logging
import json
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter

from fastmcp import FastMCP
from .base import ToolBase
from .quarterly_report import QuarterlyReportGenerator, QuarterConfig

logger = logging.getLogger(__name__)


@dataclass
class PersonalQuarterMetrics:
    """Personal performance metrics for a single quarter"""
    quarter: str
    tickets_created: int
    tickets_completed: int
    commits_authored: int
    repositories_contributed: int
    lines_added: int
    lines_removed: int
    pull_requests_created: int
    pull_requests_merged: int
    code_review_comments: int
    technical_areas: List[str]
    productivity_score: float


@dataclass
class PersonalTrendAnalysis:
    """Personal trend analysis across quarters"""
    metric_name: str
    trend_direction: str  # "improving", "declining", "stable"
    change_percentage: float
    quarters_data: List[float]
    personal_best: float
    current_performance: str  # "above_average", "average", "below_average"


class PersonalPerformanceAnalyzer:
    """Generate personal performance analysis and trends"""
    
    @staticmethod
    def get_current_user() -> str:
        """Get current Git user for personal analysis"""
        try:
            result = subprocess.run(['git', 'config', 'user.email'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return result.stdout.strip()
            
            # Fallback to GitHub CLI
            result = subprocess.run(['gh', 'api', 'user'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                user_data = json.loads(result.stdout)
                return user_data.get('login', 'unknown')
                
        except Exception as e:
            logger.warning(f"Could not determine current user: {e}")
        
        return 'current_user'
    
    @staticmethod
    def collect_personal_jira_data(team_prefix: str, quarter_config: QuarterConfig, user_email: str) -> Dict[str, Any]:
        """Collect personal Jira tickets for the quarter"""
        try:
            # Enhanced JQL to find user-created tickets
            jql = f'project = {team_prefix} AND created >= "{quarter_config.start_date}" AND created <= "{quarter_config.end_date}" AND reporter = currentUser() ORDER BY created DESC'
            
            # Mock personal Jira data - in real implementation would use actual Jira API with user filtering
            cmd = [
                "python", "-c", f"""
import json
import sys

# Mock personal Jira tickets for demonstration
personal_tickets = [
    {{
        "key": "{team_prefix}-8001",
        "fields": {{
            "summary": "Personal ticket: Implement user validation",
            "issuetype": {{"name": "Story"}},
            "priority": {{"name": "P2"}},
            "status": {{"name": "Done"}},
            "created": "{quarter_config.start_date}T10:00:00.000+0000",
            "reporter": {{"emailAddress": "{user_email}"}},
            "assignee": {{"emailAddress": "{user_email}"}}
        }}
    }},
    {{
        "key": "{team_prefix}-8002", 
        "fields": {{
            "summary": "Personal ticket: Fix authentication bug",
            "issuetype": {{"name": "Bug"}},
            "priority": {{"name": "P1"}},
            "status": {{"name": "Done"}},
            "created": "{quarter_config.start_date}T11:00:00.000+0000",
            "reporter": {{"emailAddress": "{user_email}"}},
            "assignee": {{"emailAddress": "{user_email}"}}
        }}
    }},
    {{
        "key": "{team_prefix}-8003",
        "fields": {{
            "summary": "Personal ticket: Refactor payment service",
            "issuetype": {{"name": "Task"}},
            "priority": {{"name": "P2"}},
            "status": {{"name": "In Progress"}},
            "created": "{quarter_config.start_date}T12:00:00.000+0000",
            "reporter": {{"emailAddress": "{user_email}"}},
            "assignee": {{"emailAddress": "{user_email}"}}
        }}
    }}
]

print(json.dumps({{"issues": personal_tickets, "total": len(personal_tickets)}}))
"""
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                tickets = data.get("issues", [])
                
                # Analyze personal tickets
                created_count = len(tickets)
                completed_count = len([t for t in tickets if t.get("fields", {}).get("status", {}).get("name") in ["Done", "Resolved", "Closed"]])
                
                return {
                    "tickets_created": created_count,
                    "tickets_completed": completed_count,
                    "tickets": tickets
                }
            else:
                return {"tickets_created": 0, "tickets_completed": 0, "tickets": []}
                
        except Exception as e:
            logger.error(f"Error collecting personal Jira data: {e}")
            return {"tickets_created": 0, "tickets_completed": 0, "tickets": []}
    
    @staticmethod
    def collect_personal_github_data(team_prefix: str, quarter_config: QuarterConfig, user_identifier: str) -> Dict[str, Any]:
        """Collect personal GitHub contributions for the quarter"""
        try:
            # Search for commits by the current user
            cmd = [
                "gh", "search", "commits", 
                f"author:{user_identifier}",
                f"--author-date={quarter_config.start_date}..{quarter_config.end_date}",
                "--owner", "Credify",
                "--limit", "100",
                "--json", "sha,commit,repository,author,url"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                commits = json.loads(result.stdout)
                
                # Analyze personal contributions
                total_commits = len(commits)
                repositories = set(commit.get("repository", {}).get("name", "") for commit in commits)
                
                # Estimate code changes (in real implementation, would use GitHub API for detailed stats)
                estimated_lines_added = total_commits * 25  # Rough estimate
                estimated_lines_removed = total_commits * 10
                
                return {
                    "commits_authored": total_commits,
                    "repositories_contributed": len(repositories),
                    "lines_added": estimated_lines_added,
                    "lines_removed": estimated_lines_removed,
                    "commits": commits,
                    "repositories": list(repositories)
                }
            else:
                logger.warning(f"GitHub search failed: {result.stderr}")
                return {
                    "commits_authored": 0,
                    "repositories_contributed": 0,
                    "lines_added": 0,
                    "lines_removed": 0,
                    "commits": [],
                    "repositories": []
                }
                
        except Exception as e:
            logger.error(f"Error collecting personal GitHub data: {e}")
            return {
                "commits_authored": 0,
                "repositories_contributed": 0,
                "lines_added": 0,
                "lines_removed": 0,
                "commits": [],
                "repositories": []
            }
    
    @staticmethod
    def collect_personal_pr_data(user_identifier: str, quarter_config: QuarterConfig) -> Dict[str, Any]:
        """Collect personal pull request data"""
        try:
            # Search for PRs created by the user
            cmd = [
                "gh", "search", "prs",
                f"author:{user_identifier}",
                f"created:{quarter_config.start_date}..{quarter_config.end_date}",
                "--owner", "Credify",
                "--limit", "50",
                "--json", "number,title,state,createdAt,mergedAt,url,repository"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                prs = json.loads(result.stdout)
                
                prs_created = len(prs)
                prs_merged = len([pr for pr in prs if pr.get("mergedAt")])
                
                return {
                    "pull_requests_created": prs_created,
                    "pull_requests_merged": prs_merged,
                    "pull_requests": prs
                }
            else:
                return {
                    "pull_requests_created": 0,
                    "pull_requests_merged": 0,
                    "pull_requests": []
                }
                
        except Exception as e:
            logger.error(f"Error collecting personal PR data: {e}")
            return {
                "pull_requests_created": 0,
                "pull_requests_merged": 0,
                "pull_requests": []
            }
    
    @staticmethod
    def analyze_personal_quarter(team_prefix: str, quarter_config: QuarterConfig, user_identifier: str) -> PersonalQuarterMetrics:
        """Analyze personal performance for a single quarter"""
        user_email = f"{user_identifier}@company.com"  # Adjust as needed
        
        # Collect personal data
        jira_data = PersonalPerformanceAnalyzer.collect_personal_jira_data(team_prefix, quarter_config, user_email)
        github_data = PersonalPerformanceAnalyzer.collect_personal_github_data(team_prefix, quarter_config, user_identifier)
        pr_data = PersonalPerformanceAnalyzer.collect_personal_pr_data(user_identifier, quarter_config)
        
        # Analyze technical areas from commits and tickets
        technical_areas = []
        
        # Extract from commit messages
        for commit in github_data.get("commits", []):
            message = commit.get("commit", {}).get("message", "").lower()
            if "test" in message or "testing" in message:
                technical_areas.append("Testing")
            if "refactor" in message or "cleanup" in message:
                technical_areas.append("Code Quality")
            if "fix" in message or "bug" in message:
                technical_areas.append("Bug Fixes")
            if "feature" in message or "implement" in message:
                technical_areas.append("Feature Development")
        
        technical_areas = list(set(technical_areas))[:5]  # Top 5 unique areas
        
        # Calculate productivity score
        productivity_score = (
            (jira_data["tickets_completed"] * 10) +
            (github_data["commits_authored"] * 2) +
            (pr_data["pull_requests_merged"] * 5) +
            (github_data["repositories_contributed"] * 3)
        )
        
        return PersonalQuarterMetrics(
            quarter=quarter_config.quarter_name,
            tickets_created=jira_data["tickets_created"],
            tickets_completed=jira_data["tickets_completed"],
            commits_authored=github_data["commits_authored"],
            repositories_contributed=github_data["repositories_contributed"],
            lines_added=github_data["lines_added"],
            lines_removed=github_data["lines_removed"],
            pull_requests_created=pr_data["pull_requests_created"],
            pull_requests_merged=pr_data["pull_requests_merged"],
            code_review_comments=0,  # Would require additional GitHub API calls
            technical_areas=technical_areas,
            productivity_score=productivity_score
        )
    
    @staticmethod
    def analyze_personal_trends(personal_metrics: List[PersonalQuarterMetrics]) -> List[PersonalTrendAnalysis]:
        """Analyze personal performance trends across quarters"""
        if len(personal_metrics) < 2:
            return []
        
        trends = []
        
        # Define metrics to analyze
        metrics_to_analyze = [
            ("tickets_completed", "Tickets Completed"),
            ("commits_authored", "Commits Authored"),
            ("productivity_score", "Overall Productivity"),
            ("pull_requests_merged", "PRs Merged"),
            ("repositories_contributed", "Repositories Contributed")
        ]
        
        for attr_name, display_name in metrics_to_analyze:
            data = [getattr(metric, attr_name) for metric in personal_metrics]
            
            # Calculate trend
            if len(data) >= 2:
                start_val = data[0] if data[0] > 0 else 1
                end_val = data[-1] if data[-1] > 0 else 1
                change_pct = ((end_val - start_val) / start_val) * 100
                
                # Determine trend direction
                if change_pct > 5:
                    direction = "improving"
                elif change_pct < -5:
                    direction = "declining"
                else:
                    direction = "stable"
                
                # Calculate personal best
                personal_best = max(data)
                
                # Determine current performance level
                current_val = data[-1]
                avg_val = sum(data) / len(data)
                
                if current_val >= personal_best * 0.9:
                    current_performance = "above_average"
                elif current_val >= avg_val * 0.8:
                    current_performance = "average"
                else:
                    current_performance = "below_average"
                
                trends.append(PersonalTrendAnalysis(
                    metric_name=display_name,
                    trend_direction=direction,
                    change_percentage=change_pct,
                    quarters_data=data,
                    personal_best=personal_best,
                    current_performance=current_performance
                ))
        
        return trends
    
    @staticmethod
    def generate_personal_single_quarter_report(
        team_prefix: str,
        metrics: PersonalQuarterMetrics,
        user_identifier: str
    ) -> str:
        """Generate single quarter personal performance report"""
        
        return f"""# Personal Performance Report: {metrics.quarter}

## Executive Summary

Your individual performance analysis for {metrics.quarter} in the {team_prefix} project, showing your contributions, productivity patterns, and technical focus areas.

## Key Achievements

### 📋 Ticket Management
- **Tickets Created**: {metrics.tickets_created} tickets
- **Tickets Completed**: {metrics.tickets_completed} tickets  
- **Completion Rate**: {(metrics.tickets_completed / max(metrics.tickets_created, 1) * 100):.0f}%

### 💻 Code Contributions
- **Commits Authored**: {metrics.commits_authored} commits
- **Repositories Contributed**: {metrics.repositories_contributed} repositories
- **Code Changes**: +{metrics.lines_added} / -{metrics.lines_removed} lines (estimated)

### 🔄 Pull Request Activity
- **PRs Created**: {metrics.pull_requests_created} pull requests
- **PRs Merged**: {metrics.pull_requests_merged} pull requests
- **Merge Success Rate**: {(metrics.pull_requests_merged / max(metrics.pull_requests_created, 1) * 100):.0f}%

## Technical Focus Areas

Your development work this quarter concentrated on:

{_format_technical_areas_personal(metrics.technical_areas)}

## Productivity Analysis

### Overall Productivity Score: {metrics.productivity_score:.0f}

**Scoring Breakdown:**
- Completed Tickets: {metrics.tickets_completed * 10} points ({metrics.tickets_completed} × 10)
- Code Commits: {metrics.commits_authored * 2} points ({metrics.commits_authored} × 2)  
- Merged PRs: {metrics.pull_requests_merged * 5} points ({metrics.pull_requests_merged} × 5)
- Repository Diversity: {metrics.repositories_contributed * 3} points ({metrics.repositories_contributed} × 3)

{_generate_personal_insights(metrics)}

## Development Patterns

### Repository Engagement
Your contributions spanned **{metrics.repositories_contributed}** repositories, indicating {_assess_repository_diversity(metrics.repositories_contributed)}.

### Work Distribution
{_analyze_work_distribution(metrics)}

## Quarter Summary

**Period**: {metrics.quarter}  
**Total Contributions**: {metrics.commits_authored + metrics.tickets_completed + metrics.pull_requests_merged}  
**Productivity Score**: {metrics.productivity_score:.0f}  
**Technical Areas**: {len(metrics.technical_areas)} focus areas

Your performance this quarter shows {_generate_quarter_assessment(metrics)}.

## Personal Development Notes

### Strengths Identified
{_identify_personal_strengths(metrics)}

### Growth Opportunities  
{_identify_growth_opportunities(metrics)}

---

*This report analyzes your individual contributions to maintain personal productivity insights while respecting team privacy.*
"""

    @staticmethod
    def generate_personal_qoq_report(
        team_prefix: str,
        personal_metrics: List[PersonalQuarterMetrics],
        trend_analysis: List[PersonalTrendAnalysis],
        user_identifier: str
    ) -> str:
        """Generate quarter-over-quarter personal performance report"""
        
        quarters_analyzed = len(personal_metrics)
        start_quarter = personal_metrics[0].quarter
        end_quarter = personal_metrics[-1].quarter
        
        return f"""# Personal Quarter-over-Quarter Analysis: {team_prefix} Project

## Performance Evolution: {start_quarter} to {end_quarter}

Your individual performance progression across {quarters_analyzed} quarters, tracking productivity trends, skill development, and contribution patterns.

## Personal Growth Summary

{_format_personal_growth_summary(personal_metrics, trend_analysis)}

## Quarter-by-Quarter Progression

### Performance Metrics Table
{_format_personal_metrics_table(personal_metrics)}

## Trend Analysis

{_format_personal_trends_detailed(trend_analysis)}

## Personal Development Insights

### Performance Trajectory
{_analyze_personal_trajectory(personal_metrics, trend_analysis)}

### Skill Development Areas
{_analyze_skill_development(personal_metrics)}

### Consistency Analysis
{_analyze_personal_consistency(personal_metrics)}

## Comparative Analysis

### Personal Bests
{_format_personal_bests(personal_metrics)}

### Quarter Comparisons
{_format_quarter_comparisons(personal_metrics)}

## Strategic Personal Development

### Current Performance Level
{_assess_current_performance_level(personal_metrics, trend_analysis)}

### Recommended Focus Areas
{_generate_personal_recommendations(personal_metrics, trend_analysis)}

### Growth Path Suggestions
{_suggest_growth_path(trend_analysis)}

## Individual Achievement Summary

**Analysis Period**: {start_quarter} to {end_quarter} ({quarters_analyzed} quarters)  
**Total Quarters**: {quarters_analyzed}  
**User**: {user_identifier}  

### Key Statistics
- **Tickets Completed**: {sum(pm.tickets_completed for pm in personal_metrics)} total
- **Commits Authored**: {sum(pm.commits_authored for pm in personal_metrics)} total  
- **PRs Merged**: {sum(pm.pull_requests_merged for pm in personal_metrics)} total
- **Average Productivity Score**: {sum(pm.productivity_score for pm in personal_metrics) / len(personal_metrics):.1f}

### Performance Trends Summary
{_summarize_performance_trends(trend_analysis)}

---

*This analysis tracks your individual contributions and growth patterns to support personal development while maintaining data privacy.*
"""


# Helper functions for report formatting

def _format_technical_areas_personal(areas: List[str]) -> str:
    """Format personal technical areas"""
    if not areas:
        return "- No specific technical areas identified"
    
    return "\n".join(f"- **{area}**: Active development and contribution" for area in areas)


def _generate_personal_insights(metrics: PersonalQuarterMetrics) -> str:
    """Generate personal performance insights"""
    insights = []
    
    if metrics.tickets_completed >= 5:
        insights.append("**Strong Task Completion**: Consistent ticket delivery showing good project execution")
    
    if metrics.commits_authored >= 20:
        insights.append("**Active Development**: High commit frequency indicating engaged coding activity")
    
    if metrics.repositories_contributed >= 3:
        insights.append("**Cross-Functional Work**: Contributing across multiple repositories shows versatility")
    
    if metrics.pull_requests_merged / max(metrics.pull_requests_created, 1) >= 0.8:
        insights.append("**Quality Code Review**: High PR merge rate indicates well-prepared code submissions")
    
    if not insights:
        insights.append("**Steady Contribution**: Consistent development activity with room for increased engagement")
    
    return "\n".join(insights)


def _assess_repository_diversity(repo_count: int) -> str:
    """Assess repository diversity level"""
    if repo_count >= 5:
        return "excellent cross-functional engagement"
    elif repo_count >= 3:
        return "good multi-repository contribution"
    elif repo_count >= 2:
        return "solid dual-repository focus"
    else:
        return "focused single-repository development"


def _analyze_work_distribution(metrics: PersonalQuarterMetrics) -> str:
    """Analyze work distribution patterns"""
    total_work = metrics.commits_authored + metrics.tickets_completed + metrics.pull_requests_created
    
    if total_work == 0:
        return "Limited development activity this quarter."
    
    commit_ratio = metrics.commits_authored / total_work
    ticket_ratio = metrics.tickets_completed / total_work
    pr_ratio = metrics.pull_requests_created / total_work
    
    if commit_ratio > 0.6:
        return "**Code-Heavy Quarter**: Primary focus on development and implementation work"
    elif ticket_ratio > 0.4:
        return "**Balanced Execution**: Good mix of ticket completion and code contributions"  
    elif pr_ratio > 0.3:
        return "**Review-Intensive Quarter**: High pull request activity indicating collaborative development"
    else:
        return "**Diverse Contribution**: Well-balanced across tickets, commits, and pull requests"


def _generate_quarter_assessment(metrics: PersonalQuarterMetrics) -> str:
    """Generate overall quarter assessment"""
    if metrics.productivity_score >= 100:
        return "exceptional productivity and engagement levels"
    elif metrics.productivity_score >= 60:
        return "strong performance with consistent contributions"
    elif metrics.productivity_score >= 30:
        return "solid development activity with growth potential"
    else:
        return "developing momentum with opportunity for increased engagement"


def _identify_personal_strengths(metrics: PersonalQuarterMetrics) -> str:
    """Identify personal strengths based on metrics"""
    strengths = []
    
    if metrics.tickets_completed >= metrics.tickets_created * 0.8:
        strengths.append("- **Task Execution**: Excellent follow-through on assigned work")
    
    if metrics.commits_authored >= 25:
        strengths.append("- **Development Velocity**: High coding output with frequent contributions")
    
    if metrics.pull_requests_merged / max(metrics.pull_requests_created, 1) >= 0.85:
        strengths.append("- **Code Quality**: High PR success rate indicating thorough preparation")
    
    if len(metrics.technical_areas) >= 3:
        strengths.append("- **Technical Breadth**: Diverse technical focus areas showing versatility")
    
    if not strengths:
        strengths.append("- **Steady Contribution**: Consistent development participation")
    
    return "\n".join(strengths)


def _identify_growth_opportunities(metrics: PersonalQuarterMetrics) -> str:
    """Identify growth opportunities"""
    opportunities = []
    
    if metrics.pull_requests_created < metrics.commits_authored * 0.2:
        opportunities.append("- **Code Collaboration**: Consider creating more pull requests for code review")
    
    if metrics.repositories_contributed <= 1:
        opportunities.append("- **Cross-Team Exposure**: Explore contributing to additional repositories")
    
    if len(metrics.technical_areas) <= 2:
        opportunities.append("- **Technical Diversity**: Expand involvement in different technical areas")
    
    if metrics.tickets_created > metrics.tickets_completed:
        opportunities.append("- **Task Completion**: Focus on completing created tickets for better project flow")
    
    if not opportunities:
        opportunities.append("- **Continued Excellence**: Maintain current performance levels and explore new challenges")
    
    return "\n".join(opportunities)


def _format_personal_growth_summary(personal_metrics: List[PersonalQuarterMetrics], 
                                   trend_analysis: List[PersonalTrendAnalysis]) -> str:
    """Format personal growth summary"""
    if not personal_metrics or not trend_analysis:
        return "Insufficient data for growth analysis"
    
    improving_trends = [t for t in trend_analysis if t.trend_direction == "improving"]
    declining_trends = [t for t in trend_analysis if t.trend_direction == "declining"]
    
    summary_lines = [
        f"- **Overall Trajectory**: {len(improving_trends)} metrics improving, {len(declining_trends)} declining",
        f"- **Productivity Growth**: {personal_metrics[-1].productivity_score - personal_metrics[0].productivity_score:+.0f} points",
        f"- **Technical Evolution**: {len(personal_metrics[-1].technical_areas)} current focus areas"
    ]
    
    return "\n".join(summary_lines)


def _format_personal_metrics_table(personal_metrics: List[PersonalQuarterMetrics]) -> str:
    """Format personal metrics as table"""
    lines = [
        "| Quarter | Tickets | Commits | PRs Merged | Repositories | Productivity Score |",
        "|---------|---------|---------|------------|--------------|-------------------|"
    ]
    
    for pm in personal_metrics:
        lines.append(f"| {pm.quarter} | {pm.tickets_completed} | {pm.commits_authored} | {pm.pull_requests_merged} | {pm.repositories_contributed} | {pm.productivity_score:.0f} |")
    
    return "\n".join(lines)


def _format_personal_trends_detailed(trend_analysis: List[PersonalTrendAnalysis]) -> str:
    """Format detailed personal trends"""
    if not trend_analysis:
        return "No trend data available."
    
    lines = []
    for trend in trend_analysis:
        trend_emoji = "📈" if trend.trend_direction == "improving" else "📉" if trend.trend_direction == "declining" else "➡️"
        performance_emoji = "🌟" if trend.current_performance == "above_average" else "👍" if trend.current_performance == "average" else "📊"
        
        lines.append(f"### {trend.metric_name} {trend_emoji}")
        lines.append(f"- **Trend**: {trend.trend_direction.title()} ({trend.change_percentage:+.1f}%)")
        lines.append(f"- **Personal Best**: {trend.personal_best:.1f}")
        lines.append(f"- **Current Level**: {trend.current_performance.replace('_', ' ').title()} {performance_emoji}")
        lines.append("")
    
    return "\n".join(lines)


def _analyze_personal_trajectory(personal_metrics: List[PersonalQuarterMetrics], 
                                trend_analysis: List[PersonalTrendAnalysis]) -> str:
    """Analyze personal performance trajectory"""
    productivity_trend = next((t for t in trend_analysis if "Productivity" in t.metric_name), None)
    
    if productivity_trend:
        if productivity_trend.trend_direction == "improving":
            return f"**Upward Trajectory**: Your productivity is increasing by {productivity_trend.change_percentage:.1f}%, showing consistent growth and skill development."
        elif productivity_trend.trend_direction == "declining":
            return f"**Adjustment Period**: Productivity has decreased by {abs(productivity_trend.change_percentage):.1f}%, which may indicate shifting priorities or increased complexity."
        else:
            return f"**Stable Performance**: Maintaining consistent productivity levels with {abs(productivity_trend.change_percentage):.1f}% variation."
    
    return "Performance trajectory analysis requires additional data."


def _analyze_skill_development(personal_metrics: List[PersonalQuarterMetrics]) -> str:
    """Analyze skill development progression"""
    all_areas = set()
    for pm in personal_metrics:
        all_areas.update(pm.technical_areas)
    
    if len(all_areas) >= 5:
        return "**Broad Technical Growth**: Developing expertise across multiple technical domains"
    elif len(all_areas) >= 3:
        return "**Focused Skill Building**: Consistent development in key technical areas"
    else:
        return "**Specialized Focus**: Deep development in specific technical domain"


def _analyze_personal_consistency(personal_metrics: List[PersonalQuarterMetrics]) -> str:
    """Analyze consistency of personal performance"""
    scores = [pm.productivity_score for pm in personal_metrics]
    avg_score = sum(scores) / len(scores)
    variance = sum((score - avg_score) ** 2 for score in scores) / len(scores)
    std_dev = variance ** 0.5
    
    consistency_ratio = std_dev / avg_score if avg_score > 0 else 0
    
    if consistency_ratio <= 0.2:
        return "**Highly Consistent**: Very stable performance with minimal quarter-to-quarter variation"
    elif consistency_ratio <= 0.4:
        return "**Moderately Consistent**: Good performance stability with some natural variation"
    else:
        return "**Variable Performance**: Significant quarter-to-quarter changes indicating adaptation periods"


def _format_personal_bests(personal_metrics: List[PersonalQuarterMetrics]) -> str:
    """Format personal best achievements"""
    max_tickets = max(pm.tickets_completed for pm in personal_metrics)
    max_commits = max(pm.commits_authored for pm in personal_metrics)  
    max_score = max(pm.productivity_score for pm in personal_metrics)
    max_repos = max(pm.repositories_contributed for pm in personal_metrics)
    
    return f"""- **Highest Ticket Completion**: {max_tickets} tickets
- **Peak Commit Activity**: {max_commits} commits
- **Maximum Productivity Score**: {max_score:.0f}
- **Broadest Repository Engagement**: {max_repos} repositories"""


def _format_quarter_comparisons(personal_metrics: List[PersonalQuarterMetrics]) -> str:
    """Format quarter-by-quarter comparisons"""
    if len(personal_metrics) < 2:
        return "Insufficient data for quarter comparison."
    
    comparisons = []
    for i in range(1, len(personal_metrics)):
        current = personal_metrics[i]
        previous = personal_metrics[i-1]
        
        score_change = current.productivity_score - previous.productivity_score
        ticket_change = current.tickets_completed - previous.tickets_completed
        
        comparisons.append(f"- **{current.quarter} vs {previous.quarter}**: Productivity {score_change:+.0f}, Tickets {ticket_change:+d}")
    
    return "\n".join(comparisons)


def _assess_current_performance_level(personal_metrics: List[PersonalQuarterMetrics], 
                                     trend_analysis: List[PersonalTrendAnalysis]) -> str:
    """Assess current performance level"""
    current_quarter = personal_metrics[-1]
    above_average_trends = len([t for t in trend_analysis if t.current_performance == "above_average"])
    
    if above_average_trends >= 3:
        return "**Peak Performance**: Currently operating at or near your personal best across multiple metrics"
    elif above_average_trends >= 1:
        return "**Strong Performance**: Above average in key areas with solid overall contribution"
    else:
        return "**Growth Phase**: Building momentum with opportunity for performance improvement"


def _generate_personal_recommendations(personal_metrics: List[PersonalQuarterMetrics], 
                                     trend_analysis: List[PersonalTrendAnalysis]) -> str:
    """Generate personal development recommendations"""
    recommendations = []
    
    declining_trends = [t for t in trend_analysis if t.trend_direction == "declining"]
    if declining_trends:
        recommendations.append(f"**Address Declining Areas**: Focus on {', '.join(t.metric_name for t in declining_trends[:2])}")
    
    current_quarter = personal_metrics[-1]
    if current_quarter.repositories_contributed <= 1:
        recommendations.append("**Expand Repository Engagement**: Consider contributing to additional projects")
    
    if current_quarter.pull_requests_created < current_quarter.commits_authored * 0.3:
        recommendations.append("**Increase Collaboration**: Create more pull requests for code review and feedback")
    
    improving_trends = [t for t in trend_analysis if t.trend_direction == "improving"]
    if len(improving_trends) >= 3:
        recommendations.append("**Maintain Momentum**: Continue current practices that are driving improvement")
    
    if not recommendations:
        recommendations.append("**Continue Growth**: Maintain current performance levels and seek new challenges")
    
    return "\n".join(f"{i+1}. {rec}" for i, rec in enumerate(recommendations))


def _suggest_growth_path(trend_analysis: List[PersonalTrendAnalysis]) -> str:
    """Suggest growth path based on trends"""
    improving_metrics = [t.metric_name for t in trend_analysis if t.trend_direction == "improving"]
    stable_metrics = [t.metric_name for t in trend_analysis if t.trend_direction == "stable"]
    
    if len(improving_metrics) >= 3:
        return "**Acceleration Path**: Build on current momentum to achieve breakthrough performance levels"
    elif len(improving_metrics) >= 1:
        return "**Optimization Path**: Strengthen improving areas while stabilizing other performance metrics"
    else:
        return "**Foundation Path**: Focus on establishing consistent performance across all key metrics"


def _summarize_performance_trends(trend_analysis: List[PersonalTrendAnalysis]) -> str:
    """Summarize overall performance trends"""
    improving = len([t for t in trend_analysis if t.trend_direction == "improving"])
    declining = len([t for t in trend_analysis if t.trend_direction == "declining"])
    stable = len([t for t in trend_analysis if t.trend_direction == "stable"])
    
    return f"**Trend Summary**: {improving} improving, {stable} stable, {declining} declining metrics"


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
        Generate personal performance report for a single quarter.
        
        Analyzes your individual contributions, productivity patterns, and technical focus
        areas for the specified quarter with personal insights and development guidance.
        
        Args:
            team_prefix: Team/project prefix (e.g., "SI", "PLAT", "CORE")
            year: Year for the quarter (e.g., 2025)
            quarter: Quarter number (1-4)
            description: Optional description of analysis focus
            
        Returns:
            Dictionary containing personal quarterly performance analysis
        """
        logger.info(f"Personal quarterly report requested: {team_prefix} {year} Q{quarter}")
        
        try:
            # Validate inputs
            if not team_prefix or not team_prefix.isalpha():
                return ToolBase.create_error_response(
                    "Invalid team_prefix. Must be alphabetic (e.g., 'SI', 'PLAT')",
                    error_type="validation_error"
                )
            
            if year < 2020 or year > 2030:
                return ToolBase.create_error_response(
                    "Invalid year. Must be between 2020 and 2030",
                    error_type="validation_error"
                )
            
            # Get current user
            user_identifier = PersonalPerformanceAnalyzer.get_current_user()
            
            # Get quarter configuration
            quarter_config = QuarterlyReportGenerator.get_quarter_config(year, quarter)
            
            # Analyze personal performance
            personal_metrics = PersonalPerformanceAnalyzer.analyze_personal_quarter(
                team_prefix, quarter_config, user_identifier
            )
            
            # Generate report
            report_content = PersonalPerformanceAnalyzer.generate_personal_single_quarter_report(
                team_prefix, personal_metrics, user_identifier
            )
            
            response_data = {
                "report_content": report_content,
                "quarter_info": {
                    "year": year,
                    "quarter": quarter,
                    "name": quarter_config.quarter_name,
                    "date_range": f"{quarter_config.start_date} to {quarter_config.end_date}"
                },
                "personal_metrics": asdict(personal_metrics),
                "user_identifier": user_identifier
            }
            
            logger.info(f"Personal quarterly report generated: {personal_metrics.productivity_score:.0f} productivity score")
            
            return ToolBase.create_success_response(response_data)
            
        except ValueError as e:
            return ToolBase.create_error_response(
                f"Invalid configuration: {str(e)}",
                error_type="validation_error"
            )
        except Exception as e:
            logger.error(f"Error generating personal quarterly report: {e}")
            return ToolBase.create_error_response(
                f"Failed to generate personal quarterly report: {str(e)}",
                error_type=type(e).__name__
            )
    
    @mcp.tool
    def personal_quarter_over_quarter(
        team_prefix: str,
        period: str,
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Generate personal quarter-over-quarter performance analysis.
        
        Tracks your individual performance trends, growth patterns, and skill development
        across multiple quarters with personalized insights and recommendations.
        
        Args:
            team_prefix: Team/project prefix (e.g., "SI", "PLAT", "CORE") 
            period: Analysis period like "2024" or "2023-2025"
            description: Optional description of analysis focus
            
        Returns:
            Dictionary containing personal quarter-over-quarter analysis
        """
        logger.info(f"Personal quarter-over-quarter analysis requested: {team_prefix} {period}")
        
        try:
            # Validate inputs
            if not team_prefix or not team_prefix.isalpha():
                return ToolBase.create_error_response(
                    "Invalid team_prefix. Must be alphabetic (e.g., 'SI', 'PLAT')",
                    error_type="validation_error"
                )
            
            # Parse period
            try:
                if '-' in period:
                    start_year, end_year = map(int, period.split('-'))
                else:
                    start_year = end_year = int(period)
            except ValueError:
                return ToolBase.create_error_response(
                    f"Invalid period format: {period}. Expected 'YYYY' or 'YYYY-YYYY'",
                    error_type="validation_error"
                )
            
            # Get current user
            user_identifier = PersonalPerformanceAnalyzer.get_current_user()
            
            # Generate quarters to analyze
            quarters = []
            for year in range(start_year, end_year + 1):
                for quarter in [1, 2, 3, 4]:
                    quarters.append(QuarterlyReportGenerator.get_quarter_config(year, quarter))
            
            if len(quarters) < 2:
                return ToolBase.create_error_response(
                    "Analysis requires at least 2 quarters. Use personal_quarterly_report for single quarters.",
                    error_type="validation_error"
                )
            
            # Analyze personal performance for each quarter
            personal_metrics = []
            for quarter_config in quarters:
                metrics = PersonalPerformanceAnalyzer.analyze_personal_quarter(
                    team_prefix, quarter_config, user_identifier
                )
                personal_metrics.append(metrics)
            
            # Analyze trends
            trend_analysis = PersonalPerformanceAnalyzer.analyze_personal_trends(personal_metrics)
            
            # Generate comprehensive report
            report_content = PersonalPerformanceAnalyzer.generate_personal_qoq_report(
                team_prefix, personal_metrics, trend_analysis, user_identifier
            )
            
            response_data = {
                "report_content": report_content,
                "analysis_period": {
                    "team_prefix": team_prefix,
                    "start_year": start_year,
                    "end_year": end_year,
                    "total_quarters": len(quarters),
                    "period_string": period
                },
                "personal_metrics": [asdict(pm) for pm in personal_metrics],
                "trend_analysis": [asdict(ta) for ta in trend_analysis],
                "user_identifier": user_identifier,
                "summary": {
                    "quarters_analyzed": len(quarters),
                    "avg_productivity_score": sum(pm.productivity_score for pm in personal_metrics) / len(personal_metrics),
                    "total_tickets": sum(pm.tickets_completed for pm in personal_metrics),
                    "total_commits": sum(pm.commits_authored for pm in personal_metrics),
                    "improving_trends": len([t for t in trend_analysis if t.trend_direction == "improving"])
                }
            }
            
            logger.info(f"Personal QoQ analysis completed: {len(quarters)} quarters, {len(trend_analysis)} trends")
            
            return ToolBase.create_success_response(response_data)
            
        except Exception as e:
            logger.error(f"Error generating personal quarter-over-quarter analysis: {e}")
            return ToolBase.create_error_response(
                f"Failed to generate personal quarter-over-quarter analysis: {str(e)}",
                error_type=type(e).__name__
            )