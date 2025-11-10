#!/bin/bash

# GenX_FX Deployment Script for Google VM
# Run this script on your VM to deploy the backend

set -e

echo "🚀 Starting GenX_FX Deployment..."

# Update system and install dependencies
echo "📦 Installing dependencies..."
sudo apt update
sudo apt install -y docker.io docker-compose curl wget git nginx certbot python3-certbot-nginx

# Start and enable Docker
echo "🐳 Setting up Docker..."
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER

# Create project directory
echo "📁 Setting up project directory..."
mkdir -p ~/GenX_FX
cd ~/GenX_FX

# Create .env file with your credentials
echo "🔧 Creating .env file..."
cat > .env << 'EOF'
# === Docker Registry Credentials ===
DOCKER_USERNAME=genxapitrading@gmail.com
DOCKER_PASSWORD=Leng12345@#$01
DOCKER_IMAGE=keamouyleng/genx_docker
DOCKER_TAG=latest

# === API Keys ===
GEMINI_API_KEY=AIzaSyDnjcaXnDpm1TzmIAV7EnoluI6w7wGBagM
VANTAGE_ALPHAVANTAGE_API_KEY=B8E5RHKWZIE1JLK5
NEWS_API_KEY=5919b24ab55d4ad0a71734fc2ef3542f
NEWSDATA_API_KEY=pub_7b251a30c9634424b45bc966fc3356da
FINNHUB_API_KEY=d1a1nh9r01qltimul4f0d1a1nh9r01qltimul4fg

# === Telegram Credentials ===
TELEGRAM_BOT_TOKEN=8193742894:AAHewpntyYzCaPLyP1yhPZda9eLcDDKBO8Y
TELEGRAM_USER_ID=1725480922

# === Gmail Credentials ===
GMAIL_USER=lengkundee01@gmail.com
GMAIL_PASSWORD=Leng12345@#$01
GMAIL_APP_API_KEY=iwvb_zhme_jcga_qwks

# === Reddit Credentials ===
REDDIT_CLIENT_ID=gevc7tz7VJG-dFveG3QLJA
REDDIT_CLIENT_SECRET=3ELg5NbaxAUJDpitlv_fPb7uFm7i3A
REDDIT_USERNAME=Mysterious_Set1324
REDDIT_PASSWORD=Leng12345@#$01
REDDIT_USER_AGENT=GenX-Trading-Bot/1.0

# === FXCM Credentials ===
FXCM_USERNAME=D27739526
FXCM_PASSWORD=cpsj1
FXCM_CONNECTION_TYPE=Demo
FXCM_URL=www.fxcorporate.com/Hosts.jsp

# === Security Keys ===
JWT_SECRET_KEY=f1a6828476f6892bfc9fa6601810147c2a595ab08a0bd8b8263344921dc87102

# === Feature Flags ===
ENABLE_NEWS_ANALYSIS=true
ENABLE_REDDIT_ANALYSIS=true
ENABLE_WEBSOCKET_FEED=true
API_PROVIDER=gemini
EOF

# Clone the repository
echo "📥 Cloning GenX_FX repository..."
git clone https://github.com/Mouy-leng/GenX_FX.git temp_genx
cp -r temp_genx/* .
rm -rf temp_genx

# Create Docker Compose file for production with HTTPS
echo "🐳 Creating Docker Compose configuration..."
cat > docker-compose.production.yml << 'EOF'
version: '3.8'

services:
  genx-backend:
    build: .
    container_name: genx-backend
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      - NODE_ENV=production
    env_file:
      - .env
    volumes:
      - ./expert-advisors:/app/expert-advisors
      - ./scripts:/app/scripts
      - ./logs:/app/logs
    networks:
      - genx-network

  nginx:
    image: nginx:alpine
    container_name: genx-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - genx-backend
    networks:
      - genx-network

networks:
  genx-network:
    driver: bridge

volumes:
  logs:
EOF

# Create Nginx configuration for HTTPS
echo "🌐 Creating Nginx configuration..."
cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream genx_backend {
        server genx-backend:8080;
    }

    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name _;
        return 301 https://$host$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl;
        server_name _;

        # Self-signed certificate (replace with Let's Encrypt later)
        ssl_certificate /etc/nginx/ssl/nginx.crt;
        ssl_certificate_key /etc/nginx/ssl/nginx.key;

        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        location / {
            proxy_pass http://genx_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /ws {
            proxy_pass http://genx_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
        }
    }
}
EOF

# Create SSL directory and generate self-signed certificate
echo "🔒 Setting up SSL certificate..."
mkdir -p ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/nginx.key -out ssl/nginx.crt \
    -subj "/C=US/ST=State/L=City/O=GenX/CN=localhost"

# Set proper permissions
chmod 600 ssl/nginx.key
chmod 644 ssl/nginx.crt

# Build and start the containers
echo "🏗️ Building and starting containers..."
sudo docker-compose -f docker-compose.production.yml up -d --build

# Wait for containers to start
echo "⏳ Waiting for containers to start..."
sleep 30

# Check container status
echo "📊 Container status:"
sudo docker ps

# Show logs
echo "📋 Recent logs:"
sudo docker-compose -f docker-compose.production.yml logs --tail=20

echo "✅ Deployment completed!"
echo "🌐 Your GenX_FX backend is now running on:"
echo "   - HTTP: http://$(curl -s ifconfig.me):80 (redirects to HTTPS)"
echo "   - HTTPS: https://$(curl -s ifconfig.me):443"
echo "   - Backend API: http://$(curl -s ifconfig.me):8080"

echo "📁 EA Scripts are available in: ~/GenX_FX/expert-advisors/"
echo "📁 Additional scripts in: ~/GenX_FX/scripts/"

echo "🔧 To view logs: sudo docker-compose -f docker-compose.production.yml logs -f"
echo "🔧 To stop: sudo docker-compose -f docker-compose.production.yml down"
echo "🔧 To restart: sudo docker-compose -f docker-compose.production.yml restart"