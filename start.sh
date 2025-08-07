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
        python3 version.py current 2>/dev/null | sed -n 's/Current version: //p' | head -1 | tr -d ' \n' || echo "latest"
    else
        echo "latest"
    fi
}

# Parse command line arguments  
VERSION=""  # Will auto-detect current release version
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
  --version VERSION   Use specific release image version (default: auto-detect current release)
  --port PORT        Host port for MCP Tools (default: $DEFAULT_PORT)
  --help, -h         Show this help message

Examples:
  $0                     # Start with current release version (recommended)
  $0 --version 2.1.0     # Start with specific release version  
  $0 --port 8003         # Start on different port

Build Management:
  Use ./build.sh to create release images:
  - ./build.sh                    # Build current version
  - ./build.sh --version patch    # Bump patch and build
  - ./build.sh --version minor    # Bump minor and build

Notes:
  - Only starts existing release images - does NOT auto-build
  - Auto-detects current release version from version.py
  - Use semantic versioning tags (not 'latest') for production
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

# Auto-detect current release version if not specified
if [[ -z "$VERSION" ]]; then
    VERSION=$(get_current_version)
    if [[ "$VERSION" != "latest" ]]; then
        echo -e "${BLUE}🔍 Auto-detected release version: ${VERSION}${NC}"
    else
        echo -e "${YELLOW}⚠️  No release version found, falling back to latest${NC}"
        VERSION="latest"
    fi
fi

IMAGE_NAME="localhost/mcp-tools:${VERSION}"

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

# Check if release image exists - do NOT auto-build
if ! podman images --format "{{.Repository}}:{{.Tag}}" | grep -q "localhost/mcp-tools:${VERSION}$"; then
    echo -e "${RED}❌ Release image ${IMAGE_NAME} not found${NC}"
    echo -e "${BLUE}Available mcp-tools images:${NC}"
    podman images | grep mcp-tools || echo "  No mcp-tools images found"
    echo ""
    echo -e "${BLUE}To build the release image:${NC}"
    echo "  ./build.sh                    # Build current version"
    echo "  ./build.sh --version patch    # Bump patch version and build"
    echo "  ./build.sh --version minor    # Bump minor version and build"
    echo ""
    exit 1
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