#!/usr/bin/env python3
"""
AWS Deployment Status Checker
Checks the current state of AWS deployment and provides guidance
"""

import os
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def check_aws_cli():
    """Check if AWS CLI is installed"""
    try:
        result = subprocess.run(['aws', '--version'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def check_aws_credentials():
    """Check if AWS credentials are configured"""
    try:
        result = subprocess.run(['aws', 'sts', 'get-caller-identity'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def check_terraform():
    """Check if Terraform is installed"""
    try:
        result = subprocess.run(['terraform', '--version'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def check_ssh_key():
    """Check if SSH key exists"""
    key_files = [
        "amp-trading-key",
        "amp-trading-key.pem",
        "aws/amp-trading-key",
        "aws/amp-trading-key.pem"
    ]
    
    for key_file in key_files:
        if Path(key_file).exists():
            return True
    return False

def check_aws_resources():
    """Check if AWS resources exist"""
    try:
        # Check for instance info
        if Path("instance_info.json").exists():
            with open("instance_info.json", "r") as f:
                instance_info = json.load(f)
            return instance_info
        return None
    except Exception:
        return None

def show_deployment_status():
    """Show current deployment status"""
    print("🚀 AMP System AWS Deployment Status")
    print("=" * 50)
    print(f"⏰ Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check prerequisites
    print("\n📋 Prerequisites Check:")
    print("-" * 30)
    
    aws_cli_installed = check_aws_cli()
    print(f"   AWS CLI: {'✅ Installed' if aws_cli_installed else '❌ Not installed'}")
    
    aws_creds_configured = check_aws_credentials()
    print(f"   AWS Credentials: {'✅ Configured' if aws_creds_configured else '❌ Not configured'}")
    
    terraform_installed = check_terraform()
    print(f"   Terraform: {'✅ Installed' if terraform_installed else '❌ Not installed'}")
    
    ssh_key_exists = check_ssh_key()
    print(f"   SSH Key: {'✅ Found' if ssh_key_exists else '❌ Not found'}")
    
    # Check AWS resources
    print("\n🐳 AWS Resources:")
    print("-" * 20)
    
    instance_info = check_aws_resources()
    if instance_info:
        print(f"   EC2 Instance: ✅ Deployed")
        print(f"   Instance ID: {instance_info.get('instance_id', 'N/A')}")
        print(f"   Public IP: {instance_info.get('public_ip', 'N/A')}")
        print(f"   Key Name: {instance_info.get('key_name', 'N/A')}")
    else:
        print("   EC2 Instance: ❌ Not deployed")
    
    # Check configuration files
    print("\n🔧 Configuration Files:")
    print("-" * 25)
    
    config_files = [
        "aws/amp-deploy.sh",
        "aws/terraform/main.tf",
        "aws/terraform/user_data.sh",
        "AWS_DEPLOYMENT_GUIDE.md"
    ]
    
    for config_file in config_files:
        exists = Path(config_file).exists()
        print(f"   {config_file}: {'✅ Found' if exists else '❌ Missing'}")
    
    return {
        "aws_cli": aws_cli_installed,
        "aws_creds": aws_creds_configured,
        "terraform": terraform_installed,
        "ssh_key": ssh_key_exists,
        "deployed": instance_info is not None,
        "instance_info": instance_info
    }

def show_deployment_options():
    """Show deployment options"""
    print("\n🚀 Deployment Options:")
    print("=" * 25)
    
    print("1. 🎯 Automated Script Deployment (Recommended)")
    print("   - Simple and fast")
    print("   - One-command deployment")
    print("   - Automatic configuration")
    print("   Command: ./aws/amp-deploy.sh")
    
    print("\n2. 🏗️ Terraform Infrastructure as Code")
    print("   - Infrastructure as code")
    print("   - Version controlled")
    print("   - Reproducible deployments")
    print("   Commands:")
    print("     cd aws/terraform/")
    print("     terraform init")
    print("     terraform apply")
    
    print("\n3. 📖 Manual AWS Console Deployment")
    print("   - Step-by-step process")
    print("   - Full control")
    print("   - Educational experience")
    print("   Follow: AWS_DEPLOYMENT_GUIDE.md")

def show_next_steps(status):
    """Show next steps based on current status"""
    print("\n📋 Next Steps:")
    print("=" * 15)
    
    if not status["aws_cli"]:
        print("1. 🔧 Install AWS CLI:")
        print("   curl 'https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip' -o 'awscliv2.zip'")
        print("   unzip awscliv2.zip")
        print("   sudo ./aws/install")
    
    if not status["aws_creds"]:
        print("2. 🔑 Configure AWS Credentials:")
        print("   aws configure")
        print("   # Enter your AWS Access Key ID")
        print("   # Enter your AWS Secret Access Key")
        print("   # Enter your default region (us-east-1)")
    
    if not status["ssh_key"]:
        print("3. 🔐 Generate SSH Key Pair:")
        print("   ssh-keygen -t rsa -b 4096 -f amp-trading-key -N ''")
    
    if status["aws_cli"] and status["aws_creds"] and status["ssh_key"]:
        print("4. 🚀 Deploy to AWS:")
        print("   cd aws/")
        print("   ./amp-deploy.sh")
    
    if status["deployed"]:
        print("5. ✅ System Deployed!")
        instance_info = status["instance_info"]
        public_ip = instance_info.get("public_ip", "N/A")
        key_name = instance_info.get("key_name", "N/A")
        
        print(f"   🌐 Access URLs:")
        print(f"      - AMP API: http://{public_ip}:8000/health")
        print(f"      - Grafana: http://{public_ip}:3000")
        print(f"   🔑 SSH Access:")
        print(f"      ssh -i {key_name}.pem ec2-user@{public_ip}")

def show_free_tier_info():
    """Show AWS free tier information"""
    print("\n💰 AWS Free Tier Information:")
    print("=" * 35)
    
    print("✅ Free Tier Limits:")
    print("   - EC2: 750 hours/month of t2.micro")
    print("   - S3: 5GB storage")
    print("   - DynamoDB: 25GB storage, 25 WCU/RCU")
    print("   - CloudWatch: 5GB data ingestion")
    print("   - Data Transfer: 15GB outbound")
    
    print("\n💡 Cost Optimization Tips:")
    print("   - Stop instance when not in use")
    print("   - Monitor usage in AWS Cost Explorer")
    print("   - Set up billing alerts")
    print("   - Use CloudWatch for monitoring")

def show_access_info(status):
    """Show access information if deployed"""
    if status["deployed"]:
        instance_info = status["instance_info"]
        public_ip = instance_info.get("public_ip", "N/A")
        key_name = instance_info.get("key_name", "N/A")
        
        print("\n🔗 Access Information:")
        print("=" * 25)
        print(f"🌐 Public IP: {public_ip}")
        print(f"🔑 Key File: {key_name}.pem")
        print("")
        print("📊 Access URLs:")
        print(f"   - AMP API: http://{public_ip}:8000/health")
        print(f"   - Grafana: http://{public_ip}:3000")
        print("   - Grafana Credentials: admin / amp_admin")
        print("")
        print("⚡ AMP CLI Commands:")
        print(f"   - Status: ssh -i {key_name}.pem ec2-user@{public_ip} 'docker exec -it amp-trading-system amp status'")
        print(f"   - Monitor: ssh -i {key_name}.pem ec2-user@{public_ip} 'docker exec -it amp-trading-system amp monitor --dashboard'")
        print(f"   - Logs: ssh -i {key_name}.pem ec2-user@{public_ip} 'docker logs amp-trading-system'")

def main():
    """Main function"""
    # Show deployment status
    status = show_deployment_status()
    
    # Show deployment options
    show_deployment_options()
    
    # Show next steps
    show_next_steps(status)
    
    # Show free tier info
    show_free_tier_info()
    
    # Show access info if deployed
    show_access_info(status)
    
    print("\n" + "=" * 50)
    print("🎯 Ready to deploy your AMP system to AWS!")
    print("📖 For detailed instructions, see: AWS_DEPLOYMENT_GUIDE.md")

if __name__ == "__main__":
    main()