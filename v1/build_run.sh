#!/usr/bin/env bash
set -euo pipefail

# 1) Stop & remove compose-managed containers, local images, and volumes
docker-compose down --rmi local -v

# 2) Remove any stray containers based on demomcp:latest
docker ps -a --filter ancestor=demomcp:latest -q \
  | xargs -r docker rm -f

# 3) Force-remove the demomcp:latest image
docker rmi -f demomcp:latest || true

# 4) Prune dangling volumes
docker volume prune -f

# 5) Rebuild the image
docker build -t demomcp:latest .

# 6) Bring the stack back up
docker-compose up -d

echo "✅ Cleanup, build and run complete."
