# AUTHENTICATION.md

**Shell Authentication Layer for MCP Tools Server**

This document describes the shell authentication implementation in MCP Tools Server, designed for seamless Claude Code integration without browser interaction.

## Overview

The MCP Tools server implements a **shell authentication layer** - a lightweight OAuth-like system that provides authentication endpoints without requiring actual security. This allows Claude Code to establish HTTP transport sessions properly while working in headless/containerized environments.

## Design Philosophy

### Why Shell Authentication?

1. **Claude Code Compatibility**: Claude Code expects OAuth endpoints for session establishment
2. **Headless Operation**: No browser windows or user interaction required
3. **Development Efficiency**: Auto-approval of all authentication requests
4. **Container Friendly**: Works seamlessly in Docker/Podman environments

### What It's NOT

- ❌ Real authentication or security
- ❌ Production access control
- ❌ User management system
- ❌ Actual OAuth 2.0 implementation

### What It IS

- ✅ Session establishment helper for Claude Code
- ✅ OAuth-like endpoint structure
- ✅ Auto-approval authentication flow
- ✅ Headless environment solution

## Technical Implementation

### Authentication Endpoints

The server provides these OAuth-compatible endpoints:

```
GET  /.well-known/oauth-authorization-server  # OAuth server discovery
GET  /.well-known/oauth-protected-resource    # Resource server info
POST /register                                # Client registration
GET  /auth                                    # Authorization endpoint
POST /token                                   # Token endpoint
```

### Authentication Flow

1. **Client Registration**: Auto-generates client credentials
2. **Authorization Request**: Auto-approves and redirects with auth code
3. **Token Exchange**: Issues access tokens without validation
4. **Session Established**: Claude Code can now use MCP tools

### Key Features

- **Auto-Approval**: All requests automatically approved
- **No Browser Required**: Direct HTTP redirects instead of browser opening
- **Stateless**: No session storage or user management
- **OAuth-Compatible**: Follows OAuth 2.0 patterns for compatibility

## Configuration

### Environment Variables

```bash
MCP_SERVER_PORT=8002        # Server port
LOG_LEVEL=INFO              # Logging level
```

### Route Registration

Authentication routes are automatically registered with the FastMCP app:

```python
auth_routes = [
    Route('/.well-known/oauth-authorization-server', oauth_authorization_server, methods=['GET']),
    Route('/.well-known/oauth-protected-resource', oauth_protected_resource, methods=['GET']),
    Route('/register', register_client, methods=['POST']),
    Route('/auth', authorize, methods=['GET']),
    Route('/token', token_endpoint, methods=['POST']),
]
```

## Usage with Claude Code

### Connection Process

1. Claude Code discovers MCP Tools server
2. Attempts OAuth authentication
3. Gets auto-approved credentials
4. Establishes HTTP transport session
5. Can now call MCP tools

### Example Claude Code Config

```json
{
  "mcpServers": {
    "mcp-tools": {
      "command": "python",
      "args": ["-m", "mcp_tools_server"],
      "env": {
        "MCP_SERVER_PORT": "8002"
      }
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**: Change `MCP_SERVER_PORT` if 8002 is in use
2. **Authentication Timeout**: Check server logs for endpoint access
3. **Route Registration**: Verify auth routes are properly added to FastMCP app

### Debug Logging

Enable debug logging to see authentication flow:

```bash
export LOG_LEVEL=DEBUG
python -m mcp_tools_server
```

### Testing Authentication

Test the endpoints manually:

```bash
# Check OAuth server discovery
curl http://localhost:8002/.well-known/oauth-authorization-server

# Test authorization endpoint
curl "http://localhost:8002/auth?client_id=test&redirect_uri=http://localhost:3000/callback&state=test123"

# Test token endpoint
curl -X POST http://localhost:8002/token \
  -d "grant_type=authorization_code&code=test&client_id=test&client_secret=test"
```

## Security Considerations

### Development Use Only

This shell authentication is designed for:

- ✅ Development environments
- ✅ Local testing
- ✅ Containerized development
- ✅ CI/CD pipelines

### NOT for Production

Never use shell authentication for:

- ❌ Production deployments
- ❌ Sensitive data access
- ❌ Multi-user environments
- ❌ Internet-facing services

## Integration with Other MCP Servers

This shell authentication pattern can be copied to other MCP servers:

1. Copy the authentication endpoint functions
2. Add route registration to main()
3. Update CLAUDE.md documentation
4. Test with Claude Code

## Related Documentation

- **MCP Guidelines**: FastMCP documentation
- **Claude Code**: Integration patterns
- **Container Deployment**: Docker/Podman setup
- **Development Tools**: Personal dev tools integration

## Version History

- **v1.0**: Initial shell authentication implementation
- **v1.1**: Added comprehensive documentation and troubleshooting
- **v1.2**: Enhanced OAuth compatibility and error handling