# 🚀 GenX FX AWS Free Tier Deployment Guide

Deploy your GenX FX trading system to AWS using the **free tier** - perfect for getting started without any costs!

## 🎯 What You'll Get

- **EC2 t2.micro instance** (750 hours/month FREE)
- **Public IP address** for web access
- **CloudWatch monitoring** (5GB logs/month FREE)
- **15GB data transfer/month** (FREE)
- **Estimated cost after free tier**: $5-15/month

---

## 📋 Prerequisites

### 1. AWS Account Setup
```bash
# Create AWS account at https://aws.amazon.com/free/
# Enable billing alerts in AWS Console
```

### 2. Install AWS CLI
```bash
# Windows (PowerShell)
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi

# macOS
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### 3. Configure AWS Credentials
```bash
aws configure
# Enter your:
# - AWS Access Key ID
# - AWS Secret Access Key  
# - Default region: us-east-1
# - Default output format: json
```

---

## 🚀 Quick Deployment (5 Minutes)

### Option 1: One-Command Deployment
```bash
# Clone repository (replace YourUsername with your actual GitHub username!)
git clone https://github.com/YourUsername/GenX_FX.git
cd GenX_FX

# Make script executable
chmod +x deploy/free-tier-deploy.sh

# Deploy with auto-generated key pair
./deploy/free-tier-deploy.sh --key-pair genx-fx-key
```

### Option 2: Step-by-Step Deployment
```bash
# 1. Create EC2 key pair
aws ec2 create-key-pair --key-name genx-fx-key --region us-east-1 --query 'KeyMaterial' --output text > genx-fx-key.pem
chmod 400 genx-fx-key.pem

# 2. Deploy CloudFormation stack
aws cloudformation deploy \
  --template-file deploy/aws-free-tier-deploy.yml \
  --stack-name production-genx-fx-free-tier \
  --parameter-overrides Environment=production KeyPairName=genx-fx-key \
  --capabilities CAPABILITY_IAM \
  --region us-east-1

# 3. Get deployment info
aws cloudformation describe-stacks \
  --stack-name production-genx-fx-free-tier \
  --region us-east-1 \
  --query 'Stacks[0].Outputs'
```

---

## 📊 Deployment Output

After successful deployment, you'll see:

```bash
=== GenX FX Deployment Information ===
Instance IP: 54.123.456.789
Application URL: http://54.123.456.789:8000
SSH Command: ssh -i genx-fx-key.pem ec2-user@54.123.456.789

=== Next Steps ===
1. Wait 5-10 minutes for the application to start
2. Access your trading platform at: http://54.123.456.789:8000
3. SSH into the server: ssh -i genx-fx-key.pem ec2-user@54.123.456.789
4. Check logs: docker logs genx-fx
```

---

## 🔧 Post-Deployment Setup

### 1. Access Your Trading Platform
```bash
# Open in browser
http://YOUR_INSTANCE_IP:8000

# Check API health
curl http://YOUR_INSTANCE_IP:8000/health
```

### 2. SSH into Your Server
```bash
ssh -i genx-fx-key.pem ec2-user@YOUR_INSTANCE_IP

# Check application status
docker ps
docker logs genx-fx

# View real-time logs
docker logs -f genx-fx
```

### 3. Configure Trading Settings
```bash
# SSH into server
ssh -i genx-fx-key.pem ec2-user@YOUR_INSTANCE_IP

# Edit environment variables
cd GenX_FX
nano .env

# Restart application
docker restart genx-fx
```

---

## 📈 Monitoring & Management

### 1. CloudWatch Monitoring
```bash
# View CPU usage
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=YOUR_INSTANCE_ID \
  --statistics Average \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T23:59:59Z \
  --period 3600

# View application logs
aws logs describe-log-streams --log-group-name /aws/ec2/production-genx-fx
```

### 2. Application Management
```bash
# SSH into server
ssh -i genx-fx-key.pem ec2-user@YOUR_INSTANCE_IP

# Restart application
docker restart genx-fx

# Update application
cd GenX_FX
git pull origin main
docker build -f Dockerfile.free-tier -t genx-fx .
docker stop genx-fx
docker rm genx-fx
docker run -d -p 8000:8000 --name genx-fx --restart unless-stopped genx-fx

# View trading signals
curl http://localhost:8000/MT4_Signals.csv
```

### 3. Backup Your Data
```bash
# Run the auto-generated backup script
./backup-genx.sh

# Manual backup
docker exec genx-fx tar czf - /app/data /app/logs > genx-backup-$(date +%Y%m%d).tar.gz
```

---

## 💰 Cost Management

### Free Tier Limits (12 months)
- ✅ **EC2 t2.micro**: 750 hours/month
- ✅ **EBS Storage**: 30GB/month
- ✅ **Data Transfer**: 15GB/month
- ✅ **CloudWatch**: 5GB logs/month

### Cost After Free Tier
- **EC2 t2.micro**: ~$8.50/month
- **EBS Storage (20GB)**: ~$2/month
- **Data Transfer**: ~$1-3/month
- **Total**: ~$12-15/month

### Cost Optimization Tips
```bash
# 1. Stop instance when not trading
aws ec2 stop-instances --instance-ids YOUR_INSTANCE_ID

# 2. Start instance when needed
aws ec2 start-instances --instance-ids YOUR_INSTANCE_ID

# 3. Set up billing alerts
aws budgets create-budget --account-id YOUR_ACCOUNT_ID --budget file://budget.json

# 4. Monitor usage
aws ce get-cost-and-usage --time-period Start=2024-01-01,End=2024-01-31 --granularity MONTHLY --metrics BlendedCost
```

---

## 🔒 Security Best Practices

### 1. Secure SSH Access
```bash
# Restrict SSH to your IP only
aws ec2 authorize-security-group-ingress \
  --group-id YOUR_SECURITY_GROUP_ID \
  --protocol tcp \
  --port 22 \
  --cidr YOUR_IP_ADDRESS/32
```

### 2. Enable HTTPS (Optional)
```bash
# Install Let's Encrypt SSL certificate
ssh -i genx-fx-key.pem ec2-user@YOUR_INSTANCE_IP

sudo yum install -y certbot
sudo certbot certonly --standalone -d your-domain.com

# Update Docker container to use SSL
docker run -d -p 443:8000 -v /etc/letsencrypt:/etc/letsencrypt --name genx-fx-ssl genx-fx
```

### 3. Regular Updates
```bash
# SSH into server
ssh -i genx-fx-key.pem ec2-user@YOUR_INSTANCE_IP

# Update system
sudo yum update -y

# Update application
cd GenX_FX
git pull origin main
docker build -f Dockerfile.free-tier -t genx-fx .
docker restart genx-fx
```

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. Application Not Starting
```bash
# Check Docker logs
docker logs genx-fx

# Check if port is open
netstat -tlnp | grep 8000

# Restart Docker service
sudo service docker restart
docker restart genx-fx
```

#### 2. Can't Access Web Interface
```bash
# Check security group rules
aws ec2 describe-security-groups --group-ids YOUR_SECURITY_GROUP_ID

# Test connectivity
curl -I http://YOUR_INSTANCE_IP:8000
```

#### 3. High CPU Usage
```bash
# Check resource usage
docker stats genx-fx

# Scale down if needed
docker update --cpus="0.5" --memory="512m" genx-fx
```

#### 4. Out of Disk Space
```bash
# Check disk usage
df -h

# Clean up Docker
docker system prune -a

# Clean up logs
sudo find /var/log -name "*.log" -type f -mtime +7 -delete
```

---

## 📞 Support & Next Steps

### Getting Help
1. **Check logs**: `docker logs genx-fx`
2. **GitHub Issues**: Open an issue with error details
3. **AWS Support**: Use AWS free tier support for infrastructure issues

### Scaling Up
When you're ready to scale beyond free tier:

1. **Upgrade to t3.small** for better performance
2. **Add RDS database** for production data storage
3. **Use Application Load Balancer** for high availability
4. **Deploy to multiple regions** for global access

### Advanced Features
```bash
# Enable auto-scaling
aws autoscaling create-auto-scaling-group --auto-scaling-group-name genx-fx-asg

# Add CloudFront CDN
aws cloudfront create-distribution --distribution-config file://cloudfront-config.json

# Set up Route 53 DNS
aws route53 create-hosted-zone --name your-domain.com
```

---

## 🎉 Success! Your GenX FX is Live!

🌐 **Access your trading platform**: `http://YOUR_INSTANCE_IP:8000`  
📊 **Download signals**: `http://YOUR_INSTANCE_IP:8000/MT4_Signals.csv`  
🔧 **SSH access**: `ssh -i genx-fx-key.pem ec2-user@YOUR_INSTANCE_IP`  

**Happy Trading with GenX FX on AWS! 🚀**

---

## 🧹 Deleting the Stack (to avoid charges)

If you want to remove all AWS resources and avoid any charges, run:

```bash
aws cloudformation delete-stack --stack-name production-genx-fx-free-tier --region us-east-1
```

---

## ⚠️ IMPORTANT REMINDERS

- In your CloudFormation template, update the repository URL to your actual GitHub username.
- Always use Dockerfile.free-tier for AWS Free Tier deployments.