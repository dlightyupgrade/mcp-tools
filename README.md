# MCP Tools - Multi-Server Architecture

A modular FastMCP server architecture providing development tools, analytics, and reporting for Claude Code integration.

## 🏗️ Architecture Overview

MCP Tools uses a **multi-server composition** architecture with three specialized servers:

- **🎯 Coordinator** (`localhost:8002`) - Main orchestration server that composes tools and reports
- **🛠️ Tools** (`localhost:8003`) - Development workflow automation (PR analysis, code review, JIRA)  
- **📈 Reports** (`localhost:8004`) - Performance analytics and reporting (quarterly reports, metrics)

All servers can run **independently** or **composed together** through the coordinator using FastMCP's `mount()` pattern.

## 🚀 Quick Start

### Container-First Deployment (Recommended)

```bash
# Start all services
./scripts/start.sh

# Check status
./scripts/status.sh

# Stop all services
./scripts/stop.sh

# Add to Claude Code (coordinator endpoint)
claude mcp add mcp-tools http://localhost:8002/mcp/ --transport http --scope user
```

### Development Setup

```bash
# Install dependencies
poetry install

# Run coordinator (mounts all servers)
poetry run python coordinator/server.py

# Or run individual servers
poetry run python tools/server.py      # Tools only (port 8003)
poetry run python reports/server.py    # Reports only (port 8004)
```

## 📊 Service Endpoints

| Service | Port | Health Check | Purpose |
|---------|------|--------------|---------|
| **Coordinator** | 8002 | `http://localhost:8002/health` | Main composition server |
| **Tools** | 8003 | `http://localhost:8003/health` | Development workflows |
| **Reports** | 8004 | `http://localhost:8004/health` | Analytics & reporting |

## 🛠️ Available Tools (14 Core Tools)

### Development Workflow Tools (Tools Server)

#### 1. PR Health (`pr_health`)
Analyzes PR health including open review threads, CI status, and merge readiness.

- **Input**: GitHub PR URL, optional description
- **Output**: Comprehensive health analysis with actionable solutions
- **Example**: `"pr_health https://github.com/owner/repo/pull/123"`

#### 2. Code Review (`code_review`)
Performs comprehensive code quality review with security and performance analysis.

- **Input**: GitHub PR URL, optional focus area, max diff lines
- **Output**: Structured code quality assessment
- **Example**: `"code_review https://github.com/owner/repo/pull/123 security"`

#### 3. Tech Design Review (`tech_design_review`)
Reviews technical design documents with architecture and implementation analysis.

- **Input**: Document URL (Confluence/GitHub), optional focus area
- **Output**: Design review with architecture recommendations
- **Example**: `"tech_design_review https://company.atlassian.net/wiki/pages/123456"`

#### 4. JIRA Transition (`jira_transition`)
Automates JIRA workflow transitions with intelligent state management.

- **Input**: Ticket ID, target state (supports aliases: "dev", "review", "qa", "done")
- **Output**: JIRA transition instructions with Atlassian MCP integration
- **Example**: `"jt SI-1234 start"` or `"jira_transition SI-1234 development"`

#### 5. Get JIRA Transitions (`get_jira_transitions`)
Calculates optimal transition paths between JIRA statuses.

- **Input**: From status, optional to status
- **Output**: Step-by-step transition path with MCP commands
- **Example**: `"get_jira_transitions 'Open' 'In Development'"`

#### 6. Epic Status Report (`epic_status_report`)
Generates comprehensive epic status with sub-task analysis and progress tracking.

- **Input**: Epic ticket ID, optional focus area
- **Output**: Epic progress analysis with assignee action items
- **Example**: `"epic_status_report SI-9038"`

### Analytics & Reporting Tools (Reports Server)

#### 7. Quarterly Team Report (`quarterly_team_report`)
Generates comprehensive quarterly team performance reports with anonymized metrics.

- **Input**: Team prefix, year, quarter, optional description
- **Output**: Team analysis using JIRA and GitHub data
- **Example**: `"quarterly_team_report SI 2025 2"`

#### 8. Quarter-over-Quarter Analysis (`quarter_over_quarter_analysis`)
Analyzes team performance trends and size changes across multiple quarters.

- **Input**: Team prefix, period (e.g., "2024", "2023-2025")
- **Output**: Multi-quarter trend analysis with team composition tracking
- **Example**: `"quarter_over_quarter_analysis SI 2024"`

#### 9. Personal Quarterly Report (`personal_quarterly_report`)
Generates individual contributor performance reports for personal development.

- **Input**: Team prefix, year, quarter
- **Output**: Personal performance analysis with growth recommendations
- **Example**: `"personal_quarterly_report SI 2025 2"`

#### 10. Personal Quarter-over-Quarter (`personal_quarter_over_quarter`)
Analyzes personal performance trends and growth across multiple time periods.

- **Input**: Team prefix, period
- **Output**: Personal growth analysis with development insights
- **Example**: `"personal_quarter_over_quarter SI 2024"`

### System & Utility Tools

#### 11. Setup Prerequisites (`setup_prerequisites`)
Validates and sets up all prerequisites required by MCP Tools.

- **Output**: Comprehensive validation with setup instructions
- **Features**: GitHub CLI, JIRA access, tool availability checks

#### 12. Check Tool Requirements (`check_tool_requirements`)
Checks specific prerequisites for individual MCP tools.

- **Input**: Tool name
- **Output**: Tool-specific validation results

#### 13. Echo (`echo`)
Simple connectivity test for MCP communication validation.

#### 14. Get System Info (`get_system_info`)
System diagnostics and server health monitoring.

## 🐳 Container Architecture

### Multi-Stage Dockerfiles
- **Builder Stage**: Poetry dependency installation
- **Production Stage**: Minimal runtime with non-root user
- **Multi-arch**: Supports AMD64 and ARM64 architectures

### Container Features
- **Health Checks**: Built-in `/health` endpoints for all services
- **Security**: Non-root user execution
- **Logging**: Structured logging with configurable levels
- **Networking**: Isolated bridge network for service communication

### Docker Compose Services

```yaml
services:
  mcp-coordinator:   # Main orchestration (port 8002)
  mcp-tools:         # Development tools (port 8003)
  mcp-reports:       # Analytics server (port 8004)
```

## 🔧 Development & Deployment

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_SERVER_PORT` | 8002/8003/8004 | Server port |
| `LOG_LEVEL` | INFO | Logging level |
| `MOUNT_TOOLS` | true | Mount tools server (coordinator only) |
| `MOUNT_REPORTS` | true | Mount reports server (coordinator only) |

### Container Management

```bash
# Build all containers
podman-compose build

# Start with logs
podman-compose up

# Background mode
podman-compose up -d

# Check status
podman-compose ps

# View logs
podman-compose logs -f mcp-coordinator
```

## 🎯 Integration Patterns

### Claude Code Integration
```bash
# Primary endpoint (coordinator with all tools)
claude mcp add mcp-tools http://localhost:8002/mcp/ --transport http --scope user

# Individual servers (if needed)
claude mcp add mcp-tools-dev http://localhost:8003/mcp/ --transport http --scope user
claude mcp add mcp-reports http://localhost:8004/mcp/ --transport http --scope user
```

### Workflow Examples

```bash
# Complete development workflow
claude "jt SI-1234 start -> pr_health https://github.com/owner/repo/pull/123 -> code_review same_url"

# Quarterly reporting workflow  
claude "quarterly_team_report SI 2025 2 -> personal_quarterly_report SI 2025 2"

# Epic management workflow
claude "epic_status_report SI-9038 -> jt SI-1234 start -> create implementation plan"
```

## 🚨 Alpha Development Status

**MCP Tools is currently in alpha development:**
- ⚠️ Not production ready - features and accuracy not guaranteed
- 🔬 Internal use only - data validation required
- 📊 Report outputs require manual verification
- 🔄 Format and structure may change without notice

## 🏗️ Architecture Benefits

### Modularity
- **Independent Deployment**: Each server can run standalone
- **Specialized Concerns**: Development tools vs. reporting separated
- **Scalable**: Add new servers without modifying existing ones

### FastMCP Composition
- **Server Mounting**: Coordinator mounts specialized servers
- **Unified Interface**: Single endpoint with all tools
- **Service Discovery**: Automatic tool registration and health monitoring

### Container-First Design
- **Production Ready**: Multi-stage builds with security best practices
- **Orchestration**: Docker Compose with networking and health checks
- **Portability**: Runs consistently across development and production environments

---

**Requirements**: Python 3.11+, Poetry, Podman/Docker, Git, curl, jq