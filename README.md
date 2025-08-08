# MCP Tools Server

A FastMCP server providing development tools for Claude Code integration.

## Setup

```bash
# Build image
./build.sh

# Start container  
./start.sh

# Add to Claude Code
claude mcp add mcp-tools http://localhost:8002/mcp/ --transport http --scope user
```

## Tools Available (14 Core Tools)

### 1. PR Violations (`pr_violations`)
Analyzes PR violations, open review threads, CI failures, and merge conflicts.

- **Input**: GitHub PR URL, optional description
- **Output**: Detailed analysis instructions for Claude Code execution
- **Example**: `"Use pr_violations tool to analyze this PR: https://github.com/owner/repo/pull/123"`

### 2. Code Review (`code_review`)
Performs comprehensive code quality review.

- **Input**: GitHub PR URL, optional focus area, max diff lines (default: 2000)
- **Output**: Code quality analysis instructions for Claude Code execution
- **Example**: `"Use code_review tool to review this PR with focus on security: https://github.com/owner/repo/pull/123"`

### 3. Tech Design Review (`tech_design_review`)
Reviews technical design documents with architecture analysis.

- **Input**: Confluence URL, GitHub URL, or local file path, optional focus area, design phase
- **Output**: Comprehensive design analysis instructions for Claude Code execution
- **Example**: `"Use tech_design_review tool to analyze this design doc: https://company.atlassian.net/wiki/spaces/TEAM/pages/123456"`

### 4. JIRA Transition (`jira_transition`)
Automates JIRA ticket workflow transitions.

- **Input**: JIRA ticket ID, target state (supports aliases like "dev", "review", "qa", "done"), optional description
- **Output**: JIRA workflow transition instructions for Claude Code execution
- **Example**: `"jt SI-1234 start"` or `"Use jira_transition tool to move SI-1234 to development"`

### 5. Get JIRA Transitions (`get_jira_transitions`)
Calculates transition paths between JIRA statuses.

- **Input**: From status, optional to status (supports preset shortcuts)
- **Output**: Transition path details and step-by-step instructions
- **Shortcuts**: "start"/"dev", "review"/"pr", "qa"/"test", "done"
- **Example**: `"Use get_jira_transitions tool to show the path from Open to In Development"`

### 6. Quarterly Team Report (`quarterly_team_report`)
Generates comprehensive quarterly team performance reports.

- **Input**: Team prefix (e.g., "SI", "PLAT"), year, quarter, optional description
- **Output**: Team analysis instructions using JIRA and GitHub data
- **Example**: `"Use quarterly_team_report tool to generate SI team Q2 2025 report"`

### 7. Quarter-over-Quarter Analysis (`quarter_over_quarter_analysis`)
Analyzes team performance trends across multiple quarters.

- **Input**: Team prefix, period (e.g., "2024" or "2023-2025"), optional description
- **Output**: Multi-quarter trend analysis instructions
- **Example**: `"Use quarter_over_quarter_analysis tool to analyze SI team performance trends for 2024"`

### 8. Personal Quarterly Report (`personal_quarterly_report`)
Generates individual contributor performance reports.

- **Input**: Team prefix, year, quarter, optional description
- **Output**: Personal performance analysis instructions
- **Example**: `"Use personal_quarterly_report tool to generate my Q2 2025 performance report"`

### 9. Personal Quarter-over-Quarter (`personal_quarter_over_quarter`)
Analyzes personal performance trends across multiple quarters.

- **Input**: Team prefix, period (e.g., "2024" or "2023-2025"), optional description
- **Output**: Personal growth trend analysis instructions
- **Example**: `"Use personal_quarter_over_quarter tool to analyze my personal growth trends for 2024"`

### 10. Epic Status Report (`epic_status_report`)
Generates comprehensive epic status reports with sub-task analysis.

- **Input**: Epic ticket ID (e.g., "SI-1234"), optional description for context
- **Output**: Epic and sub-task analysis instructions for comprehensive reporting
- **Features**: Epic progress tracking, sub-task completion analysis, assignee workload distribution

### 11. Setup Prerequisites (`setup_prerequisites`)
Validates and sets up all prerequisites required by MCP Tools.

- **Input**: No parameters required
- **Output**: Comprehensive validation results with setup instructions
- **Features**: GitHub CLI authentication check, JIRA access validation, required tool availability

### 12. Check Tool Requirements (`check_tool_requirements`)
Checks specific prerequisites for a given MCP tool.

- **Input**: Tool name (e.g., "pr_violations", "quarterly_team_report")
- **Output**: Tool-specific validation results with detailed requirements
- **Features**: Tool-specific dependency checking, configuration validation

### 13. Echo (`echo`)
Simple echo for testing MCP connectivity.

- **Example**: `"Use echo tool to test MCP connectivity"`

### 14. Get System Info (`get_system_info`)
System information and server diagnostics.

- **Example**: `"Use get_system_info tool to check server status"`

## Complete Workflow Examples

```bash
# JIRA to implementation workflow
claude "jt SI-1234 start->create branch->read ticket->create a plan to implement ticket spec"

# PR review workflow  
claude "Use pr_violations tool to analyze https://github.com/owner/repo/pull/123->create todo list->fix violations"

# Multi-tool integration
claude "jt SI-8748 start->implement feature->run tests->create PR->jt SI-8748 review->merge->jt SI-8748 done"
```

## Architecture

- **FastMCP Framework**: HTTP Streaming transport (MCP 2025-03-26 specification)
- **Instruction-Based**: All tools return execution instructions for Claude Code
- **Semantic Versioning**: Proper version management with release images
- **Container Ready**: Podman/Docker support with health checks

Server runs on `http://localhost:8002` with endpoints:
- **Health**: `GET /health` - Container health monitoring
- **MCP Protocol**: `POST /mcp/` - Tool execution and streaming (main MCP endpoint)
- **OAuth Discovery**: `GET /.well-known/oauth-authorization-server-mcp` - Authentication metadata
