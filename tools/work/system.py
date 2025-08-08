#!/usr/bin/env python3
"""
System Tools

Comprehensive system utilities for MCP server testing, diagnostics, and health monitoring.

**Natural Language Triggers:**
- "test mcp" / "check mcp server" - Basic connectivity testing and server verification
- "echo [message]" - Simple echo test for MCP communication validation  
- "system info" / "server status" - Comprehensive system and server diagnostics
- "health check" / "system diagnostics" - System performance and resource monitoring
- "verify mcp tools working" - End-to-end functionality verification
- "mcp server diagnostics" - Complete server health assessment

**Perfect for:** Initial MCP setup verification, troubleshooting connectivity issues, 
monitoring server health, debugging communication problems, system performance analysis, 
confirming server responsiveness and proper tool registration.
"""

import logging
import sys
from datetime import datetime
from typing import Dict, Any

import psutil
from fastmcp import FastMCP

from common.base import ToolBase
from common.config.settings import Config

logger = logging.getLogger(__name__)


def register_system_tools(mcp: FastMCP):
    """Register system tools with the FastMCP server"""
    
    @mcp.tool
    def echo(text: str) -> Dict[str, Any]:
        """
        Echo the provided text back to verify MCP connectivity.
        
        This tool is useful for testing MCP server connectivity and basic functionality.
        
        Args:
            text: The text to echo back
            
        Returns:
            Dictionary containing the echoed text and server information
        """
        logger.info(f"Echo tool called with text: {text}")
        
        return ToolBase.create_success_response({
            "echoed_text": text,
            "server": "mcp-tools-fastmcp"
        })
    
    @mcp.tool
    def get_system_info(include_processes: bool = False) -> Dict[str, Any]:
        """
        Get comprehensive system information and server diagnostics.
        
        Provides detailed system metrics useful for monitoring and debugging.
        
        Args:
            include_processes: Whether to include running process information
            
        Returns:
            Dictionary containing system information and server status
        """
        logger.info("System info tool called")
        
        try:
            # Basic system info
            system_info = {
                "server": {
                    "name": "mcp-tools-fastmcp",
                    "version": "2.0.0",
                    "port": Config.DEFAULT_PORT,
                    "transport": "http-streaming"
                },
                "system": {
                    "platform": sys.platform,
                    "python_version": sys.version,
                    "cpu_count": psutil.cpu_count(),
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "memory_total": psutil.virtual_memory().total,
                    "memory_available": psutil.virtual_memory().available,
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_usage": psutil.disk_usage('/').percent
                },
                "environment": {
                    "log_level": Config.LOG_LEVEL,
                    "tool_timeout": Config.TOOL_TIMEOUT,
                    "rate_limit": Config.RATE_LIMIT
                }
            }
            
            # Add process information if requested
            if include_processes:
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                    try:
                        processes.append(proc.info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                system_info["processes"] = processes[:10]  # Top 10 processes
            
            logger.info("System info retrieved successfully")
            return ToolBase.create_success_response(system_info)
            
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return ToolBase.create_error_response(
                f"Failed to get system info: {str(e)}",
                error_type=type(e).__name__
            )