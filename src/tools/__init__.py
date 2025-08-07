#!/usr/bin/env python3
"""
MCP Tools Registry

Dynamic tool loader that registers all available tools with the FastMCP server.
Organized into two main categories: Reports (analytics) and Work Tools (operations).
"""

import logging
from typing import List, Dict, Any

from fastmcp import FastMCP
from .reports import register_all_report_tools, get_report_tool_descriptions
from .work import register_all_work_tools, get_work_tool_descriptions

logger = logging.getLogger(__name__)


def register_all_tools(mcp: FastMCP) -> Dict[str, Any]:
    """
    Register all available tools with the FastMCP server.
    
    Tools are organized into two main categories:
    - Reports: Analytics and performance analysis tools
    - Work Tools: Operational and development tools
    
    Args:
        mcp: FastMCP server instance
        
    Returns:
        Dictionary with registration results and tool information
    """
    logger.info("Starting modular tool registration process...")
    
    # Register report tools
    report_results = register_all_report_tools(mcp)
    
    # Register work tools  
    work_results = register_all_work_tools(mcp)
    
    # Combine results
    total_successful = report_results["successful_registrations"] + work_results["successful_registrations"]
    total_failed = report_results["failed_registrations"] + work_results["failed_registrations"]
    total_modules = total_successful + total_failed
    
    all_registered_tools = report_results["registered_tools"] + work_results["registered_tools"]
    all_errors = report_results["registration_errors"] + work_results["registration_errors"]
    
    logger.info(f"Modular tool registration complete: {total_successful}/{total_modules} modules successful")
    logger.info(f"  - Reports: {report_results['successful_registrations']} tools")
    logger.info(f"  - Work Tools: {work_results['successful_registrations']} tools")
    
    if all_errors:
        logger.warning(f"Registration errors occurred in {total_failed} modules")
        for error in all_errors:
            logger.warning(f"  - {error['module']}: {error['status']} - {error['error']}")
    
    return {
        "architecture": "modular",
        "categories": {
            "reports": report_results,
            "work": work_results
        },
        "total_modules": total_modules,
        "successful_registrations": total_successful,
        "failed_registrations": total_failed,
        "registered_tools": all_registered_tools,
        "registration_errors": all_errors,
        "available_tools": get_tool_list(),
        "tool_descriptions": get_all_tool_descriptions(),
        "status": "completed" if total_failed == 0 else "completed_with_errors"
    }


def get_tool_list() -> List[str]:
    """
    Get list of available tool names.
    
    Returns:
        List of tool names that should be available after registration
    """
    return [
        "pr_violations",
        "code_review", 
        "tech_design_review",
        "jira_transition",
        "get_jira_transitions",
        "quarterly_team_report",
        "quarter_over_quarter_analysis",
        "personal_quarterly_report",
        "personal_quarter_over_quarter",
        "setup_prerequisites",
        "check_tool_requirements",
        "echo",
        "get_system_info"
    ]


def get_all_tool_descriptions() -> Dict[str, str]:
    """
    Get descriptions of all available tools from both categories.
    
    Returns:
        Dictionary mapping tool names to their descriptions
    """
    descriptions = {}
    descriptions.update(get_report_tool_descriptions())
    descriptions.update(get_work_tool_descriptions())
    return descriptions