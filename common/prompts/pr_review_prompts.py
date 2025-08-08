"""
PR Review Prompt Templates

Contextual prompts for different PR review scenarios, roles, and focuses.
"""

import fastmcp as mcp
from typing import Dict, List, Optional


class PRReviewPrompts:
    """PR review prompt templates with role-based and focus-specific guidance."""
    
    @staticmethod
    @mcp.prompt
    def comprehensive_review(
        pr_url: str,
        reviewer_role: str = "senior_engineer",
        service: str = "unknown",
        focus_areas: Optional[List[str]] = None
    ) -> str:
        """Generate comprehensive PR review prompt with role-specific guidance."""
        
        role_perspectives = {
            "senior_engineer": "Focus on code quality, architecture decisions, and technical debt implications",
            "tech_lead": "Evaluate architectural alignment, team standards compliance, and mentoring opportunities", 
            "security_engineer": "Prioritize security vulnerabilities, authentication, authorization, and data protection",
            "platform_engineer": "Assess infrastructure impact, deployment considerations, and operational concerns",
            "product_engineer": "Consider user impact, feature completeness, and business logic correctness"
        }
        
        service_contexts = {
            "loan-hardship-servicing-srvc": "Personal loan hardship programs (LHSS)",
            "creditline-hardship-servicing-srvc": "Credit line hardship programs (CHSS)", 
            "loan-servicing-srvc": "Core loan servicing (LSS)",
            "actor-hardship-srvc": "Actor hardship management",
            "unknown": "General service"
        }
        
        perspective = role_perspectives.get(reviewer_role, role_perspectives["senior_engineer"])
        context = service_contexts.get(service, service_contexts["unknown"])
        
        focus_section = ""
        if focus_areas:
            focus_section = f"\n\n**Priority Focus Areas:**\n" + "\n".join([f"- {area}" for area in focus_areas])
        
        return f"""Review {pr_url} as a {reviewer_role}.

**Service Context:** {context}
**Perspective:** {perspective}

**Review Framework:**
1. **Architecture & Design**
   - Does this change align with service architecture patterns?
   - Are design patterns appropriate for the business domain?
   - Is the change properly scoped and focused?

2. **Code Quality**
   - Is the code readable and maintainable?
   - Are naming conventions consistent with the codebase?
   - Is error handling comprehensive and appropriate?

3. **Business Logic**
   - Does the implementation correctly handle the business requirements?
   - Are edge cases and error scenarios considered?
   - Is the change backward compatible?

4. **Testing & Validation**
   - Are tests comprehensive and meaningful?
   - Is test coverage appropriate for the change?
   - Are integration points properly tested?

5. **Security & Compliance**
   - Are security best practices followed?
   - Is sensitive data properly handled?
   - Are authorization checks in place?{focus_section}

**Deliverable:** Provide specific, actionable feedback with code examples where helpful."""

    @staticmethod
    @mcp.prompt
    def security_focused_review(
        pr_url: str,
        service: str = "unknown",
        threat_model: str = "financial_services"
    ) -> str:
        """Generate security-focused PR review prompt."""
        
        threat_models = {
            "financial_services": [
                "PII data protection and encryption",
                "Authentication and authorization bypass",
                "SQL injection and data manipulation", 
                "Business logic bypass (payment/hardship rules)",
                "Audit trail and compliance requirements"
            ],
            "general": [
                "Input validation and sanitization",
                "Authentication and authorization",
                "Data exposure and leakage",
                "Injection attacks (SQL, XSS, etc.)",
                "Business logic vulnerabilities"
            ]
        }
        
        threats = threat_models.get(threat_model, threat_models["general"])
        threat_list = "\n".join([f"   - {threat}" for threat in threats])
        
        return f"""Security Review: {pr_url}

**Service:** {service}
**Threat Model:** {threat_model}

**Security Assessment Framework:**

🔒 **Primary Threat Vectors:**
{threat_list}

🔍 **Security Checklist:**
1. **Input Validation**
   - All user inputs properly validated and sanitized
   - Type checking and bounds validation implemented
   - SQL injection prevention measures in place

2. **Authentication & Authorization**
   - Proper authentication checks for all endpoints
   - Authorization rules correctly implemented
   - Role-based access control functioning as expected

3. **Data Protection**
   - Sensitive data properly encrypted at rest and in transit
   - PII handling complies with privacy requirements
   - Data exposure minimized in logs and error messages

4. **Business Logic Security**
   - Financial calculations and rules cannot be bypassed
   - State transitions properly validated
   - Race conditions and concurrency issues addressed

5. **Audit & Compliance**
   - Security-relevant actions properly logged
   - Compliance requirements met (financial regulations)
   - Error handling doesn't leak sensitive information

**Focus:** Identify specific security risks and provide remediation recommendations."""

    @staticmethod
    @mcp.prompt
    def architecture_review(
        pr_url: str,
        service: str = "unknown",
        change_type: str = "feature"
    ) -> str:
        """Generate architecture-focused PR review prompt."""
        
        change_contexts = {
            "feature": "new functionality implementation",
            "refactor": "code structure and organization improvements",
            "bugfix": "defect resolution and stability improvements", 
            "performance": "optimization and efficiency improvements",
            "security": "security enhancement or vulnerability fix"
        }
        
        context = change_contexts.get(change_type, change_contexts["feature"])
        
        return f"""Architecture Review: {pr_url}

**Service:** {service}
**Change Type:** {context}

**Architecture Assessment Framework:**

🏗️ **Design Principles:**
1. **Single Responsibility Principle**
   - Each class/method has a clear, single purpose
   - Separation of concerns is maintained
   - Business logic is properly isolated

2. **Design Patterns**
   - Appropriate patterns used (Strategy, Factory, Observer, etc.)
   - Existing architectural patterns followed consistently
   - No anti-patterns introduced

3. **Service Architecture**
   - API design follows RESTful principles
   - Database interactions follow repository patterns
   - Event handling and messaging patterns appropriate

4. **Integration Patterns**
   - External service integration follows established patterns
   - Error handling for external dependencies implemented
   - Circuit breaker and retry patterns where appropriate

5. **Scalability & Performance**
   - Database queries optimized and indexed appropriately
   - Caching strategies implemented where beneficial
   - Async processing used for long-running operations

6. **Maintainability**
   - Code is testable and follows testing patterns
   - Documentation and comments explain complex business logic
   - Configuration is externalized and environment-specific

**Assessment:** Evaluate how well this change fits within the existing architecture and identify any concerns or improvement opportunities."""

    @staticmethod
    @mcp.prompt
    def business_logic_review(
        pr_url: str,
        service: str = "unknown",
        domain: str = "hardship_servicing"
    ) -> str:
        """Generate business logic focused PR review prompt."""
        
        domain_contexts = {
            "hardship_servicing": {
                "key_concepts": [
                    "Hardship plan types (deferment, reduction, FEMA)",
                    "Eligibility rules and validation",
                    "Payment modifications and calculations", 
                    "Enrollment and unenrollment workflows",
                    "Account status and lifecycle management"
                ],
                "critical_areas": [
                    "Financial calculations accuracy",
                    "Eligibility rule correctness",
                    "State transition validity",
                    "Compliance with regulatory requirements"
                ]
            },
            "loan_servicing": {
                "key_concepts": [
                    "Loan account lifecycle",
                    "Payment processing and allocation",
                    "Interest calculations and amortization",
                    "Fee application and management",
                    "Account status transitions"
                ],
                "critical_areas": [
                    "Payment calculation accuracy",
                    "Fee application correctness", 
                    "Account state consistency",
                    "Regulatory compliance"
                ]
            }
        }
        
        context = domain_contexts.get(domain, {
            "key_concepts": ["Business rules and validation", "Data processing workflows"],
            "critical_areas": ["Business logic correctness", "Data consistency"]
        })
        
        concepts_list = "\n".join([f"   - {concept}" for concept in context["key_concepts"]])
        critical_list = "\n".join([f"   - {area}" for area in context["critical_areas"]])
        
        return f"""Business Logic Review: {pr_url}

**Service:** {service}
**Domain:** {domain}

**Business Logic Assessment:**

🧠 **Domain Knowledge Areas:**
{concepts_list}

⚠️ **Critical Assessment Points:**
{critical_list}

**Review Framework:**
1. **Business Rule Correctness**
   - Are business rules implemented according to requirements?
   - Do calculations match expected business formulas?
   - Are edge cases and exceptions properly handled?

2. **Data Validation**
   - Input validation covers all business constraints
   - Data integrity is maintained throughout processing
   - Invalid states are prevented or handled appropriately

3. **Workflow Compliance**
   - Process flows match documented business workflows
   - State transitions are valid and properly sequenced
   - Required approvals and validations are in place

4. **Error Scenarios**
   - Business errors are properly classified and handled
   - User-friendly error messages provide appropriate guidance
   - System maintains consistent state even during failures

5. **Regulatory Compliance**
   - Changes comply with financial services regulations
   - Audit trails are maintained for compliance reporting
   - Data retention and privacy requirements are met

**Focus:** Verify that the business logic correctly implements requirements and handles all scenarios appropriately."""