#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! docker info >/dev/null 2>&1; then
  echo "[start-stack] Docker not running — starting Colima..."
  colima start -f --cpu 4 --memory 6 || colima start
  docker context use colima
fi

cp -n .env.example .env 2>/dev/null || true
docker compose up --build -d
echo ""
echo "Stack ready:"
echo "  UI:         http://localhost:8088"
echo "  Prometheus: http://localhost:9091"
echo "  Grafana:    http://localhost:3001  (admin/admin)"
echo "  Alertmanager: http://localhost:9093"
