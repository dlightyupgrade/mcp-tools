# CLAUDE.md

This file provides guidance to Claude Code when working with the MCP Tools project.

## Project Information
- **Name**: MCP Tools Server
- **Version**: 2.0.1
- **Type**: Python FastMCP Server (Modular Architecture)
- **Transport**: MCP 2025-03-26 HTTP Streaming (FastMCP)
- **Port**: 8002 (default)
- **Architecture**: Modular FastMCP with dynamic tool registration

## Container Preferences

### ⚠️ IMPORTANT: Use Podman, NOT Docker
**Container Tool**: Always use `podman` instead of `docker` for this project and environment.

**Container Commands**:
```bash
# Build container
podman build -t mcp-tools:latest .

# Run container
podman run --rm -p 8002:8002 -d --name mcp-tools mcp-tools:latest

# Check running containers
podman ps

# Stop container
podman stop mcp-tools

# View logs
podman logs mcp-tools

# Available tags
podman images | grep mcp-tools
```

### Container Configuration
- **Base Image**: python:3.11-slim
- **Port**: 8002 (both host and container)
- **Health Check**: http://localhost:8002/health
- **Format**: OCI (Podman default), not Docker format
- **User**: Non-root user for security
- **Tags**: `latest`
- **Transport**: FastMCP HTTP Streaming

## Port Configuration

### Default Port: 8002
- **HTTP Server**: http://localhost:8002
- **MCP Endpoint**: http://localhost:8002/mcp
- **Health Check**: http://localhost:8002/health
- **Environment Variable**: PORT=8002

### Port Memory/Context
The port 8002 is specifically chosen for MCP Tools to avoid conflicts with:
- **8000**: MCP-RAG production service
- **8001**: ChromaDB (MCP-RAG dependency)
- **8003+**: Future MCP services

## Development Commands

### Build and Run
```bash
# Poetry (Recommended)
poetry install              # Install dependencies
poetry run python mcp_tools_server.py      # Run server

# Alternative development mode
poetry shell                # Activate virtual environment
python mcp_tools_server.py

# Container
podman build -t mcp-tools .
podman run --rm -p 8002:8002 mcp-tools
```

### Testing Endpoints
```bash
# Health check
curl http://localhost:8002/health

# List tools
curl -X POST http://localhost:8002/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'

# Test echo tool
curl -X POST http://localhost:8002/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "echo", "arguments": {"text": "Hello MCP"}}}'
```

## Architecture v2.0 - Single Server with Modular Tools

### Current Architecture 
- **mcp_tools_server.py**: v2.0 single server with modular tool system (PRODUCTION)
- **src/mcp_tools_server.py**: v2.0 source version (same functionality)
- All multi-server composition directories removed (coordinator, tools, reports)

### Modular Components
- **src/mcp_tools_server.py**: Main server with dynamic tool registration
- **src/tools/__init__.py**: Tool registry and loader
- **src/tools/base.py**: Common utilities and base classes
- **src/config/settings.py**: Centralized configuration
- **src/auth/oauth_shell.py**: OAuth authentication layer
- **pyproject.toml**: Python dependencies and configuration

### Individual Tool Files
- **src/tools/pr_violations.py**: PR violation analysis
- **src/tools/code_review.py**: Code quality review
- **src/tools/tech_design_review.py**: Technical design document review
- **src/tools/jira_transition.py**: JIRA workflow transitions
- **src/tools/jira_transitions.py**: JIRA transition calculations
- **src/tools/quarterly_report.py**: Quarterly team performance reports
- **src/tools/quarter_over_quarter.py**: Multi-quarter trend analysis with team size tracking
- **src/tools/personal_performance.py**: Personal performance analysis for individual contributors
- **src/tools/system.py**: System tools (echo, get_system_info)
- **uv.lock**: Locked dependency versions
- **Dockerfile**: Container configuration

### Available Tools
1. **pr_violations**: Analyze PR violations and threads
2. **code_review**: Comprehensive code quality review
3. **tech_design_review**: Technical design document review with architecture analysis
4. **jira_transition**: JIRA ticket workflow transitions with automation
5. **get_jira_transitions**: Calculate transition paths between JIRA statuses (supports multi-step paths + preset shortcuts: "start"/"dev", "review"/"pr", "qa"/"test", "done")
6. **quarterly_team_report**: Generate comprehensive quarterly team performance reports with anonymized metrics
7. **quarter_over_quarter_analysis**: Analyze team performance trends and size changes across multiple quarters
8. **personal_quarterly_report**: Generate individual contributor performance report for a single quarter
9. **personal_quarter_over_quarter**: Analyze personal performance trends and growth across multiple quarters
10. **epic_status_report**: Generate comprehensive epic status reports with sub-task analysis and progress tracking
11. **setup_prerequisites**: Validate and setup all prerequisites required by MCP Tools
12. **check_tool_requirements**: Check specific prerequisites for a given MCP tool
13. **echo**: Simple echo for testing
14. **get_system_info**: System information

## ⚠️ Alpha Development Status

**MCP-Tools is currently in alpha development stage:**

### Alpha Stage Limitations
- **Not Production Ready**: Features and accuracy are not guaranteed
- **Data Validation Required**: All report outputs require manual verification
- **Internal Use Only**: Not suitable for official reporting or business decisions
- **Format Instability**: Report templates and structure may change without notice
- **Incomplete Analysis**: Some metrics and insights may be missing or inaccurate

### Intended Usage Scope
- **Development Testing**: Feature validation and feedback collection
- **Internal Prototyping**: Proof-of-concept for reporting capabilities  
- **Team Experimentation**: Learning and exploring data analysis patterns
- **Feedback Collection**: Gathering requirements for production version

### Alpha Testing Guidelines
- **Manual Validation**: Always verify data accuracy against source systems
- **Limited Distribution**: Do not share reports outside development team
- **Feedback Required**: Report issues and suggestions to development team
- **Backup Methods**: Maintain alternative reporting approaches for critical needs

---

## Reporting Features

### Quarterly Team Reports (Alpha Development)
The MCP-tools server includes comprehensive quarterly reporting capabilities currently in alpha development stage:

- **Team Performance Analysis**: Anonymized metrics for team productivity and development velocity
- **Multi-Quarter Support**: Q1-Q4 for any year (2020-2030)
- **Data Source Integration**: 
  - **Jira**: Ticket analysis via project queries with JQL support
  - **GitHub**: Commit analysis and repository activity tracking
- **Generic Team Support**: Works with any team prefix (SI, PLAT, CORE, etc.)
- **Output Formats**: 
  - Comprehensive markdown reports
  - Structured JSON data with metrics
  - Data source appendix for transparency

#### Usage Examples:
```bash
# Generate SI team Q2 2025 report
quarterly_team_report --team_prefix SI --year 2025 --quarter 2

# Generate PLAT team Q1 2024 report  
quarterly_team_report --team_prefix PLAT --year 2024 --quarter 1

# With description context
quarterly_team_report --team_prefix CORE --year 2025 --quarter 3 --description "Q3 platform stability focus"
```

#### Report Contents:
- **Executive Summary**: Quarter overview with key achievements
- **Jira Analysis**: Issue types, priorities, completion metrics
- **GitHub Analysis**: Commit patterns, repository activity, collaboration
- **Technical Focus Areas**: Derived from ticket summaries and commit messages
- **Team Velocity**: Development speed and cross-functional coordination
- **Data Sources Appendix**: Complete methodology and data collection details

### Quarter-over-Quarter Analysis (Alpha Development)
Advanced multi-quarter trend analysis with team composition tracking (currently in alpha development):

- **Team Size Evolution**: Track contributor changes, retention rates, and team growth patterns
- **Performance Trends**: Velocity changes, productivity patterns, and comparative metrics
- **Trend Analysis**: Statistical analysis with significance testing and direction indicators
- **Strategic Insights**: Team stability assessment and actionable recommendations
- **Multi-Year Support**: Analyze any period from 2020-2030 across multiple quarters

#### Usage Examples:
```bash
# Analyze SI team performance across 2024
quarter_over_quarter_analysis --team_prefix SI --period "2024"

# Multi-year trend analysis for PLAT team
quarter_over_quarter_analysis --team_prefix PLAT --period "2023-2025"

# Core platform team 2-year comparison
quarter_over_quarter_analysis --team_prefix CORE --period "2024-2025" --description "Platform stability focus period"
```

#### Advanced Features:
- **Team Composition Tracking**: New contributors, departures, retention rates
- **Velocity Scoring**: Weighted productivity metrics with trend analysis
- **Stability Assessment**: Team continuity and turnover impact analysis
- **Comparative Metrics**: Quarter-by-quarter progression with statistical significance
- **Strategic Recommendations**: Data-driven insights for team optimization
- **Retention Analysis**: Contributor overlap and team knowledge continuity

### Personal Performance Reporting (Alpha Development)
Individual contributor performance analysis for personal development tracking and growth assessment (currently in alpha development):

- **Individual Focus**: Personal metrics analysis without team comparisons for privacy-conscious reporting
- **Single Quarter Analysis**: Comprehensive performance snapshot for a specific quarter
- **Quarter-over-Quarter Personal Trends**: Personal growth tracking across multiple time periods
- **Productivity Scoring**: Personal velocity metrics with improvement recommendations
- **Technical Area Analysis**: Personal skill development and focus area identification
- **Growth Recommendations**: Data-driven insights for individual development planning

#### Usage Examples:
```bash
# Generate personal Q2 2025 performance report
personal_quarterly_report --team_prefix SI --year 2025 --quarter 2

# Personal quarter-over-quarter analysis for 2024
personal_quarter_over_quarter --team_prefix SI --period "2024"

# Multi-year personal growth analysis
personal_quarter_over_quarter --team_prefix SI --period "2023-2025" --description "Personal growth assessment"
```

#### Personal Report Contents:
- **Personal Summary**: Individual contributor overview with key achievements
- **Jira Contributions**: Personal ticket completion, types, and priorities handled
- **GitHub Activity**: Individual commit patterns, repository contributions, and code quality
- **Technical Contributions**: Personal technical focus areas and expertise development
- **Productivity Metrics**: Personal velocity scoring and efficiency trends
- **Growth Analysis**: Quarter-over-quarter personal improvement tracking
- **Development Recommendations**: Personalized suggestions for skill development

#### Privacy and Data Handling:
- **Individual Focus**: Reports contain only the current user's contributions
- **No Team Comparisons**: Personal metrics presented independently without ranking
- **Data Privacy**: Personal performance data handled with appropriate confidentiality
- **Self-Assessment Support**: Designed for individual development planning and self-evaluation

## Quality Features
- **Input Validation**: Security checks and parameter validation
- **Error Handling**: Standardized error responses
- **Test Coverage**: Jest with TypeScript support
- **Code Quality**: Shared utilities, no duplication
- **Container Ready**: Production-ready with health checks

## Integration Notes
- **CLI Tools**: Integrates with pr-violations-claude and code-review-claude scripts
- **GitHub**: Requires gh CLI for PR analysis tools
- **Dependencies**: jq, curl, git for tool execution

## Environment Variables
- `MCP_SERVER_PORT`: HTTP server port (default: 8002)
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)
- `TOOL_TIMEOUT`: Tool execution timeout in seconds (default: 300)
- `RATE_LIMIT_REQUESTS`: Rate limit for requests (default: 100)