#!/usr/bin/env python3
"""
Base utilities for MCP tools
"""

import logging
import re
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class ToolBase:
    """Base class for MCP tools with common utilities"""
    
    @staticmethod
    def validate_github_pr_url(pr_url: str) -> Tuple[bool, Optional[Dict[str, str]]]:
        """
        Validate GitHub PR URL and extract components
        
        Returns:
            Tuple of (is_valid, components_dict or None)
        """
        if not pr_url.startswith("https://github.com/") or "/pull/" not in pr_url:
            return False, None
        
        url_match = re.match(r'https://github\.com/([^/]+)/([^/]+)/pull/([0-9]+)', pr_url)
        if not url_match:
            return False, None
        
        owner, repo, pr_number = url_match.groups()
        return True, {
            "owner": owner,
            "repo": repo,
            "pr_number": pr_number
        }
    
    @staticmethod
    def extract_jira_ticket(text: str) -> Optional[str]:
        """Extract JIRA ticket ID from text using regex pattern SI-XXXX"""
        match = re.search(r'SI-\d+', text, re.IGNORECASE)
        return match.group() if match else None
    
    @staticmethod
    def load_external_context(context_file: str, fallback_content: str = "") -> str:
        """Load external context file with fallback"""
        try:
            context_path = Path(context_file)
            if context_path.exists():
                return context_path.read_text()
        except Exception as e:
            logger.warning(f"Failed to load context file {context_file}: {e}")
        
        return fallback_content
    
    @staticmethod
    def create_error_response(error_msg: str, pr_url: str = "", error_type: str = "error") -> Dict[str, Any]:
        """Create standardized error response"""
        response = {
            "error": error_msg,
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "type": error_type
        }
        
        if pr_url:
            response["pr_url"] = pr_url
        
        return response
    
    @staticmethod
    def create_success_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """Create standardized success response"""
        base_response = {
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
        
        return {**base_response, **data}


def get_context_fallback(context_type: str) -> str:
    """Get fallback context content for different tool types"""
    
    fallbacks = {
        "pr_violations": """# PR Violations Analysis Guidelines

## Review Thread Analysis
- Focus on open threads (not resolved, collapsed, or outdated)
- Categorize by urgency: blocking, important, suggestion
- Identify action items vs discussion threads

## Violation Classification
- **Blocking**: Merge conflicts, failed CI, security issues
- **High Priority**: Code quality violations, missing tests
- **Medium Priority**: Style issues, suggestions for improvement  
- **Low Priority**: Discussions, clarifications

## Output Format
```
Violation Summary:
- Open Threads: X (Y blocking, Z important)
- CI Failures: X failed checks
- Merge Status: [READY|CONFLICTS|BLOCKED]
- Action Items: Prioritized list with file:line references
```

## Quality Confidence Scoring
- **A+**: Comprehensive analysis with actionable solutions
- **A**: Solid analysis with clear next steps
- **B+**: Good analysis with minor gaps
- **B**: Adequate analysis, some areas need attention
- **C**: Basic analysis, significant improvements needed
""",
        
        "code_review": """# Code Review Guidelines

## Comprehensive Assessment Areas

### 1. VIOLATIONS ANALYSIS
- Check for "DO NOT MERGE" labels or blocking issues
- Analyze CI status and test failures
- Review merge conflicts or branch protection issues
- Check PR approval status and review requirements

### 2. CODE QUALITY ASSESSMENT
- Review code changes for adherence to standards
- Check import organization and unused imports
- Verify patterns and code structure
- Assess error handling and validation patterns
- Review database query optimization
- Check for hardcoded values vs proper constants

### 3. TEST COVERAGE VERIFICATION
- Analyze test changes and new test coverage
- Check for proper test fixtures usage vs hardcoded values
- Verify unit tests focus on error scenarios
- Validate integration tests cover valid scenarios plus complex errors
- Review test naming and structure patterns

### 4. SECURITY REVIEW
- Check for exposed sensitive data in logs or errors
- Verify input validation and sanitization
- Review authentication/authorization changes
- Check for hardcoded secrets or credentials

### 5. BUSINESS LOGIC COMPLIANCE
- Verify adherence to business constants and patterns
- Check schema changes and synchronization
- Review service integration patterns and error codes
- Validate field naming conventions and type standards

## Assessment Criteria
- **APPROVE**: High quality, no blocking issues, meets requirements
- **REQUEST CHANGES**: Critical issues that block merge
- **COMMENT**: Quality suggestions but no blockers
""",
        
        "tech_design_review": """# Tech Design Review Framework

## Review Phases

### Phase 1: Basic Structure
- Business spec linked and aligned
- Key stakeholders identified
- Epic/JIRA ticket referenced
- Clear objective and scope definition

### Phase 2: Repository Analysis
- Target project identified and accessed
- Current codebase state analyzed
- Planned changes verified against existing patterns

### Phase 3: Architecture Assessment
- Database changes: entities, migrations, relationships
- Domain model: services, DTOs, business logic
- API changes: GraphQL schema, resolvers, authorization
- Standards compliance: patterns, naming, error handling

### Phase 4: Complexity Evaluation
- Problem complexity: SIMPLE/MEDIUM/HIGH
- Solution complexity appropriateness
- Documentation needs: sequence diagrams, flows
- Error handling and edge cases coverage

### Phase 5: Service-to-Service Authorization
- @RunAsService annotation usage for all external service calls
- New service integration scope configuration in login-server
- Existing scope coverage verification for new operations
- Login-server application.properties updates required

### Phase 6: Security & Data Review
- PII data identification and encryption requirements
- Authorization checks and scope requirements
- Data access patterns and security compliance

### Phase 7: Reliability & Async
- TQF usage for async operations and replayability
- Idempotency key patterns and duplicate prevention
- Error handling and retry mechanisms

### Phase 8: Deployment Strategy
- Feature flags and gradual rollout planning
- Launch auditing vs long-term monitoring
- Rollback plans and risk mitigation

## Assessment Criteria
- **Grade A+/A**: Comprehensive, ready for implementation
- **Grade B+/B**: Good foundation, minor improvements needed
- **Grade C/D**: Significant gaps, major revisions required
- **Grade F**: Fundamental issues, complete rework needed
"""
    }
    
    return fallbacks.get(context_type, "")