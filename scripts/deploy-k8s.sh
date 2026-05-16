#!/usr/bin/env bash
# Deploy full stack to Kubernetes (Colima/minikube)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "[k8s] Checking cluster..."
if ! kubectl cluster-info >/dev/null 2>&1; then
  echo "[k8s] Starting Colima with Kubernetes..."
  colima start --kubernetes --cpu 4 --memory 8 -f || colima start --kubernetes
  docker context use colima
fi

echo "[k8s] Building images..."
./scripts/build-images.sh

echo "[k8s] Installing metrics-server (for HPA)..."
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml 2>/dev/null || true
kubectl patch deployment metrics-server -n kube-system --type='json' \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]' 2>/dev/null || true

echo "[k8s] Applying manifests..."
kubectl apply -k k8s/

echo "[k8s] Waiting for api-gateway..."
kubectl rollout status deployment/api-gateway -n shop-sre --timeout=180s
kubectl rollout status deployment/order-service -n shop-sre --timeout=180s

echo ""
echo "[k8s] Deployment complete."
echo "  kubectl get pods -n shop-sre"
echo "  kubectl get svc -n shop-sre"
echo "  App (NodePort): http://localhost:30080"
echo "  Or port-forward: kubectl port-forward -n shop-sre svc/api-gateway 8088:80"
