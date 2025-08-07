#!/usr/bin/env python3
"""
Tech Design Review Tool

Comprehensive technical design document review and improvement tool.
Analyzes technical design documents for architecture, implementation feasibility, 
security, standards compliance, and provides actionable improvement recommendations.
"""

import logging
from typing import Dict, Any
import re
from datetime import datetime

from fastmcp import FastMCP
from .base import ToolBase, get_context_fallback
from config.settings import Config

logger = logging.getLogger(__name__)


def register_tech_design_review_tool(mcp: FastMCP):
    """Register the tech_design_review tool with the FastMCP server"""
    
    @mcp.tool
    def tech_design_review(
        document_url: str, 
        focus_area: str = "comprehensive", 
        design_phase: str = "detailed-design"
    ) -> Dict[str, Any]:
        """
        Perform comprehensive technical design document review - ANALYSIS ONLY.
        
        Provides step-by-step instructions for comprehensive technical design review
        including structure validation, business spec alignment, architecture analysis,
        complexity assessment, and standards compliance checking.
        Does NOT execute analysis directly - returns structured instructions for external execution.
        
        Args:
            document_url: Confluence URL or file path to technical design document
            focus_area: Optional focus area (comprehensive, architecture, security, implementation)
            design_phase: Optional design phase (early-draft, detailed-design, pre-implementation)
            
        Returns:
            Dictionary containing detailed processing instructions for Claude Code execution
        """
        logger.info(f"tech_design_review tool called for: {document_url}")
        
        try:
            # Validate URL format (Confluence or GitHub)
            is_confluence = "credify.atlassian.net" in document_url
            is_github = "github.com" in document_url
            
            if not (is_confluence or is_github or document_url.startswith('/')):
                return ToolBase.create_error_response(
                    "Invalid document URL format. Expected Confluence URL, GitHub URL, or local file path",
                    document_url,
                    "validation_error"
                )
            
            # Extract document components based on URL type
            doc_components = _extract_document_components(document_url)
            
            # Load external context for tech design review
            context_content = ToolBase.load_external_context(
                "/Users/dlighty/code/llm-context/TECH-DESIGN-REVIEW-CONTEXT.md",
                get_context_fallback("tech_design_review")
            )
            
            # Return comprehensive design review instructions
            design_review_analysis = {
                "tool_name": "tech_design_review",
                "analysis_context": "Technical Design Document Review - Comprehensive Analysis and Improvement",
                "timestamp": ToolBase.create_success_response({})["timestamp"],
                "document_url": document_url,
                "focus_area": focus_area,
                "design_phase": design_phase,
                "document_type": "confluence" if is_confluence else "github" if is_github else "local",
                "document_components": doc_components,
                
                "processing_instructions": _get_processing_instructions(doc_components, is_confluence, is_github),
                "required_output_format": _get_output_format(),
                "analysis_requirements": _get_analysis_requirements(),
                "review_categories": _get_review_categories(),
                "external_context": context_content,
                "success_criteria": _get_success_criteria()
            }
            
            logger.info(f"Tech design review instructions generated for: {document_url}")
            return design_review_analysis
            
        except Exception as e:
            logger.error(f"Error generating tech design review instructions: {str(e)}")
            return ToolBase.create_error_response(
                f"Failed to generate tech design review instructions: {str(e)}",
                document_url,
                type(e).__name__
            )


def _extract_document_components(document_url: str) -> Dict[str, str]:
    """Extract components from document URL based on type"""
    components = {}
    
    if "credify.atlassian.net" in document_url:
        # Confluence URL - extract page ID
        page_match = re.search(r'/pages/(\d+)/', document_url)
        if page_match:
            components["page_id"] = page_match.group(1)
        components["type"] = "confluence"
        
    elif "github.com" in document_url:
        # GitHub URL - extract owner, repo, file path
        github_match = re.match(r'https://github\.com/([^/]+)/([^/]+)/blob/[^/]+/(.+)', document_url)
        if github_match:
            components["owner"] = github_match.group(1)
            components["repo"] = github_match.group(2) 
            components["file_path"] = github_match.group(3)
        components["type"] = "github"
        
    else:
        # Local file path
        components["file_path"] = document_url
        components["type"] = "local"
    
    return components


def _get_processing_instructions(doc_components, is_confluence, is_github):
    """Get processing instructions based on document type"""
    instructions = {
        "overview": f"Analyze technical design document with comprehensive review during detailed design phase. Provide comprehensive analysis with actionable improvement recommendations.",
        
        "required_context_retrieval": [
            "**CRITICAL**: Before starting analysis, retrieve required context knowledge:",
            "",
            "1. **Coding Standards Context**: Retrieve from your knowledge base: coding standards, development patterns",
            "   - Alternative: Check for local context files: CODING-STANDARDS.md, DEVELOPMENT-GUIDELINES.md", 
            "   - Required knowledge: Naming conventions, package structure, annotation patterns",
            "",
            "2. **Service Authorization Standards**: Retrieve from your knowledge base: @RunAsService service authorization, login-server scopes",
            "   - Alternative: Check for context files: SERVICE-AUTH.md, AUTHORIZATION-PATTERNS.md",
            "   - Required knowledge: @RunAsService usage, scope configuration patterns, login-server setup",
            "",
            "3. **Architecture Patterns**: Retrieve from your knowledge base: architecture patterns, strategy pattern, service layer", 
            "   - Alternative: Check context files: ARCHITECTURE.md, DESIGN-PATTERNS.md",
            "   - Required knowledge: Strategy pattern usage, service layer standards, integration patterns",
            "",
            "4. **Security Standards**: Retrieve from your knowledge base: PII encryption, security patterns, GraphQL authorization",
            "   - Alternative: Check context files: SECURITY.md, PII-HANDLING.md",
            "   - Required knowledge: PII encryption requirements, authorization check patterns",
            "",
            "5. **Database Standards**: Retrieve from your knowledge base: database migration, liquibase, JPA entity patterns",
            "   - Alternative: Check context files: DATABASE.md, MIGRATION-PATTERNS.md",
            "   - Required knowledge: Entity patterns, migration standards, JPA conventions",
            "",
            "⚠️  **CONTEXT VALIDATION**: If ANY context retrieval fails or returns insufficient information:",
            "   - Document which context areas are missing in review output",
            "   - Mark review as 'PARTIAL - Missing Context' in confidence score",
            "   - Inform user that full evaluation cannot be performed",
            "   - Provide specific guidance on what context is needed",
            "   - Request user to configure their knowledge base or provide context files"
        ],
        
        "phase_1_basic_structure": [
            "1. **Document Access**: Execute appropriate command to fetch document content:",
            f"   - Confluence: mcp__atlassian__getConfluencePage(cloudId='credify.atlassian.net', pageId='{doc_components.get('page_id', 'EXTRACT_FROM_URL')}')" if is_confluence else "",
            f"   - GitHub: gh api 'repos/{doc_components.get('owner', '')}/{doc_components.get('repo', '')}/contents/{doc_components.get('file_path', '')}' --jq '.content' | base64 -d" if is_github else "",
            f"   - Local: Read file directly from path: {doc_components.get('file_path', '')}" if not (is_confluence or is_github) else "",
            "",
            "2. **Basic Structure Review**: Validate document completeness and links",
            "   ✅ Check: Business spec linked? Look for business requirements document link",
            "   ✅ Check: Key parties linked? Validate stakeholder mentions and @mentions", 
            "   ✅ Check: Epic link present? Look for JIRA epic reference (SI-XXXX format)",
            "   ✅ Check: Objective/purpose section exists and is clear?",
            "   ✅ Check: Is this design for whole business spec or partial implementation?",
            "",
            "3. **Business Spec Alignment Verification**: If business spec is linked, fetch and analyze",
            "   - If business doc URL found, execute: mcp__atlassian__getConfluencePage for business spec",
            "   - Compare technical objective with business objective for alignment",
            "   - Identify any gaps between business requirements and technical implementation",
            "   - Verify all business requirements are addressed in technical design",
            "",
            "4. **Service-to-Service Integration Analysis**: Critical authorization pattern review",
            "   ✅ @RunAsService Pattern: Scan design for service-to-service calls",
            "     - Search for external service calls (GraphQL clients, REST calls to other services)",
            "     - Verify all service calls use @RunAsService annotation pattern",
            "     - Example: AccountService calling other services must use @RunAsService",
            "   ✅ New Service Integration: If calling NEW services not used before",
            "     - Identify if this is first time calling a service (Actor, Spectrum, etc.)",
            "     - Check if service-to-service scopes exist in login-server configuration",
            "     - Flag need for login-server application.properties updates",
            "     - Pattern: security.oauth2.resourceserver.scopes.{service-name}={Resource}:{Action}",
            "   ✅ Scope Verification: For existing service integrations",
            "     - Verify existing scopes cover new operations being added",
            "     - Check if new GraphQL queries/mutations need additional scopes",
            "     - Validate scope format matches authorization check definitions"
        ]
    }
    
    return instructions


def _get_output_format():
    """Get the required output format template"""
    return """
## 🎯 Technical Design Review: [DOCUMENT_TITLE]

**Document**: [CONFLUENCE_URL or GITHUB_URL]
**Focus Area**: [comprehensive/architecture/security/implementation]
**Design Phase**: [early-draft/detailed-design/pre-implementation]
**Review Date**: [timestamp]
**Confidence Score**: [0.0-1.0] | **Context Status**: [COMPLETE/PARTIAL/MISSING]
**Overall Grade**: [A+/A/B+/B/C/D/F]

---

### 🧠 **Context Knowledge Validation**
| Knowledge Area | Status | Source | Gap Impact |
|----------------|--------|--------|------------|
| Coding Standards | ✅/⚠️/❌ | [knowledge-base/context-file/missing] | [impact on review quality] |
| Service Authorization | ✅/⚠️/❌ | [knowledge-base/context-file/missing] | [impact on security analysis] |
| Architecture Patterns | ✅/⚠️/❌ | [knowledge-base/context-file/missing] | [impact on design assessment] |
| Security Standards | ✅/⚠️/❌ | [knowledge-base/context-file/missing] | [impact on security review] |
| Database Standards | ✅/⚠️/❌ | [knowledge-base/context-file/missing] | [impact on data modeling] |

**⚠️ Context Gaps**: [List missing context areas that limit review quality]
**📋 Context Setup Help**: [Specific guidance for missing knowledge areas]

---

### 📋 **Basic Structure Review**
| Element | Status | Comments |
|---------|--------|----------|
| Business Spec Linked | ✅/❌ | [link or missing] |
| Key Parties Mentioned | ✅/❌ | [stakeholders identified] |
| Epic Link Present | ✅/❌ | [SI-XXXX or missing] |
| Objective/Purpose Clear | ✅/❌ | [clear/unclear/missing] |
| Scope Definition | ✅/❌ | [full/partial/unclear] |

### 🎯 **Business Alignment Assessment**
- **Objective Match**: [ALIGNED/PARTIAL/MISALIGNED]
- **Requirements Coverage**: [COMPLETE/PARTIAL/GAPS_IDENTIFIED]  
- **Missing Requirements**: [list any gaps found]

### 🏗️ **Architecture & Implementation Analysis**
| Component | Planned Changes | Current State | Assessment |
|-----------|----------------|---------------|------------|
| Database | [new entities/fields] | [analyzed] | ✅/⚠️/❌ |
| Domain Model | [services/DTOs] | [analyzed] | ✅/⚠️/❌ |
| API Layer | [GraphQL/REST] | [analyzed] | ✅/⚠️/❌ |
| Authorization | [new scopes/checks] | [analyzed] | ✅/⚠️/❌ |
| Standards Compliance | [patterns followed] | [verified] | ✅/⚠️/❌ |

### 🔐 **Service-to-Service Authorization Review**
| Component | Status | Action Required |
|-----------|--------|-----------------|
| @RunAsService Usage | ✅/❌ | [all external service calls annotated] |
| New Service Integration | ✅/❌/N/A | [login-server scope configuration needed] |
| Existing Scope Coverage | ✅/❌ | [scopes cover new operations] |
| Login-Server Updates | ✅/❌/N/A | [application.properties changes needed] |

**New Service Scopes Needed**: [list services requiring new scope configuration]
**Login-Server Changes**: [specific application.properties entries needed]

### 🔒 **Security & Data Review**
| Aspect | Assessment | Requirements |
|--------|------------|--------------|
| PII Data Handling | ✅/❌ | [encryption annotations needed] |
| Authorization Checks | ✅/❌ | [GraphQL authorization checks defined] |
| Data Access Patterns | ✅/❌ | [least privilege followed] |

### 🚨 **Critical Issues** ([count])
- [ ] Issue 1: [description with specific fix needed]

### ⚠️ **Important Recommendations** ([count])  
- [ ] Recommendation 1: [specific improvement with rationale]

### 🎯 **Next Actions**
1. **Immediate**: [highest priority action needed]
2. **Before Implementation**: [must-dos before coding begins]
3. **During Development**: [key checkpoints during implementation]

---
**Review Confidence**: [0.0-1.0] | **Overall Grade**: [A+ to F with justification]

## 🔄 **Interactive Design Enhancement**

Your design has been analyzed and specific improvement areas identified. **Let's enhance your design document together!**

**Most Critical Issues to Address:**
1. **Service Authorization Gap** - Missing @RunAsService and login-server scope configuration
2. **Implementation Checklist** - Need concrete development tasks for the team
3. **Sequence Diagrams** - Complex service integration needs visual documentation
4. **Monitoring Strategy** - Launch and operational monitoring plan needed

**💬 Ready to improve your design?** 

**If Context Status = COMPLETE:**
- **"Let's fix 1 and 2 now as they seem most pressing"** - Focus on highest priority issues
- **"Help me add the missing sequence diagrams"** - Create visual documentation 
- **"Let's work on the monitoring strategy"** - Define launch and operational metrics
- **"Review all issues systematically"** - Work through each identified gap

**If Context Status = PARTIAL or MISSING:**
- **"Help me set up the missing context first"** - Configure knowledge base or context files
- **"Let's work with what we have"** - Proceed with partial analysis and note limitations
- **"Show me how to configure my knowledge base"** - Get guidance on knowledge base setup

**🎯 Next Steps**: 
- **Full Context Available**: Tell me which improvements you'd like to tackle first
- **Missing Context**: Let's set up your knowledge base first, or proceed with limited analysis
"""


def _get_analysis_requirements():
    """Get analysis requirements list"""
    return [
        "Fetch document content using appropriate method (Confluence API, GitHub API, or file read)",
        "Validate basic document structure and required sections",
        "Check business spec alignment by fetching linked business document", 
        "Navigate to target repository and analyze current codebase state",
        "Assess architecture changes against existing code patterns",
        "Analyze service-to-service integration patterns and @RunAsService usage",
        "Verify authorization scopes for new or modified service integrations",
        "Check for required login-server application.properties updates",
        "Evaluate complexity appropriateness for problem being solved",
        "Generate confidence score and overall grade with justification",
        "Provide actionable recommendations with specific implementation guidance",
        "Create Claude Code commands for immediate design document improvement",
        "Generate implementation checklists and missing documentation items",
        "Follow Upgrade development standards and coding patterns",
        "Consider worktree project structures for LHSS/CHSS repositories"
    ]


def _get_review_categories():
    """Get review categories configuration"""
    return {
        "basic_structure": {
            "description": "Document completeness, links, and basic organization",
            "priority": "critical",
            "checks": ["business_spec_linked", "stakeholders_identified", "epic_linked", "objective_clear"]
        },
        "business_alignment": {
            "description": "Alignment between business requirements and technical solution",
            "priority": "critical", 
            "checks": ["objective_match", "requirements_coverage", "scope_appropriate"]
        },
        "architecture_analysis": {
            "description": "Technical architecture and implementation feasibility",
            "priority": "high",
            "checks": ["database_changes", "domain_model", "api_changes", "auth_requirements", "standards_compliance"]
        },
        "service_authorization": {
            "description": "Service-to-service authorization and scope configuration",
            "priority": "critical",
            "checks": ["run_as_service_usage", "new_service_scopes", "login_server_updates", "scope_coverage"]
        },
        "security_review": {
            "description": "Security requirements and PII data handling", 
            "priority": "high",
            "checks": ["pii_encryption", "authorization_checks", "data_access_patterns"]
        }
    }


def _get_success_criteria():
    """Get success criteria for the analysis"""
    return {
        "document_access": "Design document content successfully retrieved and parsed",
        "structure_validation": "Basic document structure validated against requirements",
        "business_alignment": "Business spec retrieved and alignment verified",
        "repository_analysis": "Target repository accessed and current state analyzed", 
        "architecture_assessment": "Architecture changes validated against existing codebase",
        "service_authorization": "Service-to-service calls analyzed for @RunAsService and scope requirements",
        "login_server_verification": "Login-server configuration requirements identified for new service integrations",
        "scope_coverage": "Authorization scope coverage verified for existing and new service operations",
        "actionable_recommendations": "Specific, implementable recommendations provided",
        "quality_scoring": "Confidence score and grade assigned with justification"
    }