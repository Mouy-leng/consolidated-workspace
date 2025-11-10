@echo off
REM GenX_FX Windows Service Setup Script
REM This script installs GenX_FX as a Windows scheduled task for 24/7 operation

echo ========================================
echo GenX_FX Windows Service Setup
echo ========================================

REM Check for administrative privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script requires administrator privileges
    echo Please run as Administrator
    pause
    exit /b 1
)

echo Setting up GenX_FX as Windows service...

REM Set working directory
cd /d "%~dp0"

REM Create task scheduler entry
echo Installing Windows Task Scheduler entry...
schtasks /create /xml "genx_scheduler_task.xml" /tn "GenX_FX_Service" /f

if errorlevel 1 (
    echo ERROR: Failed to create scheduled task
    echo Please check the XML file and try again
    pause
    exit /b 1
)

echo Task scheduler entry created successfully!

REM Start the task
echo Starting GenX_FX service...
schtasks /run /tn "GenX_FX_Service"

if errorlevel 1 (
    echo WARNING: Failed to start the task immediately
    echo The task will start on next boot/login
) else (
    echo Service started successfully!
)

REM Create desktop shortcut for management
echo Creating desktop shortcuts...

set "DesktopPath=%USERPROFILE%\Desktop"

REM Service Control Shortcut
echo @echo off > "%DesktopPath%\GenX Control Panel.bat"
echo cd /d "%~dp0" >> "%DesktopPath%\GenX Control Panel.bat"
echo python monitoring_dashboard.py >> "%DesktopPath%\GenX Control Panel.bat"
echo pause >> "%DesktopPath%\GenX Control Panel.bat"

REM Quick Status Shortcut
echo @echo off > "%DesktopPath%\GenX Status.bat"
echo cd /d "%~dp0" >> "%DesktopPath%\GenX Status.bat"
echo python genx_24_7_service.py status >> "%DesktopPath%\GenX Status.bat"
echo pause >> "%DesktopPath%\GenX Status.bat"

REM PyCharm Startup Shortcut
echo @echo off > "%DesktopPath%\Start GenX in PyCharm.bat"
echo cd /d "%~dp0" >> "%DesktopPath%\Start GenX in PyCharm.bat"
echo start "" "C:\Users\%USERNAME%\AppData\Local\JetBrains\Toolbox\apps\PyCharm-P\ch-0\*\bin\pycharm64.exe" . >> "%DesktopPath%\Start GenX in PyCharm.bat"
echo if errorlevel 1 ( >> "%DesktopPath%\Start GenX in PyCharm.bat"
echo     echo PyCharm not found in default location >> "%DesktopPath%\Start GenX in PyCharm.bat"
echo     echo Please locate PyCharm manually >> "%DesktopPath%\Start GenX in PyCharm.bat"
echo     pause >> "%DesktopPath%\Start GenX in PyCharm.bat"
echo ) >> "%DesktopPath%\Start GenX in PyCharm.bat"

echo Desktop shortcuts created!

REM Setup firewall rules for monitoring dashboard
echo Setting up firewall rules...
netsh advfirewall firewall add rule name="GenX_FX_Dashboard" dir=in action=allow protocol=TCP localport=9000
netsh advfirewall firewall add rule name="GenX_FX_API" dir=in action=allow protocol=TCP localport=8000

echo Firewall rules configured.

REM Create startup folder shortcuts
set "StartupPath=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
copy "%DesktopPath%\GenX Status.bat" "%StartupPath%\GenX Quick Status.bat" >nul

echo.
echo ========================================
echo GenX_FX Windows Service Setup Complete!
echo ========================================
echo.
echo Service Details:
echo   Task Name: GenX_FX_Service
echo   Status: %TASK_STATUS%
echo   Triggers: Boot + User Login
echo   Location: %~dp0
echo.
echo Management:
echo   Control Panel: http://localhost:9000
echo   Task Scheduler: schtasks /query /tn "GenX_FX_Service"
echo   Start Service: schtasks /run /tn "GenX_FX_Service"
echo   Stop Service: schtasks /end /tn "GenX_FX_Service"
echo   Delete Service: schtasks /delete /tn "GenX_FX_Service" /f
echo.
echo Desktop Shortcuts Created:
echo   - GenX Control Panel.bat (Web Dashboard)
echo   - GenX Status.bat (Command Line Status)
echo   - Start GenX in PyCharm.bat (PyCharm IDE)
echo.
echo The service will automatically start on:
echo   1. System boot (2 minute delay)
echo   2. User login (1 minute delay)
echo.
echo Access the monitoring dashboard at: http://localhost:9000
echo.

REM Query task status
for /f "tokens=2 delims= " %%i in ('schtasks /query /tn "GenX_FX_Service" /fo list ^| findstr /i "Status"') do set TASK_STATUS=%%i

echo Current Status: %TASK_STATUS%

echo.
echo Press any key to open the monitoring dashboard...
pause >nul

REM Open monitoring dashboard
start "" http://localhost:9000

echo Setup complete! GenX_FX is now configured for 24/7 operation.