@echo off
echo ========================================
echo   GenX FX Remote Control System
echo ========================================
echo.

echo Installing/updating dependencies...
pip install websockets psutil requests

echo.
echo Starting Remote Control Server...
echo.
echo Dashboard will be available at:
echo   http://localhost:8081/remote/dashboard
echo.
echo API Endpoints:
echo   GET  http://localhost:8081/remote/status
echo   GET  http://localhost:8081/remote/logs
echo   GET  http://localhost:8081/remote/signals
echo   POST http://localhost:8081/remote/command
echo.
echo WebSocket: ws://localhost:8082
echo.
echo API Keys:
echo   Admin:  genx_admin_2024
echo   Trader: genx_trader_2024
echo   Viewer: genx_viewer_2024
echo.
echo Press Ctrl+C to stop the server
echo ========================================

python remote_control_server.py

pause