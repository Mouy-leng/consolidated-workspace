@echo off
echo Deploying GenX_FX to Production...

REM Build and push to Docker Hub
docker build -f Dockerfile.fix -t keamouyleng/genx_docker:latest .
docker push keamouyleng/genx_docker:latest

REM Deploy to Railway (if configured)
if exist railway.json (
    railway up
    echo Deployed to Railway
)

REM Deploy to local production
docker stop genx-fx-working 2>nul
docker rm genx-fx-working 2>nul
docker run -d --name genx-fx-production -p 8080:8080 --restart unless-stopped keamouyleng/genx_docker:latest

echo Production deployment complete!
echo Access: http://localhost:8080
echo Signals: http://localhost:8080/MT4_Signals.csv