"""
System Tools for MCP Servers

Utilities for health checks, diagnostics, and system monitoring.
"""

import logging
from typing import Dict, Any
from fastmcp import FastMCP

logger = logging.getLogger(__name__)


def register_system_tools(mcp: FastMCP) -> Dict[str, Any]:
    """
    Register system tools with the FastMCP server.
    
    Args:
        mcp: FastMCP server instance
        
    Returns:
        Dictionary with registration results
    """
    # Import system tools from work directory
    try:
        from tools.work.system import register_system_tools as register_work_system_tools
        register_work_system_tools(mcp)
        
        return {
            "category": "system",
            "successful_registrations": 2,  # echo and get_system_info
            "registered_tools": [
                {"module": "system.echo", "status": "success"},
                {"module": "system.get_system_info", "status": "success"}
            ],
            "registration_errors": []
        }
    except Exception as e:
        logger.error(f"Error registering system tools: {e}")
        return {
            "category": "system",
            "successful_registrations": 0,
            "failed_registrations": 1,
            "registration_errors": [{"error": str(e)}]
        }