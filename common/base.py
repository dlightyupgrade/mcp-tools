#!/usr/bin/env python3
"""
Base utilities for MCP tools

This module provides the common base class and utilities used by all MCP tools.
It includes standardized error handling, response formatting, URL validation,
context loading, and JIRA ticket extraction functionality.
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
        
        Args:
            pr_url: GitHub PR URL to validate
            
        Returns:
            Tuple of (is_valid, components_dict or None)
            components_dict contains: owner, repo, pr_number
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
        """
        Extract JIRA ticket ID from text using regex pattern SI-XXXX
        
        Args:
            text: Text to search for JIRA tickets
            
        Returns:
            JIRA ticket ID if found, None otherwise
        """
        match = re.search(r'SI-\d+', text, re.IGNORECASE)
        return match.group() if match else None
    
    @staticmethod
    def load_external_context(context_file: str, fallback_content: str = "") -> str:
        """
        Load external context file with fallback
        
        Args:
            context_file: Path to context file
            fallback_content: Fallback content if file cannot be loaded
            
        Returns:
            Context file content or fallback
        """
        try:
            context_path = Path(context_file)
            if context_path.exists():
                return context_path.read_text()
        except Exception as e:
            logger.warning(f"Failed to load context file {context_file}: {e}")
        
        return fallback_content
    
    @staticmethod
    def create_error_response(error_msg: str, pr_url: str = "", error_type: str = "error") -> Dict[str, Any]:
        """
        Create standardized error response
        
        Args:
            error_msg: Error message
            pr_url: Optional PR URL for context
            error_type: Type of error
            
        Returns:
            Standardized error response dictionary
        """
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
        """
        Create standardized success response
        
        Args:
            data: Response data
            
        Returns:
            Standardized success response dictionary
        """
        base_response = {
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
        
        return {**base_response, **data}


def get_context_fallback(context_type: str) -> str:
    """
    Get fallback context content for different tool types
    
    Args:
        context_type: Type of context to retrieve fallback for
        
    Returns:
        Fallback context content as markdown string
    """
    
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
""",

        "pr_health": """# PR Health Analysis Guidelines

## Health Assessment Categories

### Blocking Issues (🚨)
- Merge conflicts requiring resolution
- Failing CI checks that prevent merge
- Security vulnerabilities requiring immediate attention
- Required approvals missing with "DO NOT MERGE" labels

### High Priority Issues (⚡)
- Code quality violations impacting maintainability  
- Missing test coverage for critical functionality
- Performance issues that could affect system stability
- Breaking changes without proper migration strategy

### Medium Priority Issues (📝)
- Style inconsistencies and code organization
- Refactoring opportunities for technical debt reduction
- Documentation updates needed for public APIs
- Minor test improvements and edge case coverage

### Discussion Threads (💬)
- Design questions and architecture clarifications
- Implementation approach discussions
- Code review learning opportunities
- Best practices and knowledge sharing

## Thread Complexity Assessment
- **SIMPLE**: Explanation needed, comment addition, minor clarification
- **MEDIUM**: Code analysis required, logic explanation, minor refactoring
- **HARD**: Architectural decision, major refactoring, design pattern change

## Analysis Output Format
```
## 🏥 PR Health Analysis: [PR_TITLE]

**Overall Status**: [READY|NEEDS_ATTENTION|BLOCKED]
**Confidence Score**: [0.0-1.0] 
**Quality Grade**: [A+/A/B+/B/C]

### 🚨 Blocking Issues ([count])
- [ ] Issue description with file:line reference

### ⚡ High Priority ([count])  
- [ ] Issue description with file:line reference

### 📝 Medium Priority ([count])
- [ ] Issue description with file:line reference

### 💬 Discussion Threads ([count])
- **Thread 1**: [file:line] - Complexity: [SIMPLE|MEDIUM|HARD]
  - **Question**: [reviewer's question]
  - **Solution**: [terse solution approach]

### 🎯 Next Actions
1. **Address [complexity] thread**: [specific action]
2. **Implement solution**: [concrete steps]
3. **Follow up**: [verification needed]
```

## Quality Scoring Guidelines
- **A+ (0.95-1.0)**: Exceptional analysis with comprehensive solutions
- **A (0.85-0.94)**: Solid analysis with clear actionable items
- **B+ (0.75-0.84)**: Good analysis with minor gaps in coverage
- **B (0.65-0.74)**: Adequate analysis, some areas need attention
- **C (0.50-0.64)**: Basic analysis with significant improvement needed
""",

        "jira_transition": """# JIRA Transition Guidelines

## Workflow State Mapping

### Common State Aliases
- **dev/start/begin** → "In Development"
- **review/pr/codereview** → "Ready For Codereview"  
- **qa/test/validation** → "Ready for Validation"
- **done/resolved/complete** → "Resolved"
- **blocked/block** → "Blocked"
- **open/reopen** → "Open"

### Standard Transition Paths
1. **Open** → **Definition** → **Ready for Eng** → **In Development**
2. **In Development** → **Ready For Codereview**
3. **Ready For Codereview** → **Ready for Validation**
4. **Ready for Validation** → **In Validation** → **Resolved**

### Multi-Step Path Handling
For transitions requiring multiple steps (e.g., Open → In Development):
1. Calculate shortest path using workflow knowledge
2. Execute transitions sequentially with validation
3. Provide clear step-by-step execution plan

## Error Handling
- **Invalid Status**: Provide available transitions from current state
- **Permission Denied**: Check user permissions and suggest alternatives
- **Workflow Violation**: Explain required intermediate steps

## Output Format
```
Transition: [CURRENT_STATE] → [TARGET_STATE]
Path: [STATE1] → [STATE2] → [STATE3]
Steps: [number] step(s)
Commands:
  1. atlassian_transition_issue(ticket_id, transition_id_1)
  2. atlassian_transition_issue(ticket_id, transition_id_2)
Status: [SUCCESS|FAILED|VALIDATION_NEEDED]
```
""",

        "epic_status": """# Epic Status Report Guidelines

## Report Structure

### Executive Summary
- Epic progress percentage and completion timeline
- Key accomplishments in current sprint/period
- Critical blockers requiring leadership attention
- Resource allocation and team coordination status

### Current Sprint Focus
- Active tickets in current sprint with status breakdown
- Sprint goal alignment and delivery confidence
- Resource bottlenecks and capacity planning
- Dependencies blocking sprint completion

### Lagging Items Analysis
- Stalled tickets with root cause identification
- Overdue items requiring escalation
- Technical debt items impacting velocity
- Cross-team dependency resolution needs

### Team Coordination
- Assignee workload distribution and balance
- Communication needs and ping lists
- Knowledge sharing and collaboration gaps
- Skill development and training requirements

### Risk Assessment
- Technical risks affecting delivery timeline
- Resource risks and mitigation strategies
- Dependency risks from external teams
- Quality risks requiring additional validation

## Analysis Categories

### Ticket Status Classification
- **On Track**: Progressing according to timeline
- **At Risk**: Minor delays, recoverable with focus
- **Blocked**: Requires intervention to proceed
- **Stalled**: No recent activity, needs attention

### Priority Levels
- **P0**: Critical blockers stopping all progress
- **P1**: Major issues affecting sprint goals
- **P2**: Important items affecting quality/timeline
- **P3**: Nice-to-have improvements and optimizations

### Team Communication Formats
- **Ping Lists**: @username action items with specific asks
- **Status Updates**: Executive summary for leadership
- **Technical Details**: Implementation specifics for developers
- **Project Management**: Timeline and resource analysis

## Output Templates

### Team Lead Summary
```
## Epic [EPIC_ID] Status - Week of [DATE]

**Overall Progress**: [X]% complete ([Y] of [Z] story points)
**Sprint Status**: [ON_TRACK|AT_RISK|BLOCKED]
**Key Accomplishments**: [bullet points]
**Critical Issues**: [blockers requiring attention]
**Next Week Focus**: [priority items]

**Team Ping List**: @user1 (action), @user2 (review), @user3 (unblock)
```

### Executive Report
```
**Epic**: [TITLE] - [X]% Complete
**Delivery**: [timeline status and confidence level]
**Resources**: [team allocation and capacity analysis]
**Risks**: [critical blockers and mitigation plans]
**Actions**: [leadership decisions needed]
```
"""
    }
    
    return fallbacks.get(context_type, "")