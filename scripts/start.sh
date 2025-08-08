#!/bin/bash
# MCP Tools - Container Start Script
# Purpose: Start MCP Tools multi-server architecture using podman-compose

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🚀 Starting MCP Tools Multi-Server Architecture"
echo "📁 Project Directory: $PROJECT_DIR"
echo ""

# Check if podman-compose is available
if ! command -v podman-compose >/dev/null 2>&1; then
    echo "❌ podman-compose not found. Installing..."
    pip install podman-compose || {
        echo "❌ Failed to install podman-compose"
        echo "💡 Try: pip3 install podman-compose"
        exit 1
    }
fi

cd "$PROJECT_DIR"

echo "🔧 Building and starting containers..."
podman-compose up --build -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

echo ""
echo "🏥 Checking service health..."

# Check each service
services=("mcp-coordinator:8002" "mcp-tools:8003" "mcp-reports:8004")
for service_port in "${services[@]}"; do
    service="${service_port%:*}"
    port="${service_port#*:}"
    
    echo -n "  ${service}: "
    if curl -s -f "http://localhost:${port}/health" >/dev/null 2>&1; then
        echo "✅ Healthy"
    else
        echo "❌ Not responding"
    fi
done

echo ""
echo "📊 Service URLs:"
echo "  🎯 Coordinator: http://localhost:8002"
echo "  🛠️  Tools:       http://localhost:8003" 
echo "  📈 Reports:     http://localhost:8004"
echo ""
echo "📋 Management Commands:"
echo "  podman-compose ps     # Show running services"
echo "  podman-compose logs   # Show all logs"
echo "  podman-compose stop   # Stop services"
echo "  podman-compose down   # Stop and remove containers"
echo ""
echo "✅ MCP Tools multi-server architecture started!"