"""
Service Resources

Provides service-specific configuration, patterns, and domain knowledge.
"""

import fastmcp as mcp
from typing import Dict, List, Optional


class ServiceResources:
    """Service-specific configuration and domain knowledge resources."""
    
    @staticmethod
    @mcp.resource("service://config/{service_name}")
    def get_service_config(service_name: str) -> Dict:
        """Get service-specific configuration and patterns."""
        
        service_configs = {
            "loan-hardship-servicing-srvc": {
                "name": "Loan Hardship Servicing Service",
                "abbreviation": "LHSS",
                "description": "Personal loan hardship program management",
                "domain": "hardship_servicing",
                "business_context": {
                    "primary_functions": [
                        "FEMA deferment processing for disaster-affected areas",
                        "Payment reduction programs for financial hardship",
                        "Loan restructuring for long-term hardship situations"
                    ],
                    "key_entities": [
                        "HardshipEnrollment",
                        "PaymentReductionRequest", 
                        "PaymentDefermentRequest",
                        "LoanAccount",
                        "HardshipPlan"
                    ],
                    "critical_business_rules": [
                        "Hardship eligibility based on account age and payment history",
                        "FEMA zip code validation for disaster deferments",
                        "Payment reduction calculations must maintain loan integrity",
                        "Enrollment and unenrollment state transitions"
                    ]
                },
                "architecture": {
                    "main_modules": [
                        "loan-hardship-servicing-srvc-server (GraphQL API)",
                        "loan-hardship-servicing-srvc-workflow (Argo jobs)"
                    ],
                    "key_packages": [
                        "com.credify.loanhardshipservicing.hardshipprogram",
                        "com.credify.loanhardshipservicing.hardshipUnenrollment",
                        "com.credify.loanhardshipservicing.common.spectrum"
                    ],
                    "integration_points": [
                        "Actor service (borrower information)",
                        "Loan servicing (account operations)",
                        "Spectrum (core loan servicing system)",
                        "Actor bankruptcy service"
                    ]
                },
                "review_focus_areas": [
                    "Hardship calculation accuracy (payment amounts, dates)",
                    "Eligibility validation against business rules",
                    "State transition integrity (enrollment workflows)",
                    "Integration error handling (Spectrum, Actor services)",
                    "FEMA compliance and zip code validation",
                    "Financial impact validation (payment modifications)"
                ],
                "common_patterns": {
                    "strategy_pattern": "HardshipServiceStrategy for different hardship types",
                    "repository_pattern": "Spring Data JPA repositories",
                    "validation_pattern": "Service-layer validation with custom validators",
                    "error_handling": "CfBadRequestException, CfInternalServerException",
                    "async_processing": "Task framework for enrollment processing"
                },
                "testing_patterns": {
                    "unit_tests": "Service layer with mocked dependencies",
                    "integration_tests": "MockMVC for GraphQL endpoints",
                    "fixtures": "Use Fixtures.LOAN_ACCOUNT_NUMBER constants",
                    "validation_tests": "Edge cases and business rule violations"
                }
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
                        "MasterLineBrokerageAccount",
                        "HardshipPlan"
                    ],
                    "critical_business_rules": [
                        "Master line vs sub-line hardship eligibility",
                        "Available balance impact during deferment",
                        "Draw suspension rules during hardship",
                        "Credit line specific payment calculations"
                    ]
                },
                "architecture": {
                    "main_modules": [
                        "creditline-hardship-servicing-srvc-server",
                        "creditline-hardship-servicing-srvc-batch"
                    ],
                    "key_packages": [
                        "com.credify.creditline.hardship.enrollment",
                        "com.credify.creditline.hardship.unenrollment",
                        "com.credify.creditline.hardship.common.spectrum"
                    ],
                    "integration_points": [
                        "Credit line servicing (account management)",
                        "Spectrum (payment services)",
                        "Actor service (customer data)"
                    ]
                },
                "review_focus_areas": [
                    "Master line vs sub-line logic correctness",
                    "Available credit calculations during hardship",
                    "Draw suspension and restoration logic",
                    "Credit line specific payment modifications",
                    "Integration with credit line servicing patterns"
                ]
            },
            "actor-hardship-srvc": {
                "name": "Actor Hardship Service",
                "abbreviation": "AHS",
                "description": "Customer hardship data and eligibility management",
                "domain": "actor_management",
                "business_context": {
                    "primary_functions": [
                        "Customer hardship eligibility tracking",
                        "Hardship history and documentation",
                        "Cross-service hardship coordination"
                    ]
                }
            },
            "loan-servicing-srvc": {
                "name": "Loan Servicing Service", 
                "abbreviation": "LSS",
                "description": "Core personal loan servicing operations",
                "domain": "loan_servicing",
                "business_context": {
                    "primary_functions": [
                        "Loan account management",
                        "Payment processing and allocation",
                        "Interest calculations and fee management",
                        "Account status and lifecycle management"
                    ]
                }
            }
        }
        
        default_config = {
            "name": service_name,
            "description": "Service configuration",
            "domain": "general",
            "review_focus_areas": [
                "Code quality and maintainability",
                "Business logic correctness",
                "Integration patterns",
                "Error handling"
            ]
        }
        
        return service_configs.get(service_name, default_config)
    
    @staticmethod
    @mcp.resource("service://patterns/{service_name}")
    def get_service_patterns(service_name: str) -> Dict:
        """Get service-specific development patterns and best practices."""
        
        # Common patterns across services
        common_patterns = {
            "data_objects": {
                "ato": "Application Transfer Objects - for GraphQL/API layer",
                "sto": "Service Transfer Objects - for internal service communication", 
                "entity": "JPA entities - for database persistence"
            },
            "validation": {
                "service_layer": "Business validation at service boundaries",
                "repository_layer": "Data validation using repository methods",
                "dto_validation": "Input validation on DTOs with annotations"
            },
            "error_handling": {
                "business_errors": "CfBadRequestException for business rule violations",
                "system_errors": "CfInternalServerException for technical failures",
                "error_codes": "Enum-based error codes for consistent messaging"
            },
            "testing": {
                "unit_tests": "Service layer tests with mocked dependencies",
                "integration_tests": "Repository tests with test database",
                "fixtures": "Constants in Fixtures class for test data"
            }
        }
        
        service_specific = {
            "loan-hardship-servicing-srvc": {
                "hardship_strategy": {
                    "pattern": "Strategy pattern for different hardship types",
                    "implementation": "HardshipServiceStrategy interface with ReductionStrategy, DefermentStrategy",
                    "registry": "HardshipServiceStrategyRegistry for strategy selection"
                },
                "validation_architecture": {
                    "three_phases": "Eligibility → Enrollment → Processing validation",
                    "repository_first": "Use repository existence checks before service logic",
                    "boolean_control": "Boolean parameters to control validation phases"
                },
                "jpa_patterns": {
                    "nested_properties": "Use underscore notation (PaymentRequest_StatusIn)",
                    "status_constants": "Use enum-defined status lists",
                    "existence_checks": "Prefer existsBy methods over findBy for boolean validation"
                }
            },
            "creditline-hardship-servicing-srvc": {
                "master_sub_line": {
                    "pattern": "Master line contains sub-lines for credit management",
                    "validation": "Master line eligibility affects all sub-lines",
                    "payment_impact": "Hardship affects available credit calculations"
                },
                "batch_processing": {
                    "pattern": "Separate batch module for scheduled operations",
                    "unenrollment": "Automatic unenrollment when hardship plans complete"
                }
            }
        }
        
        result = {"common_patterns": common_patterns}
        if service_name in service_specific:
            result["service_specific"] = service_specific[service_name]
            
        return result
    
    @staticmethod
    @mcp.resource("service://business-rules/{domain}")
    def get_business_rules(domain: str) -> Dict:
        """Get domain-specific business rules and constraints."""
        
        business_rules = {
            "hardship_servicing": {
                "eligibility_rules": [
                    "Account must be in OPEN status for hardship enrollment",
                    "Minimum account age requirements (typically 120+ days)",
                    "Payment history requirements (no recent delinquencies)",
                    "No active bankruptcy proceedings",
                    "One hardship enrollment per account per period"
                ],
                "deferment_rules": [
                    "Payments suspended for specified period",
                    "Interest may continue to accrue (depending on plan type)",
                    "Account remains in good standing during deferment",
                    "FEMA deferments require zip code verification"
                ],
                "reduction_rules": [
                    "Payment amount reduced but not eliminated",
                    "Loan term may be extended to accommodate reduction", 
                    "Minimum payment thresholds must be maintained",
                    "Interest calculations adjusted for new payment schedule"
                ],
                "unenrollment_rules": [
                    "Automatic unenrollment when hardship period ends",
                    "Manual unenrollment for early completion", 
                    "Payment schedule returns to original terms",
                    "Account status restored to pre-hardship state"
                ]
            },
            "loan_servicing": {
                "payment_rules": [
                    "Payments allocated to fees first, then interest, then principal",
                    "Minimum payment amounts must cover at least interest",
                    "Late fees applied after grace period expires",
                    "Prepayments applied to principal reduction"
                ],
                "account_lifecycle": [
                    "New accounts start in OPEN status",
                    "Delinquency progression based on payment history",
                    "Charge-off after specified delinquency period",
                    "Account closure requires zero balance"
                ]
            }
        }
        
        return business_rules.get(domain, {"rules": ["Domain-specific business rules not defined"]})
    
    @staticmethod
    @mcp.resource("service://architecture/{service_name}")
    def get_architecture_info(service_name: str) -> Dict:
        """Get service architecture and integration information."""
        
        architectures = {
            "loan-hardship-servicing-srvc": {
                "service_type": "Business service with GraphQL API",
                "deployment": "Server module for API, Workflow module for batch processing",
                "database": "PostgreSQL with Liquibase migrations",
                "messaging": "Event-driven architecture for cross-service communication",
                "external_integrations": [
                    {
                        "service": "Actor Service",
                        "purpose": "Customer and borrower information",
                        "integration_type": "GraphQL client"
                    },
                    {
                        "service": "Loan Servicing",
                        "purpose": "Loan account operations and data",
                        "integration_type": "Internal service calls"
                    },
                    {
                        "service": "Spectrum",
                        "purpose": "Core loan servicing system integration",
                        "integration_type": "REST API with WireMock testing"
                    }
                ],
                "key_workflows": [
                    "Hardship eligibility checking",
                    "Hardship plan generation and enrollment",
                    "Batch unenrollment processing",
                    "Payment modification coordination"
                ]
            },
            "creditline-hardship-servicing-srvc": {
                "service_type": "Business service with dual modules",
                "deployment": "Server for real-time API, Batch for scheduled processing",
                "key_differences": [
                    "Master line vs sub-line architecture",
                    "Revolving credit vs fixed-term loan handling",
                    "Available balance impact considerations"
                ]
            }
        }
        
        return architectures.get(service_name, {"architecture": "Standard Spring Boot service"})
    
    @staticmethod
    @mcp.resource("service://review-guidelines/{service_name}")
    def get_service_review_guidelines(service_name: str) -> Dict:
        """Get service-specific review guidelines and focus areas."""
        
        guidelines = {
            "loan-hardship-servicing-srvc": {
                "critical_review_areas": [
                    {
                        "area": "Financial Calculation Accuracy",
                        "description": "Payment modifications must be mathematically correct",
                        "focus_points": [
                            "Payment reduction percentages applied correctly",
                            "Interest recalculation for modified terms",
                            "Fee handling during hardship periods",
                            "Amortization schedule adjustments"
                        ]
                    },
                    {
                        "area": "Eligibility Validation", 
                        "description": "Business rules must be correctly enforced",
                        "focus_points": [
                            "Account status and age requirements",
                            "Payment history validation",
                            "Existing hardship enrollment checks",
                            "Bankruptcy status verification"
                        ]
                    },
                    {
                        "area": "State Management",
                        "description": "Account and enrollment states must remain consistent",
                        "focus_points": [
                            "Enrollment workflow state transitions",
                            "Account status during hardship periods",
                            "Rollback scenarios for failed enrollments",
                            "Concurrent enrollment prevention"
                        ]
                    },
                    {
                        "area": "Integration Reliability",
                        "description": "External service integration must handle failures gracefully",
                        "focus_points": [
                            "Spectrum API error handling",
                            "Actor service timeout scenarios", 
                            "Retry logic for transient failures",
                            "Data consistency across service boundaries"
                        ]
                    }
                ],
                "testing_requirements": [
                    "Unit tests for all business logic with edge cases",
                    "Integration tests for GraphQL endpoints",
                    "Repository tests for complex JPA queries",
                    "Mock external services for isolation"
                ],
                "security_considerations": [
                    "PII protection in hardship documentation",
                    "Financial data encryption and access control",
                    "Audit logging for compliance",
                    "Authorization for hardship operations"
                ]
            },
            "creditline-hardship-servicing-srvc": {
                "critical_review_areas": [
                    {
                        "area": "Master vs Sub-Line Logic",
                        "description": "Credit line hierarchy must be respected",
                        "focus_points": [
                            "Master line eligibility affects all sub-lines",
                            "Available credit calculations during hardship",
                            "Draw suspension and restoration logic"
                        ]
                    },
                    {
                        "area": "Revolving Credit Impacts",
                        "description": "Credit line behavior differs from term loans",
                        "focus_points": [
                            "Available balance modifications",
                            "Interest calculation on revolving balances",
                            "Credit utilization during hardship"
                        ]
                    }
                ]
            }
        }
        
        default_guidelines = {
            "critical_review_areas": [
                {
                    "area": "Business Logic Correctness",
                    "description": "Core business functionality must work correctly",
                    "focus_points": ["Rule validation", "Data processing", "Error handling"]
                }
            ],
            "testing_requirements": [
                "Unit test coverage for business logic",
                "Integration test coverage for APIs"
            ]
        }
        
        return guidelines.get(service_name, default_guidelines)