resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags = { Name = "main" }
}

variable "environment" {
  type        = string
  description = "Deployment environment"
  default     = "dev"
}

output "vpc_id" {
  value = aws_vpc.main.id
}
