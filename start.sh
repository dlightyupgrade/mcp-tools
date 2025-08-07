#!/bin/bash
# start.sh - Start MCP Tools Server Container with Semantic Versioning
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
DEFAULT_PORT="8002"

# Get current version
get_current_version() {
    if [[ -f "version.py" ]]; then
        python3 version.py current 2>/dev/null | grep -oP 'Current version: \K.*' || echo "latest"
    else
        echo "latest"
    fi
}

# Parse command line arguments
VERSION="latest"
PORT="$DEFAULT_PORT"

while [[ $# -gt 0 ]]; do
    case $1 in
        --version)
            VERSION="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --help|-h)
            cat << EOF
MCP Tools Container Start Script

Usage: $0 [options]

Options:
  --version VERSION   Use specific image version (default: auto-detect or latest)
  --port PORT        Host port for MCP Tools (default: $DEFAULT_PORT)
  --help, -h         Show this help message

Examples:
  $0                     # Start with auto-detected version
  $0 --version 2.1.0     # Start with specific version  
  $0 --port 8003         # Start on different port

Notes:
  - Automatically detects version from version.py if available
  - Uses semantic versioning for container images
  - Prefers podman over docker for container management
EOF
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Auto-detect version if using default
if [[ "$VERSION" == "latest" ]]; then
    VERSION=$(get_current_version)
    if [[ "$VERSION" != "latest" ]]; then
        echo -e "${BLUE}🔍 Auto-detected version: ${VERSION}${NC}"
    fi
fi

IMAGE_NAME="mcp-tools:${VERSION}"

echo -e "${BLUE}🚀 Starting MCP Tools Server${NC}"
echo -e "${BLUE}Container: ${CONTAINER_NAME}${NC}"
echo -e "${BLUE}Image: ${IMAGE_NAME}${NC}"
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