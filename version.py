#!/usr/bin/env python3
"""MCP Tools Version Management and Release Automation."""

import subprocess
import sys
import re
from pathlib import Path
from typing import Tuple, Optional

# Simple TOML parsing without external dependencies
def parse_simple_toml(content: str) -> dict:
    """Parse simple TOML content - focused on version extraction."""
    result = {}
    current_section = None
    
    for line in content.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        if line.startswith('[') and line.endswith(']'):
            current_section = line[1:-1]
            if current_section not in result:
                result[current_section] = {}
            continue
        
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"\'')
            
            if current_section:
                result[current_section][key] = value
            else:
                result[key] = value
    
    return result

def write_simple_toml_version(file_path: Path, new_version: str):
    """Update version in TOML file without external dependencies."""
    content = file_path.read_text()
    
    # Replace version in [project] section
    lines = content.split('\n')
    in_project_section = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        if stripped == '[project]':
            in_project_section = True
            continue
        elif stripped.startswith('[') and stripped != '[project]':
            in_project_section = False
            continue
        
        if in_project_section and 'version' in line and '=' in line:
            # Replace the version line
            indent = len(line) - len(line.lstrip())
            lines[i] = f"{' ' * indent}version = \"{new_version}\""
            break
    
    file_path.write_text('\n'.join(lines))

__version__ = "2.0.1"

PROJECT_ROOT = Path(__file__).parent
PYPROJECT_TOML = PROJECT_ROOT / "pyproject.toml"
VERSION_FILE = PROJECT_ROOT / "src" / "__version__.py"

class VersionManager:
    """Semantic versioning and release management for MCP Tools."""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        
    def get_current_version(self) -> str:
        """Get current version from pyproject.toml."""
        try:
            content = PYPROJECT_TOML.read_text()
            data = parse_simple_toml(content)
            return data.get('project', {}).get('version', __version__)
        except Exception as e:
            print(f"Error reading version: {e}")
            return __version__
    
    def bump_version(self, version_type: str) -> Tuple[str, str]:
        """Bump version according to semantic versioning.
        
        Args:
            version_type: 'major', 'minor', or 'patch'
            
        Returns:
            Tuple of (old_version, new_version)
        """
        current = self.get_current_version()
        parts = current.split('.')
        
        if len(parts) != 3:
            raise ValueError(f"Invalid version format: {current}")
        
        major, minor, patch = map(int, parts)
        
        if version_type == 'major':
            major += 1
            minor = 0
            patch = 0
        elif version_type == 'minor':
            minor += 1
            patch = 0
        elif version_type == 'patch':
            patch += 1
        else:
            raise ValueError(f"Invalid version type: {version_type}")
        
        new_version = f"{major}.{minor}.{patch}"
        return current, new_version
    
    def update_version_files(self, new_version: str):
        """Update version in all relevant files."""
        # Update pyproject.toml using custom TOML functions
        write_simple_toml_version(PYPROJECT_TOML, new_version)
        
        # Create/update src/__version__.py
        VERSION_FILE.parent.mkdir(exist_ok=True)
        with open(VERSION_FILE, 'w') as f:
            f.write(f'"""MCP Tools version information."""\n\n__version__ = "2.0.1"\n')
        
        # Update this file
        script_content = Path(__file__).read_text()
        updated_content = re.sub(
            r'__version__ = "2.0.1"]*"',
            f'__version__ = "2.0.1"',
            script_content
        )
        Path(__file__).write_text(updated_content)
        
        # Update main server file version
        server_file = PROJECT_ROOT / "src" / "mcp_tools_server.py"
        if server_file.exists():
            content = server_file.read_text()
            # Update version in server info (look for version patterns)
            content = re.sub(
                r'"version": "[^"]*"',
                f'"version": "{new_version}"',
                content
            )
            # Also update any __version__ declarations
            content = re.sub(
                r'__version__ = "2.0.1"]*"',
                f'__version__ = "2.0.1"',
                content
            )
            server_file.write_text(content)
    
    def create_git_tag(self, version: str, message: Optional[str] = None):
        """Create and push git tag for release."""
        tag = f"v{version}"
        
        if not message:
            message = f"Release {tag}: MCP Tools FastMCP server"
        
        try:
            # Create tag
            subprocess.run(['git', 'tag', '-a', tag, '-m', message], check=True)
            print(f"✅ Created git tag: {tag}")
            
            # Push tag
            subprocess.run(['git', 'push', 'origin', tag], check=True)
            print(f"✅ Pushed tag to remote: {tag}")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git tag operation failed: {e}")
    
    def generate_changelog(self, old_version: str, new_version: str) -> str:
        """Generate changelog entry for version."""
        try:
            # Get commits since last version
            result = subprocess.run(
                ['git', 'log', f'v{old_version}..HEAD', '--oneline', '--no-merges'],
                capture_output=True, text=True, check=True
            )
            commits = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
        except subprocess.CalledProcessError:
            # Fallback if no previous tag exists
            commits = ["Initial release"]
        
        changelog = f"""## [{new_version}] - {subprocess.run(['date', '+%Y-%m-%d'], capture_output=True, text=True).stdout.strip()}

### Added
- MCP Tools FastMCP server v{new_version}
- Modular development workflow automation with PR analysis, code review, and deployment tools
- 3-agent coordination system for enhanced JIRA→GitHub PR bridging

### Changes
"""
        
        for commit in commits[:10]:  # Limit to 10 most recent
            if commit.strip():
                changelog += f"- {commit.strip()}\n"
        
        return changelog
    
    def update_changelog(self, old_version: str, new_version: str):
        """Update CHANGELOG.md with new version entry."""
        changelog_file = PROJECT_ROOT / "CHANGELOG.md"
        new_entry = self.generate_changelog(old_version, new_version)
        
        if changelog_file.exists():
            existing_content = changelog_file.read_text()
            # Insert new entry after header
            lines = existing_content.split('\n')
            insert_index = 2  # After title and blank line
            lines.insert(insert_index, new_entry)
            changelog_file.write_text('\n'.join(lines))
        else:
            # Create new changelog
            content = f"""# Changelog

{new_entry}

All notable changes to MCP Tools will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
"""
            changelog_file.write_text(content)
        
        print(f"✅ Updated CHANGELOG.md with v{new_version}")

def main():
    """Version management CLI."""
    if len(sys.argv) < 2:
        print("Usage: python version.py <command> [args]")
        print("Commands:")
        print("  current                    - Show current version")
        print("  bump major|minor|patch     - Bump version and create release")
        print("  tag <version> [message]    - Create git tag for version")
        return
    
    vm = VersionManager()
    command = sys.argv[1]
    
    if command == "current":
        version = vm.get_current_version()
        print(f"Current version: {version}")
        
    elif command == "bump":
        if len(sys.argv) < 3:
            print("Usage: python version.py bump major|minor|patch")
            return
        
        version_type = sys.argv[2]
        if version_type not in ['major', 'minor', 'patch']:
            print("Version type must be major, minor, or patch")
            return
        
        try:
            old_version, new_version = vm.bump_version(version_type)
            print(f"Bumping version: {old_version} → {new_version}")
            
            # Update all version files
            vm.update_version_files(new_version)
            print(f"✅ Updated version files to {new_version}")
            
            # Update changelog
            vm.update_changelog(old_version, new_version)
            
            # Commit changes
            subprocess.run(['git', 'add', '.'], check=True)
            subprocess.run(['git', 'commit', '-m', f'bump version to {new_version}'], check=True)
            print(f"✅ Committed version bump")
            
            # Create and push tag
            vm.create_git_tag(new_version)
            
            print(f"🎉 Successfully released MCP Tools v{new_version}")
            print(f"🐳 Container images will be tagged as: mcp-tools:{new_version}")
            
        except Exception as e:
            print(f"❌ Release failed: {e}")
            
    elif command == "tag":
        if len(sys.argv) < 3:
            print("Usage: python version.py tag <version> [message]")
            return
        
        version = sys.argv[2]
        message = sys.argv[3] if len(sys.argv) > 3 else None
        vm.create_git_tag(version, message)
        
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()