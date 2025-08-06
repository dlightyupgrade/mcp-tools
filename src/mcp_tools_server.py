#!/usr/bin/env python3
"""
MCP Tools Server v2.0 - Modular FastMCP Implementation

🚀 PRODUCTION VERSION with modular architecture for better maintainability

A production-ready Model Context Protocol (MCP) server built with FastMCP Python framework,
featuring HTTP Streaming transport and modular tool architecture.

Architecture:
- Modular tool system with dynamic registration
- FastMCP Python framework with auto-generated schemas
- HTTP Streaming transport (MCP Guidelines compliant)
- Shell OAuth authentication for headless environments
- uvicorn ASGI server for production deployment
"""

import logging
import sys
from datetime import datetime

import uvicorn
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

# Import our modular components
from config.settings import Config
from auth.oauth_shell import (
    oauth_authorization_server,
    oauth_authorization_server_mcp,
    oauth_protected_resource,
    register_client,
    authorize,
    token_endpoint
)
from tools import register_all_tools, get_tool_descriptions

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("MCP Tools Server")


def main():
    """Main function to start the MCP Tools server"""
    logger.info("Starting MCP Tools Server (Modular Architecture)...")
    logger.info(f"Server configuration: Port {Config.DEFAULT_PORT}, Log Level {Config.LOG_LEVEL}")
    
    try:
        # Register all tools using the modular system
        logger.info("Registering tools using modular architecture...")
        registration_result = register_all_tools(mcp)
        
        # Log registration results
        if registration_result["status"] == "completed":
            logger.info(f"All tools registered successfully: {registration_result['successful_registrations']} modules")
        else:
            logger.warning(f"Tool registration completed with errors: {registration_result['failed_registrations']} failed")
        
        # Get the FastAPI app from FastMCP
        app = mcp.http_app()
        
        # Health endpoint for container health checks
        async def health_check(request: Request):
            tool_descriptions = get_tool_descriptions()
            return JSONResponse({
                "status": "healthy",
                "service": "mcp-tools",
                "version": "2.0.0",
                "architecture": "modular",
                "transport": "FastMCP HTTP Streaming",
                "timestamp": datetime.now().isoformat(),
                "port": Config.DEFAULT_PORT,
                "tools": {
                    "available": list(tool_descriptions.keys()),
                    "count": len(tool_descriptions),
                    "descriptions": tool_descriptions
                },
                "registration": {
                    "status": registration_result["status"],
                    "successful": registration_result["successful_registrations"],
                    "failed": registration_result["failed_registrations"],
                    "total": registration_result["total_modules"]
                }
            })
        
        # Add shell authentication routes for Claude Code compatibility
        auth_routes = [
            Route('/health', health_check, methods=['GET']),
            Route('/.well-known/oauth-authorization-server', oauth_authorization_server, methods=['GET']),
            Route('/.well-known/oauth-authorization-server-mcp', oauth_authorization_server_mcp, methods=['GET']),
            Route('/.well-known/oauth-protected-resource', oauth_protected_resource, methods=['GET']),
            Route('/register', register_client, methods=['POST']),
            Route('/auth', authorize, methods=['GET']),
            Route('/token', token_endpoint, methods=['POST']),
        ]
        
        for route in auth_routes:
            app.routes.append(route)
        
        logger.info("FastMCP HTTP Streaming server initialized with shell authentication")
        logger.info(f"Available tools: {', '.join(get_tool_descriptions().keys())}")
        logger.info("Authentication endpoints: /.well-known/oauth-authorization-server, /register, /auth, /token")
        
        # Run with uvicorn
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=Config.DEFAULT_PORT,
            log_level=Config.LOG_LEVEL.lower()
        )
        
    except Exception as e:
        logger.error(f"Failed to start MCP Tools server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
