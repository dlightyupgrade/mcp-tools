#!/bin/bash
# MCP Tools - Container Stop Script
# Purpose: Stop MCP Tools multi-server architecture

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🛑 Stopping MCP Tools Multi-Server Architecture"
echo ""

cd "$PROJECT_DIR"

# Stop services gracefully
echo "🔧 Stopping services..."
podman-compose stop

echo ""
echo "🧹 Removing containers..."
podman-compose down

echo ""
echo "✅ MCP Tools multi-server architecture stopped!"