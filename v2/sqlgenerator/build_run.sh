# === build_run.sh ===
#!/usr/bin/env bash
set -euo pipefail
docker-compose down --rmi local -v
docker ps -a --filter ancestor=sqlgen-tool:latest -q | xargs -r docker rm -f
docker rmi -f sqlgen-tool:latest || true
docker build -t sqlgen-tool:latest .
docker-compose up -d
echo "✅ SQL Generator Tool running at: http://localhost:9002"