# MCP Tools - Container-ready streaming HTTP server
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install system dependencies for tool execution
RUN apk add --no-cache \
    git \
    bash \
    curl \
    jq \
    openssh-client

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY dist/ ./dist/

# Create non-root user
RUN addgroup -g 1001 -S mcp && \
    adduser -S mcp -u 1001

# Set ownership
RUN chown -R mcp:mcp /app
USER mcp

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Environment variables
ENV NODE_ENV=production
ENV PORT=8002
ENV MCP_TRANSPORT=http

# Start server with streaming HTTP by default
CMD ["node", "dist/index.js"]