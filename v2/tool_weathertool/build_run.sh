#!/usr/bin/env bash
set -euo pipefail
docker-compose down --rmi local -v
docker ps -a --filter ancestor=weather-tool:latest -q | xargs -r docker rm -f
docker rmi -f weather-tool:latest || true
docker build -t weather-tool:latest .
docker-compose up -d
echo "✅ Weather Tool running at: http://localhost:9001"