#!/usr/bin/env python3
"""
Tools MCP Server

Development workflow automation server providing PR analysis,
code quality reviews, JIRA automation, and system utilities.
"""

import logging
import asyncio
from typing import Dict, Any

from fastmcp import FastMCP

logger = logging.getLogger(__name__)


def create_tools_server() -> FastMCP:
    """
    Create the tools MCP server with development workflow tools.
    
    Returns:
        FastMCP tools server instance
    """
    tools_mcp = FastMCP(name="ToolsMCP")
    
    # Register tool categories
    registration_results = {}
    
    # Register work tools (PR analysis, code review, JIRA automation)
    try:
        from .work import register_work_tools
        work_result = register_work_tools(tools_mcp)
        registration_results["work"] = work_result
        logger.info(f"Registered work tools: {work_result['successful_registrations']} successful")
    except Exception as e:
        logger.error(f"Failed to register work tools: {e}")
        registration_results["work"] = {"error": str(e)}
    
    # Register system tools (health, diagnostics, utilities)
    try:
        from .system import register_system_tools
        system_result = register_system_tools(tools_mcp)
        registration_results["system"] = system_result
        logger.info(f"Registered system tools: {system_result['successful_registrations']} successful")
    except Exception as e:
        logger.error(f"Failed to register system tools: {e}")
        registration_results["system"] = {"error": str(e)}
    
    # Add tools server health endpoint
    @tools_mcp.tool
    def tools_server_health() -> Dict[str, Any]:
        """Check tools server health and registered tools status"""
        return {
            "status": "healthy",
            "server": "tools",
            "registration_results": registration_results,
            "total_tools": sum(
                result.get("successful_registrations", 0) 
                for result in registration_results.values()
                if isinstance(result, dict) and "successful_registrations" in result
            )
        }
    
    logger.info("Tools server created successfully")
    return tools_mcp


async def main():
    """Main entry point for tools server"""
    import os
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Create and run tools server
    tools_server = create_tools_server()
    
    port = int(os.getenv("MCP_SERVER_PORT", "8003"))
    logger.info(f"Starting tools server on port {port}")
    
    try:
        await tools_server.run(port=port)
    except KeyboardInterrupt:
        logger.info("Tools server stopped by user")
    except Exception as e:
        logger.error(f"Tools server error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())