#!/bin/bash
# start.sh - Start MCP Tools Server Container
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
IMAGE_NAME="mcp-tools:latest"
PORT="8002"

echo -e "${BLUE}🚀 Starting MCP Tools Server${NC}"
echo -e "${BLUE}Container: ${CONTAINER_NAME}${NC}"
echo -e "${BLUE}Port: ${PORT}${NC}"
echo ""

# Check if container is already running
if podman ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${YELLOW}⚠️  Container '${CONTAINER_NAME}' is already running${NC}"
    echo -e "${BLUE}Use: ${NC}podman logs ${CONTAINER_NAME} ${BLUE}to view logs${NC}"
    echo -e "${BLUE}Use: ${NC}./stop.sh ${BLUE}to stop the container${NC}"
    exit 0
fi

# Check if port is available
if lsof -Pi :${PORT} -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}❌ Port ${PORT} is already in use${NC}"
    echo -e "${BLUE}Check what's using the port:${NC} lsof -i :${PORT}"
    exit 1
fi

# Build image if it doesn't exist
if ! podman images --format "{{.Repository}}:{{.Tag}}" | grep -q "^${IMAGE_NAME}$"; then
    echo -e "${YELLOW}📦 Building ${IMAGE_NAME}...${NC}"
    podman build -t "${IMAGE_NAME}" .
fi

# Start container
echo -e "${GREEN}🚀 Starting container...${NC}"
podman run \
    --rm \
    -d \
    --name "${CONTAINER_NAME}" \
    -p "${PORT}:${PORT}" \
    -e MCP_SERVER_PORT="${PORT}" \
    -e LOG_LEVEL=INFO \
    "${IMAGE_NAME}"

# Wait for container to be ready
echo -e "${BLUE}⏳ Waiting for server to be ready...${NC}"
for i in {1..30}; do
    if curl -sf http://localhost:${PORT}/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ MCP Tools Server is ready!${NC}"
        echo ""
        echo -e "${BLUE}🔗 Endpoints:${NC}"
        echo -e "  Health: http://localhost:${PORT}/health"
        echo -e "  MCP:    http://localhost:${PORT}/mcp"
        echo ""
        echo -e "${BLUE}📋 Management:${NC}"
        echo -e "  Logs:   podman logs ${CONTAINER_NAME}"
        echo -e "  Stop:   ./stop.sh"
        echo ""
        exit 0
    fi
    sleep 1
done

echo -e "${RED}❌ Server failed to start or is not responding${NC}"
echo -e "${BLUE}Check logs:${NC} podman logs ${CONTAINER_NAME}"
exit 1