#!/usr/bin/env python3
"""
MCP Tools - Work Module

Operational and development tools for daily workflow automation and productivity.
"""

import logging
from typing import List, Dict, Any

from fastmcp import FastMCP

logger = logging.getLogger(__name__)


def register_work_tools(mcp: FastMCP) -> Dict[str, Any]:
    """
    Register all work tools with the FastMCP server.
    
    Args:
        mcp: FastMCP server instance
        
    Returns:
        Dictionary with registration results
    """
    registered_tools = []
    registration_errors = []
    
    # List of work tool modules to register
    work_modules = [
        ("pr_health", "register_pr_health_tool"),
        ("code_review", "register_code_review_tool"), 
        ("enhanced_code_review", "register_enhanced_code_review_tool"),
        ("enhanced_code_review_v2", "register_enhanced_code_review_v2_tool"),
        ("tech_design_review", "register_tech_design_review_tool"),
        ("jira_transition", "register_jira_transition_tool"),
        ("jira_transitions", "register_jira_transitions_tool"),
        ("epic_status", "register_epic_status_tool"),
        ("setup_tools", "register_setup_tools"),
        ("system", "register_system_tools")
    ]
    
    logger.info("Starting work tools registration...")
    
    for module_name, register_function_name in work_modules:
        try:
            # Dynamic import of work tool module
            module = __import__(f".{module_name}", fromlist=[register_function_name], package="tools.work")
            
            # Get the registration function
            register_function = getattr(module, register_function_name)
            
            # Call the registration function
            register_function(mcp)
            
            registered_tools.append({
                "module": f"work.{module_name}",
                "register_function": register_function_name,
                "status": "success"
            })
            
            logger.info(f"Successfully registered work tools from: work.{module_name}")
            
        except Exception as e:
            error_info = {
                "module": f"work.{module_name}",
                "register_function": register_function_name,
                "status": "error",
                "error": str(e)
            }
            registration_errors.append(error_info)
            logger.error(f"Error registering work tools from {module_name}: {e}")
    
    return {
        "category": "work", 
        "successful_registrations": len(registered_tools),
        "failed_registrations": len(registration_errors),
        "registered_tools": registered_tools,
        "registration_errors": registration_errors
    }


def get_work_tool_descriptions() -> Dict[str, str]:
    """
    Get descriptions of all available work tools.
    
    Returns:
        Dictionary mapping tool names to their descriptions
    """
    return {
        "pr_health": "Analyze PR health including open review threads, CI status, merge conflicts, and overall readiness",
        "code_review": "Perform comprehensive code quality review of pull requests",
        "tech_design_review": "Comprehensive technical design document review with architecture, security, and implementation analysis",
        "jira_transition": "Automatically perform JIRA ticket transitions using Atlassian MCP",
        "get_jira_transitions": "Calculate transition paths between JIRA statuses with preset shortcuts",
        "epic_status_report": "Generate comprehensive epic status reports with sub-task analysis, progress tracking, and assignee action items",
        "setup_prerequisites": "Validate and setup all prerequisites required by MCP Tools",
        "check_tool_requirements": "Check specific prerequisites for a given MCP tool",
        "echo": "Echo text back to verify MCP connectivity",
        "get_system_info": "Get comprehensive system information and server diagnostics"
    }