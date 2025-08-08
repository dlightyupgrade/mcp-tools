#!/usr/bin/env python3
"""
Enhanced Code Review Analysis Tool

Enhanced PR review with prompts and resources integration.
Provides contextual guidance based on team, service, and role-specific standards.
"""

import logging
import re
from typing import Dict, Any, Optional

from fastmcp import FastMCP
from common.base import ToolBase

logger = logging.getLogger(__name__)


def register_enhanced_code_review_tool(mcp: FastMCP):
    """Register the enhanced_code_review tool with integrated prompts and resources"""
    
    @mcp.tool
    def enhanced_code_review(
        pr_url: str, 
        reviewer_role: str = "senior_engineer",
        focus: str = "comprehensive",
        use_context: bool = True
    ) -> Dict[str, Any]:
        """
        Enhanced code review with contextual prompts and team/service resources.
        
        Provides role-specific guidance, team standards, and service-specific focus areas
        for comprehensive PR analysis. This is the testbed implementation of FastMCP
        prompt and resource integration.
        
        Args:
            pr_url: GitHub PR URL to review
            reviewer_role: Role-based perspective ("senior_engineer", "tech_lead", "security_engineer", "platform_engineer", "product_engineer")
            focus: Review focus ("comprehensive", "security", "architecture", "business_logic", "performance")
            use_context: Include team/service context and resources (default: True)
            
        Returns:
            Enhanced review instructions with integrated prompts and contextual resources
        """
        logger.info(f"enhanced_code_review tool called: {pr_url}, role: {reviewer_role}, focus: {focus}")
        
        try:
            # Validate PR URL
            is_valid, components = ToolBase.validate_github_pr_url(pr_url)
            if not is_valid:
                return ToolBase.create_error_response(
                    "Invalid GitHub PR URL format", pr_url, "validation_error"
                )
            
            owner = components["owner"]
            repo = components["repo"]
            pr_number = components["pr_number"]
            
            # Extract team and service information
            team_prefix = _extract_team_from_repo(repo)
            service_name = repo
            
            # Build enhanced response with integrated prompts and resources
            response = {
                "tool_name": "enhanced_code_review",
                "analysis_context": f"Enhanced PR Review with Contextual Guidance - {focus.title()} Focus",
                "timestamp": ToolBase.create_success_response({})["timestamp"],
                "pr_details": {
                    "url": pr_url,
                    "owner": owner,
                    "repo": repo,
                    "pr_number": pr_number,
                    "service_name": service_name,
                    "team_prefix": team_prefix
                },
                "review_config": {
                    "reviewer_role": reviewer_role,
                    "focus": focus,
                    "context_enabled": use_context
                }
            }
            
            # Generate integrated contextual prompts (embedded instead of separate module)
            response["contextual_prompts"] = _generate_integrated_prompts(
                pr_url, reviewer_role, focus, service_name
            )
            
            # Include integrated team and service resources if context is enabled
            if use_context:
                response["team_context"] = _get_integrated_team_context(team_prefix)
                response["service_context"] = _get_integrated_service_context(service_name)
                response["review_resources"] = _get_integrated_review_resources(service_name, focus)
            
            # Enhanced processing instructions
            response["processing_instructions"] = _create_processing_instructions(
                owner, repo, pr_number, reviewer_role, focus, use_context
            )
            
            return ToolBase.create_success_response(response)
            
        except Exception as e:
            logger.error(f"Enhanced code review failed: {str(e)}")
            return ToolBase.create_error_response(
                "Enhanced code review analysis failed", pr_url, "processing_error"
            )


def _extract_team_from_repo(repo_name: str) -> str:
    """Extract team prefix from repository name."""
    
    # Service to team mapping
    service_to_team = {
        "loan-hardship-servicing-srvc": "SI",
        "creditline-hardship-servicing-srvc": "SI", 
        "actor-hardship-srvc": "SI",
        "loan-servicing-srvc": "SI",
        "platform-core": "PLAT",
        "shared-libraries": "PLAT",
        "infrastructure-tools": "PLAT"
    }
    
    return service_to_team.get(repo_name, "UNKNOWN")


def _generate_integrated_prompts(pr_url: str, reviewer_role: str, focus: str, service_name: str) -> Dict[str, Any]:
    """Generate integrated contextual prompts based on review parameters."""
    
    prompts = {}
    
    # Generate appropriate prompt based on focus
    if focus == "security":
        prompts["security_prompt"] = f"""
Role-Based Security Review for {reviewer_role.replace('_', ' ').title()}

**Security Review Focus for {service_name}**:
- Review {pr_url} with security engineer perspective
- Threat model: {'financial_services' if 'hardship' in service_name else 'general'}
- Focus areas: Input validation, authentication, data protection, API security
- Service-specific concerns: {_get_service_security_concerns(service_name)}

**Analysis Framework**:
1. **Input Validation**: Check all user inputs are properly validated
2. **Authentication/Authorization**: Verify access controls are appropriate
3. **Data Protection**: Ensure sensitive data handling follows standards
4. **Vulnerability Assessment**: Look for common security patterns
5. **Service Integration Security**: Review external service interactions

**Output**: Detailed security analysis with specific file:line references
"""
    elif focus == "architecture":
        prompts["architecture_prompt"] = f"""
Role-Based Architecture Review for {reviewer_role.replace('_', ' ').title()}

**Architecture Review Focus for {service_name}**:
- Review {pr_url} with architecture perspective
- Change type: Feature enhancement
- Service architecture: {_get_service_architecture_notes(service_name)}
- Focus areas: Design patterns, scalability, maintainability

**Analysis Framework**:
1. **Design Patterns**: Evaluate pattern usage and consistency
2. **Service Integration**: Assess external service interactions
3. **Data Flow**: Review data handling and processing
4. **Scalability**: Consider performance and growth implications
5. **Technical Debt**: Identify areas for improvement

**Output**: Architecture assessment with design recommendations
"""
    elif focus == "business_logic":
        domain = "hardship_servicing" if "hardship" in service_name else "loan_servicing"
        prompts["business_logic_prompt"] = f"""
Role-Based Business Logic Review for {reviewer_role.replace('_', ' ').title()}

**Business Logic Review Focus for {service_name}**:
- Review {pr_url} with business domain expertise
- Domain: {domain}
- Business rules: {_get_business_rules_summary(service_name)}
- Focus areas: Rule correctness, edge cases, compliance

**Analysis Framework**:
1. **Business Rule Validation**: Verify rules are correctly implemented
2. **Edge Case Handling**: Check boundary conditions and error scenarios
3. **Domain Model Integrity**: Assess data model consistency
4. **Compliance**: Ensure regulatory requirements are met
5. **Process Flow**: Review workflow and state transitions

**Output**: Business logic assessment with domain-specific insights
"""
    else:
        # Comprehensive review (default)
        prompts["comprehensive_prompt"] = f"""
Role-Based Comprehensive Review for {reviewer_role.replace('_', ' ').title()}

**Comprehensive Review Focus for {service_name}**:
- Review {pr_url} from {reviewer_role.replace('_', ' ')} perspective
- Service context: {_get_service_summary(service_name)}
- Focus areas: {', '.join(_get_focus_areas_for_service(service_name, focus))}

**Analysis Framework**:
1. **Code Quality**: Standards compliance, maintainability, readability
2. **Testing**: Coverage, test quality, edge cases
3. **Performance**: Efficiency, resource usage, scalability
4. **Security**: Input validation, access control, data protection
5. **Business Logic**: Rule correctness, domain model integrity
6. **Integration**: External service interactions, error handling

**Role-Specific Considerations**:
{_get_role_specific_guidance(reviewer_role)}

**Output**: Multi-faceted review with prioritized recommendations
"""
    
    return prompts


def _get_focus_areas_for_service(service_name: str, focus: str) -> list:
    """Get focus areas specific to the service and review focus."""
    
    service_focus_areas = {
        "loan-hardship-servicing-srvc": [
            "Hardship calculation accuracy",
            "Eligibility validation logic",
            "State transition integrity", 
            "Spectrum integration handling"
        ],
        "creditline-hardship-servicing-srvc": [
            "Master vs sub-line logic",
            "Available credit calculations",
            "Draw suspension logic",
            "Credit line specific payments"
        ]
    }
    
    return service_focus_areas.get(service_name, ["Code quality", "Business logic", "Integration patterns"])


def _get_integrated_team_context(team_prefix: str) -> Dict[str, Any]:
    """Get integrated team-specific context and configuration."""
    
    team_configs = {
        "SI": {
            "name": "Servicing Infrastructure Team",
            "description": "Personal loan and credit line hardship servicing",
            "tech_stack": {
                "language": "Java 17",
                "framework": "Spring Boot",
                "database": "PostgreSQL",
                "api_style": "GraphQL"
            },
            "coding_standards": {
                "style_guide": "Google Java Style",
                "coverage_target": "90%+",
                "naming_conventions": "camelCase, descriptive method names"
            },
            "review_focus_areas": [
                "Business logic correctness for hardship calculations",
                "Data validation for financial transactions",
                "Security for PII and payment data",
                "Integration patterns with Spectrum core services"
            ]
        },
        "PLAT": {
            "name": "Platform Team",
            "description": "Core platform infrastructure and shared services",
            "tech_stack": {
                "language": "Multiple (Java, Python, Go)",
                "framework": "Spring Boot, FastAPI",
                "database": "PostgreSQL, Redis"
            },
            "review_focus_areas": [
                "Scalability and performance impact",
                "Cross-service compatibility",
                "Infrastructure security",
                "Operational monitoring"
            ]
        }
    }
    
    config = team_configs.get(team_prefix, {
        "name": f"{team_prefix} Team",
        "description": "Development team",
        "review_focus_areas": ["Code quality", "Security", "Testing"]
    })
    
    review_checklist = {
        "security": ["Input validation", "Authentication checks", "Data encryption"],
        "performance": ["Query optimization", "Caching strategy", "Resource usage"],
        "maintainability": ["Code patterns", "Documentation", "Test coverage"],
        "business_logic": ["Rule correctness", "Edge cases", "Compliance"]
    }
    
    return {
        "config": config,
        "review_checklist": review_checklist,
        "resource_uri": f"team://config/{team_prefix}"
    }


def _get_integrated_service_context(service_name: str) -> Dict[str, Any]:
    """Get integrated service-specific context and patterns."""
    
    service_configs = {
        "loan-hardship-servicing-srvc": {
            "name": "Loan Hardship Servicing Service",
            "abbreviation": "LHSS",
            "description": "Personal loan hardship program management",
            "domain": "hardship_servicing",
            "business_context": {
                "primary_functions": [
                    "FEMA deferment processing",
                    "Payment reduction programs", 
                    "Loan restructuring"
                ],
                "key_entities": [
                    "HardshipEnrollment",
                    "PaymentReductionRequest",
                    "LoanAccount"
                ]
            },
            "review_focus_areas": [
                "Hardship calculation accuracy",
                "Eligibility validation against business rules",
                "State transition integrity",
                "Integration error handling"
            ]
        },
        "creditline-hardship-servicing-srvc": {
            "name": "Credit Line Hardship Servicing Service",
            "abbreviation": "CHSS",
            "description": "Credit line hardship program management",
            "domain": "hardship_servicing",
            "business_context": {
                "primary_functions": [
                    "Credit line deferment processing",
                    "Payment reduction for revolving credit",
                    "FEMA deferment for credit lines"
                ],
                "key_entities": [
                    "CreditlineAccountDetails",
                    "CreditlineHardshipEnrollment",
                    "MasterLineBrokerageAccount"
                ]
            },
            "review_focus_areas": [
                "Master line vs sub-line logic correctness",
                "Available credit calculations",
                "Draw suspension and restoration logic"
            ]
        }
    }
    
    config = service_configs.get(service_name, {
        "name": service_name,
        "description": "Service configuration",
        "domain": "general",
        "review_focus_areas": ["Code quality", "Business logic", "Integration patterns"]
    })
    
    common_patterns = {
        "data_objects": {
            "ato": "Application Transfer Objects - for GraphQL/API layer",
            "sto": "Service Transfer Objects - for internal service communication",
            "entity": "JPA entities - for database persistence"
        },
        "validation": {
            "service_layer": "Business validation at service boundaries",
            "repository_layer": "Data validation using repository methods"
        },
        "error_handling": {
            "business_errors": "CfBadRequestException for business rule violations",
            "system_errors": "CfInternalServerException for technical failures"
        }
    }
    
    return {
        "config": config,
        "patterns": {"common_patterns": common_patterns},
        "resource_uris": [
            f"service://config/{service_name}",
            f"service://patterns/{service_name}"
        ]
    }


def _get_integrated_review_resources(service_name: str, focus: str) -> Dict[str, Any]:
    """Get integrated review-specific resources and references."""
    
    resources = {
        "available_resources": [
            f"team://config/{_extract_team_from_repo(service_name)}",
            f"service://config/{service_name}",
            f"service://patterns/{service_name}",
            f"team://standards/review-checklist"
        ]
    }
    
    # Add focus-specific resources
    if focus == "security":
        resources["security_resources"] = [
            "team://standards/security-checklist",
            "service://business-rules/security"
        ]
    elif focus == "architecture":
        resources["architecture_resources"] = [
            f"service://architecture/{service_name}",
            "team://standards/architecture-patterns"
        ]
    
    return resources


def _get_service_security_concerns(service_name: str) -> str:
    """Get service-specific security concerns for security reviews."""
    
    security_concerns = {
        "loan-hardship-servicing-srvc": "PII handling in hardship data, payment processing security",
        "creditline-hardship-servicing-srvc": "Credit line data protection, financial transaction security",
        "actor-hardship-srvc": "Customer data privacy, identity verification",
        "loan-servicing-srvc": "Loan account security, payment data protection"
    }
    
    return security_concerns.get(service_name, "Standard input validation, authentication checks")


def _get_service_architecture_notes(service_name: str) -> str:
    """Get service-specific architecture patterns and notes."""
    
    architecture_notes = {
        "loan-hardship-servicing-srvc": "Spring Boot microservice, GraphQL API, PostgreSQL persistence, Spectrum integration",
        "creditline-hardship-servicing-srvc": "Spring Boot microservice, GraphQL API, master/sub-line architecture",
        "actor-hardship-srvc": "Spring Boot microservice, customer data management, event-driven architecture",
        "loan-servicing-srvc": "Core loan servicing, payment processing, batch job integration"
    }
    
    return architecture_notes.get(service_name, "Standard Spring Boot microservice architecture")


def _get_business_rules_summary(service_name: str) -> str:
    """Get business rules summary for business logic reviews."""
    
    business_rules = {
        "loan-hardship-servicing-srvc": "FEMA deferment eligibility, payment reduction calculations, hardship program rules",
        "creditline-hardship-servicing-srvc": "Credit line hardship eligibility, available credit calculations, draw suspension rules",
        "actor-hardship-srvc": "Customer eligibility validation, hardship program enrollment rules",
        "loan-servicing-srvc": "Loan payment processing, interest calculations, late fee assessment"
    }
    
    return business_rules.get(service_name, "Standard business validation rules")


def _get_service_summary(service_name: str) -> str:
    """Get service summary for comprehensive reviews."""
    
    service_summaries = {
        "loan-hardship-servicing-srvc": "Personal loan hardship program management and processing",
        "creditline-hardship-servicing-srvc": "Credit line hardship program management with master/sub-line support",
        "actor-hardship-srvc": "Customer and actor data management for hardship programs",
        "loan-servicing-srvc": "Core loan servicing operations and payment processing"
    }
    
    return service_summaries.get(service_name, f"Service: {service_name}")


def _get_role_specific_guidance(reviewer_role: str) -> str:
    """Get role-specific guidance for comprehensive reviews."""
    
    role_guidance = {
        "senior_engineer": "Focus on code quality, maintainability, and technical excellence. Look for design patterns, performance implications, and long-term sustainability.",
        "tech_lead": "Evaluate architectural decisions, team consistency, and technical direction. Consider impact on other teams and services.",
        "security_engineer": "Prioritize security vulnerabilities, data protection, and compliance. Review authentication, authorization, and input validation thoroughly.",
        "platform_engineer": "Assess infrastructure impact, scalability concerns, and operational considerations. Review monitoring, logging, and deployment aspects.",
        "product_engineer": "Focus on business logic correctness, user experience impact, and feature completeness. Ensure requirements are properly implemented."
    }
    
    return role_guidance.get(reviewer_role, "Apply general engineering best practices and code review standards.")


def _create_processing_instructions(
    owner: str, repo: str, pr_number: str, reviewer_role: str, focus: str, use_context: bool
) -> Dict[str, Any]:
    """Create enhanced processing instructions with context integration."""
    
    instructions = {
        "overview": f"""
Enhanced PR Review Analysis with Contextual Guidance

**Review Approach**: {reviewer_role} perspective with {focus} focus
**Context Integration**: {'Enabled' if use_context else 'Disabled'}

This enhanced review leverages:
- Role-specific prompts for targeted analysis
- Team configuration and standards
- Service-specific patterns and business rules
- Contextual resources for comprehensive evaluation
        """.strip(),
        
        "data_extraction_steps": [
            f"Execute: gh api \"repos/{owner}/{repo}/pulls/{pr_number}\" (PR details)",
            f"Execute: gh pr diff {pr_number} --repo {owner}/{repo} (code changes)", 
            f"Execute: gh api \"repos/{owner}/{repo}/pulls/{pr_number}/files\" (files changed)",
            f"Execute: gh api \"repos/{owner}/{repo}/pulls/{pr_number}/reviews\" (existing reviews)",
            "Extract JIRA ticket from PR title/body if present"
        ],
        
        "contextual_analysis_steps": [
            "Apply the provided contextual prompt for role-specific analysis",
            "Reference team configuration for standards compliance",
            "Use service patterns for architecture assessment",
            "Apply service-specific review guidelines",
            "Cross-reference with review checklist items"
        ],
        
        "output_requirements": {
            "format": "Enhanced structured review with contextual insights",
            "sections": [
                "Executive Summary with role-specific assessment",
                "Standards Compliance (team-specific)",
                "Service Pattern Analysis", 
                "Focus Area Deep Dive",
                "Contextual Recommendations",
                "Resource References"
            ]
        },
        
        "quality_gates": [
            "Role-specific concerns addressed",
            "Team standards validated",
            "Service patterns followed",
            "Focus area thoroughly analyzed",
            "Actionable recommendations provided"
        ]
    }
    
    return instructions


# Update the function call in the main tool to use the integrated version
def _update_function_calls():
    """Helper to document the function calls that need to use integrated versions"""
    # This function serves as documentation for the integrated approach:
    # - _generate_integrated_prompts() - embedded prompt templates
    # - _get_integrated_team_context() - embedded team configurations  
    # - _get_integrated_service_context() - embedded service patterns
    # - _get_integrated_review_resources() - embedded resource references
    # - Helper functions for prompt generation with embedded data
    pass