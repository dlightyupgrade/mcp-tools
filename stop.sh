#!/bin/bash
# stop.sh - Stop MCP Tools Server Container
# Following MCP Guidelines: Containerized server with easy start/stop scripts

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="mcp-tools"

echo -e "${BLUE}🛑 Stopping MCP Tools Server${NC}"
echo -e "${BLUE}Container: ${CONTAINER_NAME}${NC}"
echo ""

# Check if container is running
if ! podman ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${YELLOW}⚠️  Container '${CONTAINER_NAME}' is not running${NC}"
    
    # Check if container exists but is stopped
    if podman ps -a --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        echo -e "${BLUE}🗑️  Removing stopped container...${NC}"
        podman rm "${CONTAINER_NAME}"
        echo -e "${GREEN}✅ Stopped container removed${NC}"
    else
        echo -e "${BLUE}ℹ️  No container to stop${NC}"
    fi
    exit 0
fi

# Stop the container
echo -e "${BLUE}🛑 Stopping container...${NC}"
podman stop "${CONTAINER_NAME}"

echo -e "${GREEN}✅ MCP Tools Server stopped successfully${NC}"
echo ""
echo -e "${BLUE}🚀 To start again:${NC} ./start.sh"