#!/usr/bin/env bash
# Docker Swarm deploy — build images, tag for stack, deploy
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! docker info 2>/dev/null | grep -q 'Swarm: active'; then
  echo "[swarm] Initializing swarm..."
  docker swarm init 2>/dev/null || true
fi

echo "[swarm] Building images via compose..."
docker compose build

tag() {
  local src="sreendterm-${1}:latest"
  local dst="shop-${1}:local"
  if docker image inspect "$src" >/dev/null 2>&1; then
    docker tag "$src" "$dst"
    echo "  tagged $dst"
  else
    echo "  WARN: missing $src — run: docker compose build"
  fi
}

echo "[swarm] Tagging images for docker-stack.yml..."
tag api-gateway
tag frontend
tag auth-service
tag product-service
tag order-service
tag user-service
tag payment-service
tag notification-service

echo "[swarm] Deploying stack 'shop'..."
docker stack deploy -c docker-stack.yml shop

echo ""
echo "[swarm] Waiting 15s for services..."
sleep 15
docker stack services shop
