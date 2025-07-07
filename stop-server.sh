#!/bin/bash

# MCP Tools Server Stop Script

echo "🛑 Stopping MCP Tools Server..."

# Find and kill the server process
if pgrep -f "node dist/index.js" > /dev/null; then
    echo "📊 Found running server process:"
    ps aux | grep "node dist/index.js" | grep -v grep
    
    echo "🔄 Stopping server..."
    pkill -f "node dist/index.js"
    
    # Wait for process to stop
    sleep 2
    
    if pgrep -f "node dist/index.js" > /dev/null; then
        echo "⚠️  Process still running, force killing..."
        pkill -9 -f "node dist/index.js"
        sleep 1
    fi
    
    if ! pgrep -f "node dist/index.js" > /dev/null; then
        echo "✅ Server stopped successfully"
    else
        echo "❌ Failed to stop server"
        exit 1
    fi
else
    echo "ℹ️  No MCP Tools server process found"
fi