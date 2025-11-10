#!/bin/bash

# GenX FX - VPS Deployment Script
# ================================

set -e

echo "🚀 GenX FX Trading Platform - VPS Deployment"
echo "============================================="

# Configuration
REPO_URL="https://github.com/Mouy-leng/GenX_FX.git"
DEPLOY_DIR="/opt/genx-trading"
BACKUP_DIR="/opt/backups/genx-fx"
LOG_FILE="/var/log/genx-deployment.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a $LOG_FILE
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a $LOG_FILE
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a $LOG_FILE
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error "This script should not be run as root for security reasons"
   exit 1
fi

log "Starting VPS deployment process..."

# Update system packages
log "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    log "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
else
    log "✅ Docker already installed"
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    log "🔧 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    log "✅ Docker Compose already installed"
fi

# Install additional tools
log "🔧 Installing additional tools..."
sudo apt install -y git curl htop nginx certbot python3-certbot-nginx

# Create deployment directory
log "📁 Setting up deployment directory..."
sudo mkdir -p $DEPLOY_DIR
sudo chown $USER:$USER $DEPLOY_DIR

# Create backup directory
sudo mkdir -p $BACKUP_DIR
sudo chown $USER:$USER $BACKUP_DIR

# Clone or update repository
if [ -d "$DEPLOY_DIR/.git" ]; then
    log "🔄 Updating existing repository..."
    cd $DEPLOY_DIR
    git fetch --all
    git reset --hard origin/feature/fxcm-integration-with-spreadsheet
else
    log "📥 Cloning repository..."
    git clone $REPO_URL $DEPLOY_DIR
    cd $DEPLOY_DIR
    git checkout feature/fxcm-integration-with-spreadsheet
fi

# Copy environment template
if [ ! -f "$DEPLOY_DIR/.env" ]; then
    log "📝 Creating environment file..."
    cp $DEPLOY_DIR/.env.example $DEPLOY_DIR/.env
    warning "Please edit $DEPLOY_DIR/.env file with your API keys"
fi

# Build and start services
log "🏗️ Building and starting Docker services..."
cd $DEPLOY_DIR

# Stop existing services
docker-compose -f docker-compose.production.yml down 2>/dev/null || true

# Build and start databases first
log "🗄️ Starting database services..."
docker-compose -f docker-compose.production.yml up -d postgres mongo redis

# Wait for databases to be ready
log "⏳ Waiting for databases to be ready..."
sleep 30

# Start API service
log "🚀 Starting API service..."
docker-compose -f docker-compose.production.yml up -d api

# Start additional services
log "🤖 Starting bot services..."
docker-compose -f docker-compose.production.yml up -d discord_bot telegram_bot websocket_feed

# Setup Nginx reverse proxy
log "🌐 Setting up Nginx reverse proxy..."
sudo tee /etc/nginx/sites-available/genx-trading > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/genx-trading /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Setup firewall
log "🔥 Setting up firewall..."
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# Create backup script
log "💾 Creating backup script..."
sudo tee /usr/local/bin/backup-genx.sh > /dev/null <<'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/genx-fx"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR/$DATE

# Backup database
docker exec genx-postgres pg_dump -U genx_user genx_trading > $BACKUP_DIR/$DATE/postgres_backup.sql
docker exec genx-mongo mongodump --db genx_trading --out $BACKUP_DIR/$DATE/

# Backup configuration
cp -r /opt/genx-trading/.env $BACKUP_DIR/$DATE/
cp -r /opt/genx-trading/logs $BACKUP_DIR/$DATE/ 2>/dev/null || true

# Create archive
tar -czf $BACKUP_DIR/genx_backup_$DATE.tar.gz -C $BACKUP_DIR $DATE
rm -rf $BACKUP_DIR/$DATE

# Keep only last 7 backups
ls -t $BACKUP_DIR/genx_backup_*.tar.gz | tail -n +8 | xargs -r rm

echo "Backup completed: genx_backup_$DATE.tar.gz"
EOF

sudo chmod +x /usr/local/bin/backup-genx.sh

# Setup cron job for daily backups
log "⏰ Setting up daily backups..."
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-genx.sh") | crontab -

# Create monitoring script
log "📊 Creating monitoring script..."
sudo tee /usr/local/bin/monitor-genx.sh > /dev/null <<'EOF'
#!/bin/bash

check_service() {
    local service=$1
    if docker ps | grep -q $service; then
        echo "✅ $service is running"
        return 0
    else
        echo "❌ $service is not running"
        return 1
    fi
}

echo "GenX FX Health Check - $(date)"
echo "================================"

# Check all services
services=("genx-postgres" "genx-mongo" "genx-redis" "genx-api")
all_healthy=true

for service in "${services[@]}"; do
    if ! check_service $service; then
        all_healthy=false
    fi
done

# Check API health
if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ API health endpoint is responding"
else
    echo "❌ API health endpoint is not responding"
    all_healthy=false
fi

if $all_healthy; then
    echo "🎉 All services are healthy!"
    exit 0
else
    echo "⚠️  Some services have issues"
    exit 1
fi
EOF

sudo chmod +x /usr/local/bin/monitor-genx.sh

# Setup monitoring cron job
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/monitor-genx.sh >> /var/log/genx-health.log") | crontab -

# Create systemd service for auto-restart
log "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/genx-trading.service > /dev/null <<EOF
[Unit]
Description=GenX FX Trading Platform
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$DEPLOY_DIR
ExecStart=/usr/local/bin/docker-compose -f docker-compose.production.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.production.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable genx-trading

# Final health check
log "🔍 Running final health check..."
sleep 10
if /usr/local/bin/monitor-genx.sh; then
    log "🎉 Deployment completed successfully!"
    log "📊 Access your application at: http://$(curl -s ifconfig.me):8000"
    log "📋 Local access: http://localhost:8000"
    log "📖 API Documentation: http://localhost:8000/docs"
    log "🔧 Logs: docker-compose -f $DEPLOY_DIR/docker-compose.production.yml logs"
    log "💾 Backups: /opt/backups/genx-fx/"
    log "📈 Monitoring: /usr/local/bin/monitor-genx.sh"
else
    error "Deployment completed but some services may not be healthy"
    error "Check logs: docker-compose -f $DEPLOY_DIR/docker-compose.production.yml logs"
fi

log "🔐 Security recommendations:"
log "  1. Update .env file with real API keys"
log "  2. Setup SSL certificate: sudo certbot --nginx -d your-domain.com"
log "  3. Change default passwords in .env"
log "  4. Setup monitoring and alerting"
log "  5. Configure backup retention policy"

echo ""
echo "Deployment Summary:"
echo "=================="
echo "🌐 Application: http://$(curl -s ifconfig.me 2>/dev/null || echo 'YOUR-SERVER-IP'):8000"
echo "📚 API Docs: http://$(curl -s ifconfig.me 2>/dev/null || echo 'YOUR-SERVER-IP'):8000/docs"
echo "🔍 Health Check: http://$(curl -s ifconfig.me 2>/dev/null || echo 'YOUR-SERVER-IP'):8000/health"
echo "📁 Deploy Dir: $DEPLOY_DIR"
echo "💾 Backups: $BACKUP_DIR"
echo "📋 Logs: /var/log/genx-*.log"
