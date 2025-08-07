#!/usr/bin/env python3
"""
MCP Tools - Reports Module

Analytics and performance reporting tools for team and personal development tracking.
"""

import logging
from typing import List, Dict, Any

from fastmcp import FastMCP

logger = logging.getLogger(__name__)


def register_all_report_tools(mcp: FastMCP) -> Dict[str, Any]:
    """
    Register all reporting tools with the FastMCP server.
    
    Args:
        mcp: FastMCP server instance
        
    Returns:
        Dictionary with registration results
    """
    registered_tools = []
    registration_errors = []
    
    # List of reporting tool modules to register
    report_modules = [
        ("quarterly_report", "register_quarterly_team_report_tool"),
        ("quarter_over_quarter", "register_quarter_over_quarter_tool"),
        ("personal_performance", "register_personal_performance_tools")
    ]
    
    logger.info("Starting report tools registration...")
    
    for module_name, register_function_name in report_modules:
        try:
            # Dynamic import of report tool module
            module = __import__(f"tools.reports.{module_name}", fromlist=[register_function_name])
            
            # Get the registration function
            register_function = getattr(module, register_function_name)
            
            # Call the registration function
            register_function(mcp)
            
            registered_tools.append({
                "module": f"reports.{module_name}",
                "register_function": register_function_name,
                "status": "success"
            })
            
            logger.info(f"Successfully registered report tools from: reports.{module_name}")
            
        except Exception as e:
            error_info = {
                "module": f"reports.{module_name}",
                "register_function": register_function_name,
                "status": "error",
                "error": str(e)
            }
            registration_errors.append(error_info)
            logger.error(f"Error registering report tools from {module_name}: {e}")
    
    return {
        "category": "reports",
        "successful_registrations": len(registered_tools),
        "failed_registrations": len(registration_errors),
        "registered_tools": registered_tools,
        "registration_errors": registration_errors
    }


def get_report_tool_descriptions() -> Dict[str, str]:
    """
    Get descriptions of all available reporting tools.
    
    Returns:
        Dictionary mapping tool names to their descriptions
    """
    return {
        "quarterly_team_report": "Generate comprehensive quarterly team performance reports with anonymized metrics",
        "quarter_over_quarter_analysis": "Analyze team performance trends and size changes across multiple quarters",
        "personal_quarterly_report": "Generate individual contributor performance report for a single quarter",
        "personal_quarter_over_quarter": "Analyze personal performance trends and growth across multiple quarters"
    }