#!/usr/bin/env python3
"""
Reports MCP Server

Performance analytics and reporting server providing team metrics,
quarterly analysis, and project status reports.
"""

import logging
import asyncio
from typing import Dict, Any

from fastmcp import FastMCP

logger = logging.getLogger(__name__)


def create_reports_server() -> FastMCP:
    """
    Create the reports MCP server with analytics and reporting tools.
    
    Returns:
        FastMCP reports server instance
    """
    reports_mcp = FastMCP(name="ReportsMCP")
    
    # Register reporting tool categories
    registration_results = {}
    
    # Register analytics tools (quarterly reports, team metrics, etc.)
    try:
        from .analytics import register_analytics_tools
        analytics_result = register_analytics_tools(reports_mcp)
        registration_results["analytics"] = analytics_result
        logger.info(f"Registered analytics tools: {analytics_result['successful_registrations']} successful")
    except ImportError:
        logger.warning("Analytics tools module not found - creating placeholder")
        # Create placeholder analytics tool
        @reports_mcp.tool
        def placeholder_analytics() -> Dict[str, Any]:
            """Placeholder analytics tool - reports server in development"""
            return {
                "status": "placeholder",
                "message": "Analytics tools in development",
                "server": "reports"
            }
        registration_results["analytics"] = {"successful_registrations": 1, "tools": ["placeholder_analytics"]}
    except Exception as e:
        logger.error(f"Failed to register analytics tools: {e}")
        registration_results["analytics"] = {"error": str(e)}
    
    # Register dashboard tools (status dashboards, project tracking, etc.)
    try:
        from .dashboards import register_dashboard_tools
        dashboard_result = register_dashboard_tools(reports_mcp)
        registration_results["dashboards"] = dashboard_result
        logger.info(f"Registered dashboard tools: {dashboard_result['successful_registrations']} successful")
    except ImportError:
        logger.warning("Dashboard tools module not found - creating placeholder")
        # Create placeholder dashboard tool
        @reports_mcp.tool
        def placeholder_dashboards() -> Dict[str, Any]:
            """Placeholder dashboard tool - reports server in development"""
            return {
                "status": "placeholder", 
                "message": "Dashboard tools in development",
                "server": "reports"
            }
        registration_results["dashboards"] = {"successful_registrations": 1, "tools": ["placeholder_dashboards"]}
    except Exception as e:
        logger.error(f"Failed to register dashboard tools: {e}")
        registration_results["dashboards"] = {"error": str(e)}
    
    # Add reports server health endpoint
    @reports_mcp.tool
    def reports_server_health() -> Dict[str, Any]:
        """Check reports server health and registered tools status"""
        return {
            "status": "healthy",
            "server": "reports",
            "registration_results": registration_results,
            "total_tools": sum(
                result.get("successful_registrations", 0) 
                for result in registration_results.values()
                if isinstance(result, dict) and "successful_registrations" in result
            )
        }
    
    logger.info("Reports server created successfully")
    return reports_mcp


async def main():
    """Main entry point for reports server"""
    import os
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Create and run reports server
    reports_server = create_reports_server()
    
    port = int(os.getenv("MCP_SERVER_PORT", "8004"))
    logger.info(f"Starting reports server on port {port}")
    
    try:
        await reports_server.run(port=port)
    except KeyboardInterrupt:
        logger.info("Reports server stopped by user")
    except Exception as e:
        logger.error(f"Reports server error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())