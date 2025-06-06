#!/usr/bin/env bash
set -euo pipefail
docker-compose down --rmi local -v
docker ps -a --filter ancestor=storage-service:latest -q | xargs -r docker rm -f
docker rmi -f storage-service:latest || true
docker build -t storage-service:latest .
docker-compose up -d
echo "✅ Storage Service running at: http://192.168.4.154:8002"