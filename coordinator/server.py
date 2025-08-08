#!/usr/bin/env python3
"""
MCP Coordinator Server

Main orchestration server that composes tools and reports servers
using FastMCP composition patterns. Provides unified access to all
MCP Tools capabilities.
"""

import logging
import asyncio
from typing import Optional

from fastmcp import FastMCP

logger = logging.getLogger(__name__)


def create_coordinator_server(
    mount_tools: bool = True,
    mount_reports: bool = True,
    tools_prefix: str = "tools",
    reports_prefix: str = "reports"
) -> FastMCP:
    """
    Create the coordinator MCP server with mounted sub-servers.
    
    Args:
        mount_tools: Whether to mount the tools server
        mount_reports: Whether to mount the reports server
        tools_prefix: Prefix for tools server mounting
        reports_prefix: Prefix for reports server mounting
        
    Returns:
        FastMCP coordinator server instance
    """
    coordinator = FastMCP(name="CoordinatorMCP")
    
    # Add coordinator-specific health endpoint
    @coordinator.tool
    def coordinator_health() -> dict:
        """Check coordinator server health and mounted servers status"""
        return {
            "status": "healthy",
            "server": "coordinator",
            "mounted_servers": {
                "tools": mount_tools,
                "reports": mount_reports
            }
        }
    
    # Mount specialized servers if requested
    if mount_tools:
        try:
            from tools.server import create_tools_server
            tools_server = create_tools_server()
            coordinator.mount(tools_server, prefix=tools_prefix)
            logger.info(f"Mounted tools server with prefix: {tools_prefix}")
        except ImportError as e:
            logger.error(f"Failed to import tools server: {e}")
        except Exception as e:
            logger.error(f"Failed to mount tools server: {e}")
    
    if mount_reports:
        try:
            from reports.server import create_reports_server
            reports_server = create_reports_server()
            coordinator.mount(reports_server, prefix=reports_prefix)
            logger.info(f"Mounted reports server with prefix: {reports_prefix}")
        except ImportError as e:
            logger.error(f"Failed to import reports server: {e}")
        except Exception as e:
            logger.error(f"Failed to mount reports server: {e}")
    
    logger.info("Coordinator server created successfully")
    return coordinator


async def main():
    """Main entry point for coordinator server"""
    import os
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Create and run coordinator server
    coordinator = create_coordinator_server()
    
    port = int(os.getenv("MCP_SERVER_PORT", "8002"))
    logger.info(f"Starting coordinator server on port {port}")
    
    try:
        await coordinator.run(port=port)
    except KeyboardInterrupt:
        logger.info("Coordinator server stopped by user")
    except Exception as e:
        logger.error(f"Coordinator server error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())