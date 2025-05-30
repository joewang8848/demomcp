#!/usr/bin/env bash
set -euo pipefail

echo "🧹 Starting MCP Gateway cleanup and build..."

# 1) Stop & remove compose-managed containers, local images, and volumes
echo "📦 Stopping docker-compose services..."
docker-compose down --rmi local -v

# 2) Remove any stray containers based on mcp-gateway-v2:latest
echo "🗑️  Removing stray containers..."
docker ps -a --filter ancestor=mcp-gateway-v2:latest -q \
  | xargs -r docker rm -f

# 3) Force-remove the mcp-gateway-v2:latest image
echo "🔥 Removing old image..."
docker rmi -f mcp-gateway-v2:latest || true

# 4) Prune dangling volumes
echo "🧽 Pruning dangling volumes..."
docker volume prune -f

# 5) Rebuild the image
echo "🏗️  Building new image: mcp-gateway-v2:latest..."
docker build -t mcp-gateway-v2:latest .

# 6) Bring the stack back up
echo "🚀 Starting services..."
docker-compose up -d

echo "✅ Cleanup, build and run complete."
echo "🌐 MCP Gateway available at: http://localhost:8001"
echo "📦 Configuration packaged in image: gateway.yml, tool.yml"