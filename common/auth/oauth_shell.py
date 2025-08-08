#!/usr/bin/env python3
"""
Shell OAuth authentication for MCP Tools Server

Provides OAuth-like endpoints for MCP client authentication without browser interaction.
Auto-approves all requests for headless/containerized environments.
"""

import logging
from datetime import datetime
from urllib.parse import urlencode

from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse

from config.settings import Config

logger = logging.getLogger(__name__)


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


async def oauth_authorization_server_mcp(request: Request):
    """
    MCP-specific OAuth authorization server discovery endpoint.
    
    Same as oauth_authorization_server but specifically for MCP clients.
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