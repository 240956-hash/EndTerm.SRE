# SRE End Term Project — Shop Microservices Platform

Comprehensive Site Reliability Engineering implementation for a distributed microservices system (Docker Compose, Docker Swarm, Kubernetes, Terraform, Ansible, Prometheus, Grafana).

## Microservices (6+)

| Service | Port | Role |
|---------|------|------|
| auth-service | 8001 | Authentication |
| product-service | 8002 | Product catalog |
| order-service | 8003 | Order processing |
| user-service | 8004 | User profile |
| payment-service | 8005 | Payment simulation |
| notification-service | 8006 | Email/alert via Redis |

Supporting: Frontend (Nginx), API Gateway, PostgreSQL, Redis, Prometheus, Grafana, cAdvisor.

## Quick start (Docker Compose)

```bash
./scripts/start-stack.sh
```

Or manually (if Docker Desktop is not running, use [Colima](https://github.com/abiosoft/colima): `colima start && docker context use colima`):

```bash
cp .env.example .env
docker compose up --build -d
```

| URL | Purpose |
|-----|---------|
| http://localhost:8088 | Web UI + API |
| http://localhost:9091 | Prometheus |
| http://localhost:3001 | Grafana (admin/admin) |
| http://localhost:9093 | Alertmanager |

## SLI / SLO (Assignment 2)

Grafana dashboard: http://localhost:3001/d/assignment2-sli-slo (folder **SRE End Term**)

See [docs/sli-slo.md](docs/sli-slo.md).

## Incident simulation (Assignment 4)

1. Set wrong DB host: `ORDER_DB_HOST=postgres-wrong` in `.env`
2. Recreate order service: `docker compose up -d --force-recreate order-service`
3. Create order from UI or:
   ```bash
   curl -X POST http://localhost:8088/api/orders/orders \
     -H 'Content-Type: application/json' \
     -d '{"user_id":1,"product_id":2,"quantity":1}'
   ```
4. Observe `order_create_failures_total` in Prometheus
5. Restore `ORDER_DB_HOST=postgres` and recreate service

Reports: [reports/assignment4-incident-report.md](reports/assignment4-incident-report.md), [reports/assignment4-postmortem.md](reports/assignment4-postmortem.md)

## Docker Swarm

```bash
docker swarm init
docker compose build
docker stack deploy -c docker-stack.yml shop
docker stack services shop
```

## Kubernetes (6.2)

Полная архитектура: **User → Frontend → API Gateway → 6 микросервисов → PostgreSQL/Redis**

Pods, Deployments, Services, ConfigMaps, Secrets, HPA, liveness/readiness.

```bash
./scripts/deploy-k8s.sh
# UI: http://localhost:30080
```

Details: [k8s/README.md](k8s/README.md)

## Terraform VM

EC2 VM для продакшен-деплоя — см. [terraform/README.md](terraform/README.md).  
`terraform output instance_public_ip`

## Grafana dashboards

| Dashboard | URL |
|-----------|-----|
| SLI/SLO (Assignment 2) | http://localhost:3001/d/assignment2-sli-slo |
| System metrics (CPU/RAM/RPS) | http://localhost:3001/d/system-metrics |
| Overview | http://localhost:3001/d/assignment45-overview |

## Terraform (AWS EC2)

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

Update `terraform.tfvars` with valid `ami_id` and `key_name`.

## Ansible

```bash
ansible-playbook -i ansible/inventory.ini ansible/site.yml
ansible-playbook -i ansible/inventory.ini ansible/monitoring.yml
```

## Automation & capacity planning

- Health checks on all services (`/health`)
- `restart: unless-stopped` in Compose
- Alerts in `prometheus/alerts.yml`
- Load test: `python scripts/load_test.py --url "http://localhost:8088/api/products/products" --concurrency 50 --requests 2000`
- Pre-deploy validation: `python scripts/validate_env.py`

See [reports/assignment6.md](reports/assignment6.md) and [reports/endterm-report.md](reports/endterm-report.md).

## Project structure

```
├── services/          # 6 FastAPI microservices
├── api-gateway/       # Nginx reverse proxy
├── frontend/          # Demo UI
├── docker-compose.yml
├── docker-stack.yml   # Swarm
├── k8s/               # Kubernetes manifests
├── ansible/           # Playbooks
├── terraform/         # AWS provisioning
├── prometheus/        # Metrics + alerts
├── grafana/           # Dashboards
├── docs/sli-slo.md
└── reports/           # Incident + end term docs
```

## Submission

For the course deliverable: capture screenshots (containers, Prometheus targets, Grafana, incident before/after) and submit a **PDF with your Git repository link**.
