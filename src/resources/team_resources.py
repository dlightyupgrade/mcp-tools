"""
Team Resources

Provides team-specific configuration, standards, and current metrics.
"""

import fastmcp as mcp
from typing import Dict, List, Optional
from datetime import datetime


class TeamResources:
    """Team configuration and standards resources."""
    
    @staticmethod
    @mcp.resource("team://config/{team_prefix}")
    def get_team_config(team_prefix: str) -> Dict:
        """Get team-specific configuration and development standards."""
        
        team_configs = {
            "SI": {
                "name": "Servicing Infrastructure Team",
                "description": "Personal loan and credit line hardship servicing",
                "jira_project": "SI",
                "github_repos": [
                    "loan-hardship-servicing-srvc",
                    "creditline-hardship-servicing-srvc", 
                    "actor-hardship-srvc",
                    "loan-servicing-srvc"
                ],
                "primary_services": [
                    "loan-hardship-servicing-srvc",
                    "creditline-hardship-servicing-srvc"
                ],
                "tech_stack": {
                    "language": "Java 17",
                    "framework": "Spring Boot",
                    "database": "PostgreSQL",
                    "api_style": "GraphQL",
                    "build_tool": "Maven",
                    "testing": "JUnit 5, AssertJ, MockMVC"
                },
                "coding_standards": {
                    "style_guide": "Google Java Style",
                    "coverage_target": "90%+",
                    "review_requirements": ["security", "performance", "maintainability"],
                    "naming_conventions": "camelCase, descriptive method names",
                    "file_endings": "single newline required"
                },
                "deployment": {
                    "pipeline": "Tekton",
                    "environments": ["local", "stage", "prod"],
                    "container_runtime": "Podman preferred over Docker"
                },
                "review_focus_areas": [
                    "Business logic correctness for hardship calculations",
                    "Data validation for financial transactions", 
                    "Security for PII and payment data",
                    "Integration patterns with Spectrum core services",
                    "Error handling for external service failures"
                ]
            },
            "PLAT": {
                "name": "Platform Team", 
                "description": "Core platform infrastructure and shared services",
                "jira_project": "PLAT",
                "github_repos": [
                    "platform-core",
                    "shared-libraries",
                    "infrastructure-tools"
                ],
                "tech_stack": {
                    "language": "Multiple (Java, Python, Go)",
                    "framework": "Spring Boot, FastAPI",
                    "database": "PostgreSQL, Redis",
                    "api_style": "REST, GraphQL",
                    "build_tool": "Maven, Poetry, Go modules"
                },
                "coding_standards": {
                    "style_guide": "Language-specific standards",
                    "coverage_target": "95%+",
                    "review_requirements": ["security", "scalability", "operational"],
                    "cross_language_consistency": "API design, error handling patterns"
                },
                "review_focus_areas": [
                    "Scalability and performance impact",
                    "Cross-service compatibility",
                    "Infrastructure security",
                    "Operational monitoring and alerting"
                ]
            },
            "CORE": {
                "name": "Core Services Team",
                "description": "Core business services and data management", 
                "jira_project": "CORE",
                "github_repos": [
                    "user-management-srvc",
                    "notification-srvc", 
                    "data-pipeline-srvc"
                ],
                "tech_stack": {
                    "language": "Java 17, Python",
                    "framework": "Spring Boot, FastAPI",
                    "database": "PostgreSQL, MongoDB",
                    "messaging": "Kafka, RabbitMQ"
                },
                "review_focus_areas": [
                    "Data consistency and integrity",
                    "Message processing reliability",
                    "API backward compatibility",
                    "Performance at scale"
                ]
            }
        }
        
        default_config = {
            "name": f"{team_prefix} Team",
            "description": "Development team", 
            "jira_project": team_prefix,
            "github_repos": [],
            "tech_stack": {
                "language": "Java",
                "framework": "Spring Boot",
                "database": "PostgreSQL"
            },
            "coding_standards": {
                "coverage_target": "90%+",
                "review_requirements": ["security", "quality"]
            },
            "review_focus_areas": [
                "Code quality and maintainability",
                "Security best practices",
                "Testing coverage and quality"
            ]
        }
        
        return team_configs.get(team_prefix, default_config)
    
    @staticmethod
    @mcp.resource("team://standards/review-checklist")
    def get_review_checklist() -> Dict:
        """Get comprehensive PR review checklist."""
        
        return {
            "security": {
                "description": "Security-focused review items",
                "checklist": [
                    "Input validation implemented for all user inputs",
                    "SQL injection prevention (parameterized queries)",
                    "Authentication checks present for protected endpoints",
                    "Authorization rules correctly implemented",
                    "Sensitive data properly encrypted/masked",
                    "Error messages don't leak sensitive information",
                    "PII handling complies with privacy requirements",
                    "Audit logging in place for security events"
                ]
            },
            "performance": {
                "description": "Performance and scalability review items",
                "checklist": [
                    "Database queries optimized with proper indexing",
                    "N+1 query problems avoided",
                    "Appropriate caching strategy implemented",
                    "Resource usage reasonable (memory, CPU)",
                    "Async processing used for long-running operations",
                    "Connection pooling and resource management proper",
                    "Load testing considerations addressed",
                    "Monitoring and alerting in place"
                ]
            },
            "maintainability": {
                "description": "Code quality and maintainability review items",
                "checklist": [
                    "Code follows established patterns and conventions",
                    "Single responsibility principle maintained",
                    "Method and class names are descriptive",
                    "Complex business logic is well-documented", 
                    "Error handling is comprehensive and appropriate",
                    "Tests are meaningful and provide good coverage",
                    "Configuration is externalized properly",
                    "Dependencies are minimal and justified"
                ]
            },
            "business_logic": {
                "description": "Business logic correctness review items",
                "checklist": [
                    "Business rules correctly implemented per requirements",
                    "Edge cases and error scenarios handled",
                    "Financial calculations are accurate and tested",
                    "State transitions are valid and properly sequenced", 
                    "Regulatory compliance requirements met",
                    "Data validation covers all business constraints",
                    "Integration points properly tested",
                    "Backward compatibility maintained"
                ]
            }
        }
    
    @staticmethod
    @mcp.resource("team://metrics/current/{team_prefix}")
    async def get_current_metrics(team_prefix: str) -> Dict:
        """Get current team performance metrics (simulated for now)."""
        
        # TODO: Integrate with actual JIRA/GitHub APIs for live data
        # This is a placeholder showing the structure
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        return {
            "team": team_prefix,
            "last_updated": current_date,
            "current_sprint": {
                "sprint_name": f"Sprint {datetime.now().strftime('%Y-%m')}",
                "completed_stories": 12,
                "in_progress": 4,
                "blocked": 1,
                "story_points_completed": 34,
                "velocity_trend": "stable"
            },
            "code_quality": {
                "avg_pr_review_time": "2.1 days",
                "pr_approval_rate": "94%",
                "defect_rate": "low", 
                "test_coverage_avg": "92%",
                "technical_debt_trend": "decreasing"
            },
            "recent_achievements": [
                f"{team_prefix}-8748 hardship validation enhancement completed",
                f"{team_prefix}-8695 performance optimization delivered",
                "Architecture review session completed", 
                "Security audit findings addressed"
            ],
            "active_focus_areas": [
                "Performance optimization",
                "Technical debt reduction",
                "Test automation improvement"
            ],
            "upcoming_milestones": [
                "Q4 feature delivery",
                "Security compliance review",
                "Performance benchmark achievement"
            ]
        }