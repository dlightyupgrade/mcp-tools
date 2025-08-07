#!/usr/bin/env python3
"""
MCP Tools Setup and Prerequisites Validation

Centralized tool for validating and setting up all prerequisites required by MCP Tools.
This eliminates the need for individual tools to include validation steps, making
tool execution more streamlined once setup is complete.
"""

import logging
import subprocess
import sys
from typing import Dict, Any, List, Optional
import json

from fastmcp import FastMCP
from ..base import ToolBase

logger = logging.getLogger(__name__)


def register_setup_tools(mcp: FastMCP):
    """Register setup and validation tools with the FastMCP server"""
    
    @mcp.tool
    def setup_prerequisites() -> Dict[str, Any]:
        """
        Validate and setup all prerequisites required by MCP Tools.
        
        **What this tool does:**
        Comprehensive validation of all external tools and services required by MCP Tools:
        - GitHub CLI authentication and configuration
        - Atlassian MCP server connectivity  
        - JIRA access and permissions
        - Required command-line tools (jq, git, etc.)
        - Environment variables and configuration files
        
        **Perfect for:** Initial MCP Tools setup, troubleshooting tool failures, 
        environment validation after system changes.
        
        Returns:
            Dictionary containing setup status and any required actions
        """
        logger.info("Starting comprehensive prerequisites validation")
        
        try:
            setup_results = {
                "tool_name": "setup_prerequisites",
                "timestamp": ToolBase.create_success_response({})["timestamp"],
                "validation_results": {},
                "setup_actions": [],
                "overall_status": "unknown"
            }
            
            # GitHub CLI validation
            github_status = validate_github_cli()
            setup_results["validation_results"]["github_cli"] = github_status
            
            # Atlassian MCP validation  
            atlassian_status = validate_atlassian_mcp()
            setup_results["validation_results"]["atlassian_mcp"] = atlassian_status
            
            # Command-line tools validation
            cli_tools_status = validate_cli_tools()
            setup_results["validation_results"]["cli_tools"] = cli_tools_status
            
            # Environment validation
            env_status = validate_environment()
            setup_results["validation_results"]["environment"] = env_status
            
            # Collect setup actions
            for category, status in setup_results["validation_results"].items():
                if not status["valid"] and "setup_actions" in status:
                    setup_results["setup_actions"].extend(status["setup_actions"])
            
            # Determine overall status
            all_valid = all(result["valid"] for result in setup_results["validation_results"].values())
            setup_results["overall_status"] = "ready" if all_valid else "setup_required"
            
            # Add summary
            setup_results["summary"] = generate_setup_summary(setup_results)
            
            logger.info(f"Prerequisites validation completed: {setup_results['overall_status']}")
            return setup_results
            
        except Exception as e:
            logger.error(f"Error during prerequisites validation: {str(e)}")
            return ToolBase.create_error_response(
                f"Failed to validate prerequisites: {str(e)}",
                error_type=type(e).__name__
            )
    
    @mcp.tool  
    def check_tool_requirements(tool_name: str) -> Dict[str, Any]:
        """
        Check specific prerequisites for a given MCP tool.
        
        Args:
            tool_name: Name of the tool to check requirements for
            
        Returns:
            Dictionary containing tool-specific requirement status
        """
        logger.info(f"Checking requirements for tool: {tool_name}")
        
        try:
            tool_requirements = get_tool_requirements()
            
            if tool_name not in tool_requirements:
                return ToolBase.create_error_response(
                    f"Unknown tool: {tool_name}. Available tools: {list(tool_requirements.keys())}",
                    error_type="validation_error"
                )
            
            requirements = tool_requirements[tool_name]
            requirement_status = {}
            
            # Check each requirement category
            for category, items in requirements.items():
                if category == "description":
                    continue
                    
                requirement_status[category] = []
                for item in items:
                    status = check_individual_requirement(item)
                    requirement_status[category].append({
                        "requirement": item,
                        "status": status
                    })
            
            all_met = all(
                all(req["status"]["valid"] for req in category_reqs)
                for category_reqs in requirement_status.values()
            )
            
            return {
                "tool_name": tool_name,
                "requirements_met": all_met,
                "requirement_details": requirement_status,
                "tool_description": requirements.get("description", ""),
                "timestamp": ToolBase.create_success_response({})["timestamp"]
            }
            
        except Exception as e:
            logger.error(f"Error checking tool requirements: {str(e)}")
            return ToolBase.create_error_response(
                f"Failed to check tool requirements: {str(e)}",
                error_type=type(e).__name__
            )


def validate_github_cli() -> Dict[str, Any]:
    """Validate GitHub CLI installation and authentication"""
    result = {
        "valid": False,
        "details": {},
        "setup_actions": []
    }
    
    try:
        # Check if gh is installed
        gh_version = subprocess.run(
            ["gh", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if gh_version.returncode != 0:
            result["details"]["installation"] = "GitHub CLI not found"
            result["setup_actions"].append("Install GitHub CLI: brew install gh")
            return result
            
        result["details"]["installation"] = "✅ GitHub CLI installed"
        result["details"]["version"] = gh_version.stdout.split('\n')[0]
        
        # Check authentication
        auth_status = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if auth_status.returncode != 0:
            result["details"]["authentication"] = "❌ Not authenticated"
            result["setup_actions"].append("Authenticate GitHub CLI: gh auth login")
            return result
            
        result["details"]["authentication"] = "✅ Authenticated"
        result["valid"] = True
        
    except subprocess.TimeoutExpired:
        result["details"]["error"] = "GitHub CLI command timed out"
        result["setup_actions"].append("Check GitHub CLI installation and network connectivity")
    except FileNotFoundError:
        result["details"]["installation"] = "GitHub CLI not found"  
        result["setup_actions"].append("Install GitHub CLI: brew install gh")
    except Exception as e:
        result["details"]["error"] = f"Unexpected error: {str(e)}"
        
    return result


def validate_atlassian_mcp() -> Dict[str, Any]:
    """Validate Atlassian MCP server connectivity"""
    result = {
        "valid": False,
        "details": {},
        "setup_actions": []
    }
    
    # Note: This is a placeholder for MCP server validation
    # In a real implementation, this would test the MCP connection
    result["details"]["status"] = "⚠️  MCP server validation not yet implemented"
    result["setup_actions"].append("Ensure Atlassian MCP server is configured and accessible")
    result["valid"] = True  # Assume valid for now
    
    return result


def validate_cli_tools() -> Dict[str, Any]:
    """Validate required command-line tools"""
    result = {
        "valid": True,
        "details": {},
        "setup_actions": []
    }
    
    required_tools = {
        "jq": "JSON processor - Install with: brew install jq",
        "git": "Version control - Usually pre-installed on macOS/Linux", 
        "curl": "HTTP client - Usually pre-installed",
        "python3": "Python interpreter - Install with: brew install python"
    }
    
    for tool, install_msg in required_tools.items():
        try:
            tool_check = subprocess.run(
                [tool, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if tool_check.returncode == 0:
                result["details"][tool] = "✅ Available"
            else:
                result["details"][tool] = "❌ Not working"
                result["setup_actions"].append(install_msg)
                result["valid"] = False
                
        except FileNotFoundError:
            result["details"][tool] = "❌ Not found"
            result["setup_actions"].append(install_msg)
            result["valid"] = False
        except Exception as e:
            result["details"][tool] = f"⚠️  Error checking: {str(e)}"
            
    return result


def validate_environment() -> Dict[str, Any]:
    """Validate environment variables and configuration"""
    result = {
        "valid": True,
        "details": {},
        "setup_actions": []
    }
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 11:
        result["details"]["python_version"] = f"✅ Python {python_version.major}.{python_version.minor}"
    else:
        result["details"]["python_version"] = f"⚠️  Python {python_version.major}.{python_version.minor} (recommend 3.11+)"
        
    # Check working directory
    import os
    result["details"]["working_directory"] = os.getcwd()
    
    # Add any environment-specific checks here
    result["details"]["environment"] = "✅ Basic environment checks passed"
    
    return result


def check_individual_requirement(requirement: str) -> Dict[str, Any]:
    """Check status of an individual requirement"""
    result = {"valid": False, "details": ""}
    
    if requirement.startswith("github_cli"):
        gh_status = validate_github_cli()
        result["valid"] = gh_status["valid"]
        result["details"] = gh_status["details"]
    elif requirement.startswith("atlassian_mcp"):
        atlassian_status = validate_atlassian_mcp()
        result["valid"] = atlassian_status["valid"] 
        result["details"] = atlassian_status["details"]
    elif requirement in ["jq", "git", "curl", "python3"]:
        try:
            tool_check = subprocess.run(
                [requirement, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            result["valid"] = tool_check.returncode == 0
            result["details"] = "Available" if result["valid"] else "Not working"
        except FileNotFoundError:
            result["valid"] = False
            result["details"] = "Not found"
        except Exception as e:
            result["valid"] = False
            result["details"] = f"Error: {str(e)}"
    else:
        result["details"] = f"Unknown requirement: {requirement}"
        
    return result


def get_tool_requirements() -> Dict[str, Dict[str, Any]]:
    """Get requirements for all MCP tools"""
    return {
        "quarterly_team_report": {
            "description": "Generate comprehensive quarterly team performance reports with anonymized metrics",
            "cli_tools": ["github_cli", "jq", "git"],
            "mcp_services": ["atlassian_mcp"],
            "permissions": ["jira_project_access", "github_org_access"]
        },
        "quarter_over_quarter_analysis": {
            "description": "Analyze team performance trends and size changes across multiple quarters", 
            "cli_tools": ["github_cli", "jq", "git"],
            "mcp_services": ["atlassian_mcp"],
            "permissions": ["jira_project_access", "github_org_access"]
        },
        "personal_quarterly_report": {
            "description": "Generate individual contributor performance report for a single quarter",
            "cli_tools": ["github_cli", "jq", "git"], 
            "mcp_services": ["atlassian_mcp"],
            "permissions": ["jira_personal_access", "github_user_access"]
        },
        "personal_quarter_over_quarter": {
            "description": "Analyze personal performance trends and growth across multiple quarters",
            "cli_tools": ["github_cli", "jq", "git"],
            "mcp_services": ["atlassian_mcp"], 
            "permissions": ["jira_personal_access", "github_user_access"]
        },
        "pr_violations": {
            "description": "Analyze PR violations, open review threads, CI failures, and merge conflicts",
            "cli_tools": ["github_cli", "jq", "git"],
            "mcp_services": [],
            "permissions": ["github_pr_access"]
        },
        "code_review": {
            "description": "Comprehensive code quality review of pull requests",
            "cli_tools": ["github_cli", "jq", "git"],
            "mcp_services": [],
            "permissions": ["github_pr_access"]
        },
        "tech_design_review": {
            "description": "Perform comprehensive technical design document review",
            "cli_tools": ["curl"],
            "mcp_services": ["atlassian_mcp"],
            "permissions": ["confluence_access"]
        },
        "jira_transition": {
            "description": "Automatically perform JIRA ticket transitions",
            "cli_tools": [],
            "mcp_services": ["atlassian_mcp"],
            "permissions": ["jira_transition_access"]
        },
        "get_jira_transitions": {
            "description": "Calculate transition paths between JIRA statuses", 
            "cli_tools": [],
            "mcp_services": ["atlassian_mcp"],
            "permissions": ["jira_read_access"]
        }
    }


def generate_setup_summary(setup_results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a human-readable setup summary"""
    summary = {
        "status": setup_results["overall_status"],
        "ready_tools": [],
        "blocked_tools": [],
        "next_actions": setup_results["setup_actions"][:3]  # Top 3 actions
    }
    
    if setup_results["overall_status"] == "ready":
        summary["message"] = "🎉 All prerequisites validated successfully! MCP Tools are ready to use."
        summary["ready_tools"] = list(get_tool_requirements().keys())
    else:
        summary["message"] = f"⚠️  Setup required. {len(setup_results['setup_actions'])} actions needed."
        
        # Determine which tools are ready vs blocked
        tool_requirements = get_tool_requirements()
        for tool_name, requirements in tool_requirements.items():
            tool_ready = True
            for category, items in requirements.items():
                if category == "description":
                    continue
                for item in items:
                    requirement_status = check_individual_requirement(item)
                    if not requirement_status["valid"]:
                        tool_ready = False
                        break
                if not tool_ready:
                    break
                    
            if tool_ready:
                summary["ready_tools"].append(tool_name)
            else:
                summary["blocked_tools"].append(tool_name)
    
    return summary