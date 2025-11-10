# GenX FX Trading Platform - Exness Broker VPS Deployment Guide

This guide provides step-by-step instructions for deploying the GenX FX Trading Platform on a VPS with Exness broker integration.

## 🎯 Overview

This deployment replaces your existing Google Cloud VM with a dedicated VPS optimized for Exness broker trading, providing:
- Lower latency to Exness servers
- Dedicated resources for trading operations
- 24/7 automated trading capability
- Enhanced security and monitoring

## 🏗️ Architecture

```
┌─────────────────────────────────┐
│         VPS (DigitalOcean)      │
│                                 │
│  ┌─────────────────────────────┐│
│  │      GenX AI Backend       ││
│  │   - AI Models              ││
│  │   - Signal Generation      ││
│  │   - Risk Management        ││
│  └─────────────────────────────┘│
│                                 │
│  ┌─────────────────────────────┐│
│  │    EA Communication        ││
│  │   - Socket Server (9090)   ││
│  │   - Signal Broadcasting    ││
│  └─────────────────────────────┘│
│                                 │
│  ┌─────────────────────────────┐│
│  │      Database Layer        ││
│  │   - PostgreSQL             ││
│  │   - Redis Cache            ││
│  └─────────────────────────────┘│
│                                 │
│  ┌─────────────────────────────┐│
│  │    Monitoring Stack        ││
│  │   - Prometheus             ││
│  │   - Grafana                ││
│  └─────────────────────────────┘│
└─────────────────────────────────┘
         │
         │ TCP/IP Socket (9090)
         ▼
┌─────────────────────────────────┐
│      Exness MT4/MT5 Terminal   │
│                                 │
│  ┌─────────────────────────────┐│
│  │     GenX AI EA             ││
│  │  - Socket Client           ││
│  │  - Trade Execution         ││
│  │  - Risk Management         ││
│  └─────────────────────────────┘│
└─────────────────────────────────┘
```

## 📋 Prerequisites

### 1. VPS Requirements
- **Provider**: DigitalOcean (recommended), Vultr, Linode, or AWS
- **Specifications**: 
  - 4 vCPUs minimum
  - 8GB RAM minimum
  - 160GB SSD storage
  - Ubuntu 22.04 LTS
- **Location**: Choose closest to Exness servers (London/New York)
- **Network**: High-bandwidth connection

### 2. Exness Account
- Active Exness trading account (demo or live)
- Account credentials
- MT4 or MT5 terminal access
- API access (optional)

### 3. Domain Name (Optional)
- Domain for SSL certificate
- DNS management access

## 🚀 Deployment Steps

### Step 1: Create VPS

#### DigitalOcean Setup
```bash
# Create droplet
doctl compute droplet create genx-exness-vps \
  --image ubuntu-22-04-x64 \
  --size c-4 \
  --region lon1 \
  --ssh-keys $SSH_KEY_ID \
  --enable-monitoring \
  --enable-backups

# Get droplet IP
doctl compute droplet get genx-exness-vps --format ID,PublicIPv4
```

#### Alternative: Manual VPS Creation
1. Sign up for VPS provider
2. Create new VPS with Ubuntu 22.04
3. Note the IP address
4. Configure SSH access

### Step 2: Initial VPS Setup

```bash
# Connect to VPS
ssh root@YOUR_VPS_IP

# Update system
apt update && apt upgrade -y

# Create non-root user (optional but recommended)
adduser genx
usermod -aG sudo genx
su - genx
```

### Step 3: Deploy GenX FX

```bash
# Clone repository
git clone https://github.com/Mouy-leng/GenX-EA_Script.git
cd GenX-EA_Script

# Run setup script
chmod +x deploy/setup-exness-vps.sh
sudo ./deploy/setup-exness-vps.sh
```

### Step 4: Configure Environment

```bash
# Edit environment file
nano /opt/genx-trading/.env
```

#### Essential Exness Configuration
```env
# Exness Account Settings
EXNESS_ACCOUNT_TYPE=real  # or demo
EXNESS_LOGIN=YOUR_EXNESS_ACCOUNT_NUMBER
EXNESS_PASSWORD=YOUR_EXNESS_PASSWORD
EXNESS_SERVER=Exness-MT4Live  # or Exness-MT5Live
EXNESS_TERMINAL=MT5  # MT4 or MT5

# EA Communication
EA_SERVER_HOST=0.0.0.0
EA_SERVER_PORT=9090
EA_MAGIC_NUMBER=123456
EA_DEFAULT_LOT_SIZE=0.1
EA_MAX_RISK_PER_TRADE=0.02

# VPS Network
VPS_PUBLIC_IP=YOUR_VPS_IP_HERE
```

### Step 5: Setup Exness MT4/MT5

#### Option A: Local MT4/MT5 Installation
1. Download Exness MT4/MT5 from broker
2. Install on your local machine
3. Login with Exness credentials
4. Copy EA files to Experts folder

#### Option B: VPS MT4/MT5 Installation (Recommended)
1. Install Windows VPS or use Exness VPS
2. Install MT4/MT5 on VPS
3. Configure EA for low-latency trading

### Step 6: Deploy Expert Advisor

#### Copy EA Files
```bash
# Copy EA to MT4/MT5 Experts folder
cp expert-advisors/GenX_AI_EA.mq5 /path/to/MT5/Experts/
cp expert-advisors/GenX_Gold_Master_EA.mq4 /path/to/MT4/Experts/
```

#### EA Configuration
```cpp
// EA Settings for Exness
input string AI_Server_Host = "YOUR_VPS_IP";
input int    AI_Server_Port = 9090;
input int    Magic_Number = 123456;
input double Default_Lot_Size = 0.1;
input double Max_Risk_Per_Trade = 0.02;
input bool   Enable_Auto_Trading = true;
```

### Step 7: Start Services

```bash
# Start GenX trading system
sudo systemctl start genx-trading

# Check status
sudo systemctl status genx-trading

# View logs
sudo journalctl -u genx-trading -f
```

### Step 8: Verify Deployment

```bash
# Check API health
curl http://YOUR_VPS_IP:8000/health

# Check EA connection
netstat -tlnp | grep 9090

# Check database
sudo -u postgres psql -d genx_trading -c "SELECT COUNT(*) FROM trades;"
```

## 🔧 Configuration Details

### Exness-Specific Settings

#### Server Selection
- **Europe**: Exness-MT4Live, Exness-MT5Live
- **Asia**: Exness-MT4Live-Asia, Exness-MT5Live-Asia
- **Demo**: Exness-MT4Demo, Exness-MT5Demo

#### Trading Parameters
```env
# Risk Management
EA_MAX_RISK_PER_TRADE=0.02      # 2% per trade
EA_MAX_TOTAL_RISK=0.06          # 6% total
EA_STOP_LOSS_METHOD=atr_based   # ATR-based stops
EA_TAKE_PROFIT_RATIO=2.0        # 1:2 risk-reward

# Trading Instruments
TRADING_SYMBOLS=EURUSD,GBPUSD,USDJPY,USDCHF,AUDUSD,USDCAD,NZDUSD,XAUUSD
TRADING_TIMEFRAMES=M15,H1,H4,D1
```

### Network Configuration

#### Firewall Rules
```bash
# Allow EA communication
sudo ufw allow from ANY to any port 9090

# Allow API access
sudo ufw allow 8000

# Allow SSH
sudo ufw allow 22

# Enable firewall
sudo ufw enable
```

#### SSL Certificate (Optional)
```bash
# Install SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring and Maintenance

### Health Checks
```bash
# Manual health check
/opt/genx-trading/scripts/health-check.sh

# Automated monitoring
sudo systemctl status genx-monitor

# View monitoring logs
tail -f /opt/genx-trading/logs/monitor.log
```

### Backup Strategy
```bash
# Manual backup
/opt/genx-trading/scripts/backup.sh

# Automated daily backups
sudo systemctl status genx-backup.timer

# List backups
ls -la /opt/genx-trading/backups/
```

### Performance Monitoring
```bash
# System resources
htop

# Disk usage
df -h

# Memory usage
free -h

# Network connections
netstat -tlnp
```

## 🔒 Security Best Practices

### 1. Access Control
```bash
# Disable root SSH
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no

# Use SSH keys only
# Set: PasswordAuthentication no

# Restart SSH
sudo systemctl restart ssh
```

### 2. Firewall Configuration
```bash
# Configure UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from YOUR_IP to any port 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8000
sudo ufw allow 9090
sudo ufw enable
```

### 3. Regular Updates
```bash
# Setup automatic updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure unattended-upgrades
```

## 🚨 Troubleshooting

### Common Issues

#### 1. EA Connection Failed
```bash
# Check if server is listening
netstat -tlnp | grep 9090

# Check firewall
sudo ufw status

# Test connection
telnet YOUR_VPS_IP 9090
```

#### 2. High Latency
```bash
# Test network latency
ping YOUR_VPS_IP

# Check for packet loss
mtr YOUR_VPS_IP

# Consider VPS location closer to Exness servers
```

#### 3. Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
sudo -u postgres psql -d genx_trading

# Check logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

#### 4. Memory Issues
```bash
# Check memory usage
free -h

# Check swap
swapon --show

# Add swap if needed
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Log Locations
- **GenX Trading**: `/opt/genx-trading/logs/`
- **System**: `/var/log/syslog`
- **Nginx**: `/var/log/nginx/`
- **PostgreSQL**: `/var/log/postgresql/`
- **Redis**: `/var/log/redis/`

## 📈 Performance Optimization

### 1. Database Optimization
```sql
-- Create indexes for frequent queries
CREATE INDEX idx_trades_timestamp ON trades(created_at);
CREATE INDEX idx_signals_instrument ON signals(instrument);
CREATE INDEX idx_trades_magic_number ON trades(magic_number);
```

### 2. Redis Caching
```python
# Cache market data
import redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Cache for 5 seconds
def get_cached_price(instrument):
    cached = redis_client.get(f"price:{instrument}")
    if cached:
        return json.loads(cached)
    # Fetch from API and cache
```

### 3. System Tuning
```bash
# Optimize PostgreSQL
sudo nano /etc/postgresql/*/main/postgresql.conf
# shared_buffers = 256MB
# effective_cache_size = 1GB
# work_mem = 4MB

# Restart PostgreSQL
sudo systemctl restart postgresql
```

## 🔄 Migration from Google Cloud

### 1. Data Migration
```bash
# Export data from Google Cloud
pg_dump -h OLD_DB_HOST -U OLD_USER OLD_DB > backup.sql

# Import to new VPS
psql -h localhost -U genx_user genx_trading < backup.sql
```

### 2. Configuration Migration
```bash
# Copy configuration files
scp user@OLD_VM:/path/to/config/* /opt/genx-trading/config/

# Update environment variables
nano /opt/genx-trading/.env
```

### 3. Model Migration
```bash
# Copy trained models
scp -r user@OLD_VM:/path/to/models/* /opt/genx-trading/models/

# Verify model integrity
python -c "import joblib; joblib.load('/opt/genx-trading/models/ensemble_model.joblib')"
```

## 📞 Support and Maintenance

### Regular Maintenance Tasks
1. **Daily**: Check system logs and trading performance
2. **Weekly**: Review backup integrity and update system packages
3. **Monthly**: Analyze trading performance and optimize models
4. **Quarterly**: Security audit and performance review

### Monitoring Alerts
- Set up email/SMS alerts for critical issues
- Monitor trading performance metrics
- Track system resource usage
- Monitor network connectivity

### Backup Verification
```bash
# Test backup restoration
sudo -u postgres psql -d genx_trading -c "SELECT COUNT(*) FROM trades;"

# Verify model files
ls -la /opt/genx-trading/models/
```

## 🎯 Success Metrics

### Performance Indicators
- **Latency**: <10ms to Exness servers
- **Uptime**: >99.9%
- **Trade Execution**: <100ms
- **Signal Accuracy**: >65%
- **System Resources**: <80% utilization

### Trading Metrics
- **Win Rate**: Track in trading dashboard
- **Profit Factor**: Monitor risk-reward ratios
- **Drawdown**: Keep below 10%
- **Sharpe Ratio**: Aim for >1.5

---

## 📝 Quick Reference Commands

```bash
# Start/Stop Services
sudo systemctl start genx-trading
sudo systemctl stop genx-trading
sudo systemctl restart genx-trading

# Check Status
sudo systemctl status genx-trading
sudo journalctl -u genx-trading -f

# Backup
/opt/genx-trading/scripts/backup.sh

# Health Check
/opt/genx-trading/scripts/health-check.sh

# Update System
sudo apt update && sudo apt upgrade -y

# View Logs
tail -f /opt/genx-trading/logs/genx-backend.log
```

This deployment guide provides a complete setup for running GenX FX with Exness broker on a dedicated VPS, offering improved performance, reliability, and security compared to the previous Google Cloud setup. 