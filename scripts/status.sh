#!/bin/bash
# MCP Tools - Status Check Script
# Purpose: Check status of MCP Tools multi-server architecture

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "📊 MCP Tools Multi-Server Status"
echo ""

cd "$PROJECT_DIR"

echo "🐳 Container Status:"
podman-compose ps

echo ""
echo "🏥 Service Health Checks:"

services=("coordinator:8002" "tools:8003" "reports:8004")
for service_port in "${services[@]}"; do
    service="${service_port%:*}"
    port="${service_port#*:}"
    
    echo -n "  ${service}: "
    if curl -s -f "http://localhost:${port}/health" >/dev/null 2>&1; then
        echo "✅ Healthy (http://localhost:${port})"
    else
        echo "❌ Not responding"
    fi
done

echo ""
echo "📋 Quick Commands:"
echo "  ./scripts/start.sh    # Start all services"
echo "  ./scripts/stop.sh     # Stop all services"
echo "  podman-compose logs   # View logs"