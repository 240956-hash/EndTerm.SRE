output "instance_public_ip" {
  description = "Public IP of deployed instance"
  value       = aws_instance.app_vm.public_ip
}

output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.app_vm.id
}
