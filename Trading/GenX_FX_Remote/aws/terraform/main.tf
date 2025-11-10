# AMP System AWS Infrastructure
# Optimized for AWS Free Tier
# Uses Terraform to provision infrastructure as code

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"  # Free tier region
}

# Variables
variable "project_name" {
  description = "Name of the AMP trading system project"
  type        = string
  default     = "amp-trading-system"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

# Data sources
data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "state"
    values = ["available"]
  }
}

# VPC and Networking
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "${var.project_name}-vpc"
    Environment = var.environment
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true

  tags = {
    Name        = "${var.project_name}-public-subnet"
    Environment = var.environment
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name        = "${var.project_name}-igw"
    Environment = var.environment
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name        = "${var.project_name}-public-rt"
    Environment = var.environment
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# Security Group
resource "aws_security_group" "amp_sg" {
  name        = "${var.project_name}-sg"
  description = "Security group for AMP trading system"
  vpc_id      = aws_vpc.main.id

  # SSH access
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # AMP API
  ingress {
    description = "AMP API"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Grafana
  ingress {
    description = "Grafana Dashboard"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-sg"
    Environment = var.environment
  }
}

# Key Pair
resource "aws_key_pair" "amp_key" {
  key_name   = "${var.project_name}-key"
  public_key = file("${path.module}/../../amp-trading-key.pub")
}

# EC2 Instance (t2.micro - free tier eligible)
resource "aws_instance" "amp_server" {
  ami                    = data.aws_ami.amazon_linux_2.id
  instance_type          = "t2.micro"  # Free tier eligible
  key_name               = aws_key_pair.amp_key.key_name
  vpc_security_group_ids = [aws_security_group.amp_sg.id]
  subnet_id              = aws_subnet.public.id

  user_data = templatefile("${path.module}/user_data.sh", {
    project_name = var.project_name
    environment  = var.environment
  })

  root_block_device {
    volume_size = 8  # Free tier: 30GB total
    volume_type = "gp2"
  }

  tags = {
    Name        = "${var.project_name}-server"
    Environment = var.environment
  }
}

# S3 Bucket for data storage
resource "aws_s3_bucket" "amp_data" {
  bucket = "${var.project_name}-data-${random_string.bucket_suffix.result}"

  tags = {
    Name        = "${var.project_name}-data-bucket"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "amp_data" {
  bucket = aws_s3_bucket.amp_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "amp_data" {
  bucket = aws_s3_bucket.amp_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# DynamoDB Table
resource "aws_dynamodb_table" "amp_data" {
  name           = "${var.project_name}-data"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    Name        = "${var.project_name}-data-table"
    Environment = var.environment
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "amp_logs" {
  name              = "/aws/${var.project_name}"
  retention_in_days = 7

  tags = {
    Name        = "${var.project_name}-logs"
    Environment = var.environment
  }
}

# Random string for bucket naming
resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# Outputs
output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.amp_server.id
}

output "public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.amp_server.public_ip
}

output "s3_bucket" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.amp_data.bucket
}

output "dynamodb_table" {
  description = "Name of the DynamoDB table"
  value       = aws_dynamodb_table.amp_data.name
}

output "cloudwatch_log_group" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.amp_logs.name
}

output "access_urls" {
  description = "Access URLs for the AMP system"
  value = {
    amp_api   = "http://${aws_instance.amp_server.public_ip}:8000/health"
    grafana   = "http://${aws_instance.amp_server.public_ip}:3000"
    ssh       = "ssh -i ${path.module}/../../amp-trading-key.pem ec2-user@${aws_instance.amp_server.public_ip}"
  }
}