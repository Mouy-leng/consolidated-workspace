@echo off
echo Deploying GenX_FX to Cloud...

REM Push to Docker Hub
docker tag genx-enhanced keamouyleng/genx_docker:enhanced
docker push keamouyleng/genx_docker:enhanced

REM Deploy to Railway (Free Tier)
echo Visit: https://railway.app
echo 1. Connect GitHub repo
echo 2. Deploy from Docker image: keamouyleng/genx_docker:enhanced
echo 3. Set environment variables from .env.template

REM Deploy to Render (Free Tier)
echo Visit: https://render.com
echo 1. New Web Service
echo 2. Docker image: keamouyleng/genx_docker:enhanced
echo 3. Port: 8080

echo Cloud deployment ready!
echo Your trading will run 24/7 without laptop