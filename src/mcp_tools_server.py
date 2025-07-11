#!/usr/bin/env python3
"""
MCP Tools Server - FastMCP Implementation

A production-ready Model Context Protocol (MCP) server built with FastMCP Python framework,
featuring HTTP Streaming transport and comprehensive development workflow tools.

Tools:
- new_ws: Launch workstream commands in iTerm2
- pr_violations: Analyze PR violations and review threads  
- code_review: Comprehensive code quality review
- morning_workflow: Daily workflow automation
- deploy_approval: Generate Slack deployment messages
- echo: Simple echo for testing
- get_system_info: System information and diagnostics

Architecture:
- FastMCP Python framework with auto-generated schemas
- HTTP Streaming transport (MCP Guidelines compliant)
- uvicorn ASGI server for production deployment
- Comprehensive error handling and logging
- Type-safe tool definitions with validation
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import psutil
import uvicorn
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse
from starlette.routing import Route

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration class for centralized settings
class Config:
    DEFAULT_PORT = int(os.getenv("MCP_SERVER_PORT", "8002"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    TOOL_TIMEOUT = int(os.getenv("TOOL_TIMEOUT", "300"))  # 5 minutes
    RATE_LIMIT = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    
    # Tool script paths
    PR_VIOLATIONS_SCRIPT = os.getenv("PR_VIOLATIONS_SCRIPT", "pr-violations-claude")
    CODE_REVIEW_SCRIPT = os.getenv("CODE_REVIEW_SCRIPT", "code-review-claude")
    MORNING_WORKFLOW_SCRIPT = os.getenv("MORNING_WORKFLOW_SCRIPT", "morning-workflow-claude")
    DEPLOY_APPROVAL_SCRIPT = os.getenv("DEPLOY_APPROVAL_SCRIPT", "deployment-diff-claude")
    NEW_WS_SCRIPT = os.getenv("NEW_WS_SCRIPT", "wclds")

# Initialize FastMCP server
mcp = FastMCP("MCP Tools Server")

# SHELL AUTHENTICATION LAYER
#
# Provides OAuth-like endpoints for MCP client authentication without browser interaction.
# Auto-approves all requests for headless/containerized environments.
#

async def oauth_authorization_server(request: Request):
    """
    OAuth authorization server discovery endpoint.
    
    Provides OAuth 2.0 server metadata for MCP client discovery.
    This is a shell/fake OAuth implementation for headless environments.
    """
    return JSONResponse({
        "issuer": f"http://localhost:{Config.DEFAULT_PORT}",
        "authorization_endpoint": f"http://localhost:{Config.DEFAULT_PORT}/auth",
        "token_endpoint": f"http://localhost:{Config.DEFAULT_PORT}/token",
        "registration_endpoint": f"http://localhost:{Config.DEFAULT_PORT}/register",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "scopes_supported": ["mcp"],
        "code_challenge_methods_supported": ["S256"],
        "headless_supported": True,
        "shell_auth": True,
        "auto_approve": True
    })

async def oauth_protected_resource(request: Request):
    """OAuth protected resource discovery endpoint."""
    return JSONResponse({
        "resource_server": f"http://localhost:{Config.DEFAULT_PORT}",
        "authorization_servers": [f"http://localhost:{Config.DEFAULT_PORT}"],
        "scopes_supported": ["mcp"],
        "bearer_methods_supported": ["header", "query"]
    })

async def register_client(request: Request):
    """Dynamic client registration endpoint."""
    try:
        client_data = await request.json()
        
        # Generate fake client credentials
        client_id = f"mcp_tools_client_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        client_secret = f"secret_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Shell auth: Registered client {client_id}")
        
        return JSONResponse({
            "client_id": client_id,
            "client_secret": client_secret,
            "client_id_issued_at": int(datetime.now().timestamp()),
            "client_secret_expires_at": 0,  # Never expires
            "redirect_uris": client_data.get("redirect_uris", []),
            "grant_types": ["authorization_code"],
            "response_types": ["code"],
            "scope": "mcp",
            "token_endpoint_auth_method": "client_secret_post"
        })
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return JSONResponse(
            {"error": "invalid_client_metadata", "error_description": str(e)},
            status_code=400
        )

async def authorize(request: Request):
    """Authorization endpoint - auto-approve and redirect to callback."""
    query_params = dict(request.query_params)
    
    # Generate authorization code
    auth_code = f"mcp_tools_auth_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    logger.info(f"Shell auth: Generated authorization code {auth_code} (AUTO-REDIRECT)")
    
    state = query_params.get("state", "")
    redirect_uri = query_params.get("redirect_uri", "")
    
    if redirect_uri:
        # Build callback URL with auth code and state
        callback_params = {
            "code": auth_code,
            "state": state
        }
        
        callback_url = f"{redirect_uri}?{urlencode(callback_params)}"
        
        logger.info(f"Shell auth: Redirecting to callback URL: {callback_url}")
        
        # Return redirect response (critical for OAuth compliance)
        return RedirectResponse(url=callback_url, status_code=302)
    else:
        # Fallback: return JSON if no redirect_uri provided
        logger.warning("Shell auth: No redirect_uri provided, returning JSON response")
        return JSONResponse({
            "code": auth_code,
            "state": state,
            "authorization_granted": True,
            "message": "Authorization granted but no redirect_uri specified"
        })

async def token_endpoint(request: Request):
    """Token endpoint - issue access tokens."""
    try:
        form_data = await request.form()
        
        # Generate access token
        access_token = f"mcp_tools_access_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Shell auth: Issued access token {access_token}")
        
        return JSONResponse({
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 3600,  # 1 hour
            "scope": "mcp",
            "refresh_token": f"mcp_tools_refresh_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        })
        
    except Exception as e:
        logger.error(f"Token error: {e}")
        return JSONResponse(
            {"error": "invalid_grant", "error_description": str(e)},
            status_code=400
        )

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
    
    return {
        "echoed_text": text,
        "timestamp": datetime.now().isoformat(),
        "server": "mcp-tools-fastmcp",
        "status": "success"
    }

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
                "version": "1.0.0",
                "port": Config.DEFAULT_PORT,
                "timestamp": datetime.now().isoformat(),
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
        return system_info
        
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return {
            "error": f"Failed to get system info: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "status": "error"
        }

@mcp.tool
def new_ws(command: str, description: str = "") -> Dict[str, Any]:
    """
    Launch workstream commands in iTerm2 for multi-Claude coordination.
    
    Integrates with wclds (workstream Claude launch script) to create new iTerm2 panes
    with specific development tasks.
    
    Args:
        command: The workstream command to execute (e.g., "pr_violations <URL>")
        description: Optional description of the workstream task
        
    Returns:
        Dictionary containing execution results and workstream status
    """
    logger.info(f"new_ws tool called with command: {command}")
    
    try:
        # Validate command format
        if not command.strip():
            return {
                "error": "Command cannot be empty",
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }
        
        # Execute wclds command
        full_command = [Config.NEW_WS_SCRIPT, command]
        logger.info(f"Executing: {' '.join(full_command)}")
        
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            timeout=Config.TOOL_TIMEOUT
        )
        
        if result.returncode == 0:
            return {
                "command": command,
                "description": description,
                "status": "success",
                "output": result.stdout,
                "workstream_launched": True,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "command": command,
                "status": "error",
                "error": result.stderr or "Unknown error occurred",
                "exit_code": result.returncode,
                "timestamp": datetime.now().isoformat()
            }
            
    except subprocess.TimeoutExpired:
        logger.error(f"new_ws command timed out after {Config.TOOL_TIMEOUT} seconds")
        return {
            "error": f"Command timed out after {Config.TOOL_TIMEOUT} seconds",
            "status": "timeout",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error executing new_ws: {e}")
        return {
            "error": f"Failed to execute workstream: {str(e)}",
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool
def pr_violations(pr_url: str, description: str = "") -> Dict[str, Any]:
    """
    Analyze PR violations, open review threads, CI failures, and merge conflicts.
    
    Performs comprehensive PR analysis using the pr-violations-claude script
    to identify issues requiring attention.
    
    Args:
        pr_url: GitHub PR URL to analyze
        description: Optional description of analysis focus
        
    Returns:
        Dictionary containing violation analysis and actionable recommendations
    """
    logger.info(f"pr_violations tool called for: {pr_url}")
    
    try:
        # Validate PR URL format
        if not pr_url.startswith("https://github.com/") or "/pull/" not in pr_url:
            return {
                "error": "Invalid GitHub PR URL format",
                "expected_format": "https://github.com/owner/repo/pull/number",
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }
        
        # Execute pr-violations-claude script
        result = subprocess.run(
            [Config.PR_VIOLATIONS_SCRIPT, pr_url],
            capture_output=True,
            text=True,
            timeout=Config.TOOL_TIMEOUT
        )
        
        if result.returncode == 0:
            return {
                "pr_url": pr_url,
                "description": description,
                "status": "success",
                "analysis": result.stdout,
                "tool_used": "pr-violations-claude",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "pr_url": pr_url,
                "status": "error",
                "error": result.stderr or "Analysis failed",
                "exit_code": result.returncode,
                "timestamp": datetime.now().isoformat()
            }
            
    except subprocess.TimeoutExpired:
        logger.error(f"pr_violations analysis timed out for {pr_url}")
        return {
            "error": f"Analysis timed out after {Config.TOOL_TIMEOUT} seconds",
            "status": "timeout",
            "pr_url": pr_url,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in pr_violations analysis: {e}")
        return {
            "error": f"Failed to analyze PR violations: {str(e)}",
            "status": "error",
            "pr_url": pr_url,
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool
def code_review(pr_url: str, focus: str = "") -> Dict[str, Any]:
    """
    Perform comprehensive code quality review of pull requests.
    
    Uses the code-review-claude script to analyze code quality, security,
    performance, and maintainability aspects.
    
    Args:
        pr_url: GitHub PR URL to review
        focus: Optional focus area (e.g., "security", "performance", "tests")
        
    Returns:
        Dictionary containing comprehensive code review analysis
    """
    logger.info(f"code_review tool called for: {pr_url}")
    
    try:
        # Validate PR URL format
        if not pr_url.startswith("https://github.com/") or "/pull/" not in pr_url:
            return {
                "error": "Invalid GitHub PR URL format",
                "expected_format": "https://github.com/owner/repo/pull/number",
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }
        
        # Execute code-review-claude script
        result = subprocess.run(
            [Config.CODE_REVIEW_SCRIPT, pr_url],
            capture_output=True,
            text=True,
            timeout=Config.TOOL_TIMEOUT
        )
        
        if result.returncode == 0:
            return {
                "pr_url": pr_url,
                "focus": focus,
                "status": "success",
                "review": result.stdout,
                "tool_used": "code-review-claude",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "pr_url": pr_url,
                "status": "error",
                "error": result.stderr or "Code review failed",
                "exit_code": result.returncode,
                "timestamp": datetime.now().isoformat()
            }
            
    except subprocess.TimeoutExpired:
        logger.error(f"code_review timed out for {pr_url}")
        return {
            "error": f"Code review timed out after {Config.TOOL_TIMEOUT} seconds",
            "status": "timeout",
            "pr_url": pr_url,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in code_review: {e}")
        return {
            "error": f"Failed to perform code review: {str(e)}",
            "status": "error",
            "pr_url": pr_url,
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool
def morning_workflow(customization: str = "") -> Dict[str, Any]:
    """
    Execute daily morning workflow automation with parallel subagent orchestration.
    
    Runs the morning-workflow-claude script to perform todo import, PR analysis,
    master branch updates, and thread resolution automation.
    
    Args:
        customization: Optional workflow customization description
        
    Returns:
        Dictionary containing workflow execution results and summary
    """
    logger.info("morning_workflow tool called")
    
    try:
        # Execute morning-workflow-claude script
        result = subprocess.run(
            [Config.MORNING_WORKFLOW_SCRIPT],
            capture_output=True,
            text=True,
            timeout=Config.TOOL_TIMEOUT
        )
        
        if result.returncode == 0:
            return {
                "customization": customization,
                "status": "success",
                "workflow_output": result.stdout,
                "tool_used": "morning-workflow-claude",
                "features_executed": [
                    "todo_import",
                    "pr_analysis", 
                    "master_updates",
                    "thread_automation"
                ],
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "error",
                "error": result.stderr or "Morning workflow failed",
                "exit_code": result.returncode,
                "timestamp": datetime.now().isoformat()
            }
            
    except subprocess.TimeoutExpired:
        logger.error(f"morning_workflow timed out after {Config.TOOL_TIMEOUT} seconds")
        return {
            "error": f"Morning workflow timed out after {Config.TOOL_TIMEOUT} seconds",
            "status": "timeout",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in morning_workflow: {e}")
        return {
            "error": f"Failed to execute morning workflow: {str(e)}",
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool  
def deploy_approval(pr_url: str, deployment_description: str = "") -> Dict[str, Any]:
    """
    Generate deployment approval messages for Slack team coordination.
    
    Uses the deployment-diff-claude script to analyze deployment changes
    and generate formatted Slack messages for approval workflow.
    
    Args:
        pr_url: GitHub PR URL for deployment
        deployment_description: Optional deployment context
        
    Returns:
        Dictionary containing formatted Slack approval message
    """
    logger.info(f"deploy_approval tool called for: {pr_url}")
    
    try:
        # Validate PR URL format
        if not pr_url.startswith("https://github.com/") or "/pull/" not in pr_url:
            return {
                "error": "Invalid GitHub PR URL format",
                "expected_format": "https://github.com/owner/repo/pull/number", 
                "status": "error",
                "timestamp": datetime.now().isoformat()
            }
        
        # Execute deployment-diff-claude script
        result = subprocess.run(
            [Config.DEPLOY_APPROVAL_SCRIPT, pr_url],
            capture_output=True,
            text=True,
            timeout=Config.TOOL_TIMEOUT
        )
        
        if result.returncode == 0:
            return {
                "pr_url": pr_url,
                "deployment_description": deployment_description,
                "status": "success",
                "approval_message": result.stdout,
                "tool_used": "deployment-diff-claude",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "pr_url": pr_url,
                "status": "error",
                "error": result.stderr or "Deployment approval generation failed",
                "exit_code": result.returncode,
                "timestamp": datetime.now().isoformat()
            }
            
    except subprocess.TimeoutExpired:
        logger.error(f"deploy_approval timed out for {pr_url}")
        return {
            "error": f"Deployment approval timed out after {Config.TOOL_TIMEOUT} seconds",
            "status": "timeout",
            "pr_url": pr_url,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in deploy_approval: {e}")
        return {
            "error": f"Failed to generate deployment approval: {str(e)}",
            "status": "error",
            "pr_url": pr_url,
            "timestamp": datetime.now().isoformat()
        }

# TEMPLATE PATTERN: Start the MCP Server over HTTP
# This allows persistent server deployment with HTTP endpoint
# Much more efficient than stdio for containerized deployment
def main():
    """Main function to start the MCP Tools server"""
    logger.info("Starting MCP Tools Server...")
    logger.info(f"Server configuration: Port {Config.DEFAULT_PORT}, Log Level {Config.LOG_LEVEL}")
    
    try:
        # Get the FastAPI app from FastMCP
        app = mcp.http_app()
        
        # Add shell authentication routes for Claude Code compatibility
        auth_routes = [
            Route('/.well-known/oauth-authorization-server', oauth_authorization_server, methods=['GET']),
            Route('/.well-known/oauth-protected-resource', oauth_protected_resource, methods=['GET']),
            Route('/register', register_client, methods=['POST']),
            Route('/auth', authorize, methods=['GET']),
            Route('/token', token_endpoint, methods=['POST']),
        ]
        
        for route in auth_routes:
            app.routes.append(route)
        
        logger.info("FastMCP HTTP Streaming server initialized with shell authentication")
        logger.info("Available tools: echo, get_system_info, new_ws, pr_violations, code_review, morning_workflow, deploy_approval")
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