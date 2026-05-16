#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

services=(
  auth-service
  product-service
  order-service
  user-service
  payment-service
  notification-service
)

for svc in "${services[@]}"; do
  docker build -f "services/${svc}/Dockerfile" -t "shop/${svc}:latest" .
done

docker build -f api-gateway/Dockerfile -t shop/api-gateway:latest .
docker build -f frontend/Dockerfile -t shop/frontend:latest .

echo "Images built under shop/*:latest"
