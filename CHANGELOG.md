# Changelog

## [2.0.2] - 2025-08-08

### Changed
- **BREAKING**: Migrated from uv to Poetry for dependency management
  - Updated pyproject.toml with Poetry configuration
  - Fixed Python version constraint (>=3.11,<4.0) for compatibility
  - Updated Dockerfile to use Poetry instead of uv
  - Modified build.sh to use Poetry lock file updates
  - Updated documentation and README with Poetry setup instructions

### Removed  
- uv.lock file (replaced with Poetry lock file)
- Old uv-specific configuration

### Added
- poetry.lock file for reproducible builds
- Enhanced development setup documentation

## [2.0.1] - 2025-08-07

### Added
- MCP Tools FastMCP server v2.0.1
- Modular development workflow automation with PR analysis, code review, and deployment tools
- 3-agent coordination system for enhanced JIRA→GitHub PR bridging

### Changes
- Initial release


All notable changes to MCP Tools will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
