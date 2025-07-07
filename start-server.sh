#!/bin/bash

# MCP Tools Server Startup Script
# Starts the server on port 8002 (default MCP Tools port)

cd "$(dirname "$0")"

echo "🔍 Checking if server is already running..."
if pgrep -f "node dist/index.js" > /dev/null; then
    echo "⚠️  MCP Tools server is already running"
    echo "📊 Process info:"
    ps aux | grep "node dist/index.js" | grep -v grep
    exit 1
fi

echo "🚀 Starting MCP Tools Server on port 8002..."
echo "📡 Endpoint will be: http://localhost:8002/mcp"

# Start in background and log to file
PORT=8002 nohup node dist/index.js > server.log 2>&1 &
SERVER_PID=$!

echo "✅ Server started with PID: $SERVER_PID"
echo "📝 Logs are written to: $(pwd)/server.log"

# Wait a moment and check if it started successfully
sleep 2

if ps -p $SERVER_PID > /dev/null; then
    echo "🎉 Server is running successfully!"
    echo "🔗 Test with: curl http://localhost:8002/mcp"
else
    echo "❌ Server failed to start. Check server.log for details."
    cat server.log
    exit 1
fi