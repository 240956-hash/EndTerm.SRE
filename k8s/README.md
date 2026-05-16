# Kubernetes (Section 6.2)

Декларативное развертывание по архитектуре:

```
User → Frontend (Nginx) → API Gateway
              |
+--------------------------------------+
| Auth | Product | Order | Payment     |
| Notification | User Profile          |
+--------------------------------------+
              |
        PostgreSQL / Redis
```

## Компоненты K8s

| Тип | Ресурсы |
|-----|---------|
| **Pods** | Контейнеры внутри каждого Deployment |
| **Deployments** | frontend, api-gateway, 6 микросервисов, postgres, redis, prometheus, grafana |
| **Services** | ClusterIP для внутренних, NodePort для api-gateway (:30080) |
| **ConfigMaps** | `shop-config` — URL сервисов, DB host |
| **Secrets** | `shop-secrets` — пароли PostgreSQL |
| **HPA** | order-service, product-service, payment-service (CPU 70%) |
| **Self-healing** | `livenessProbe` + `readinessProbe` на всех сервисах |
| **PVC** | postgres-pvc для данных БД |

## Быстрый деплой

```bash
./scripts/deploy-k8s.sh
```

Или вручную:

```bash
colima start --kubernetes
docker context use colima
./scripts/build-images.sh
kubectl apply -k k8s/
kubectl get pods -n shop-sre -w
```

## Доступ

```bash
# NodePort (Colima)
open http://localhost:30080

# Port-forward
kubectl port-forward -n shop-sre svc/api-gateway 8088:80
```

## Проверка auto-scaling

```bash
kubectl get hpa -n shop-sre
kubectl top pods -n shop-sre
```

## Файлы

- `namespace.yaml` — namespace `shop-sre`
- `configmap.yaml` / `secret.yaml`
- `postgres-redis.yaml` — PostgreSQL + Redis
- `microservices.yaml` — 6 микросервисов
- `gateway-frontend.yaml` — Frontend + API Gateway (точка входа)
- `hpa.yaml` — HorizontalPodAutoscaler
- `monitoring.yaml` — Prometheus + Grafana в кластере
