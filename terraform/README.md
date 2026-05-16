# Terraform — VM Provisioning (Assignment 5)

## Что создаётся

| Ресурс | Описание |
|--------|----------|
| `aws_security_group.shop-sre-sg` | HTTP 80, Grafana 3000, Prometheus 9090, SSH 22 |
| `aws_instance.app_vm` | EC2 VM для развёртывания стека (Docker через `user_data`) |

## Статус (текущий state)

VM **уже была создана** ранее через `terraform apply`:

| Параметр | Значение |
|----------|----------|
| Instance ID | `i-0a7b32129f3d78e01` |
| Public IP | `54.197.13.101` |
| Region | `us-east-1` |

Проверить актуальные значения:

```bash
cd terraform
terraform output instance_public_ip
terraform output instance_id
```

## Развёртывание

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars  # если есть
# Заполните ami_id и key_name
terraform init
terraform plan
terraform apply
```

## После создания VM

```bash
ssh -i shop.pem ubuntu@$(terraform output -raw instance_public_ip)
# На VM: клонировать репозиторий и запустить Ansible
ansible-playbook -i ansible/inventory.ini ansible/site.yml
```

## Outputs

- `instance_public_ip` — публичный IP для UI (порт 80/8088 после деплоя)
- `instance_id` — ID инстанса AWS
