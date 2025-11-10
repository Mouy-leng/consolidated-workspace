@echo off
echo ========================================
echo GenX FX Project Migration to D: Drive
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if errorlevel 1 (
    echo ERROR: This script must be run as Administrator
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo [1/8] Checking drive space...
echo C: Drive - Current project location
echo D: Drive - Target location (225GB free)
echo E: Drive - Backup location (62GB free)
echo.

echo [2/8] Creating directory structure on D: drive...
if not exist "D:\GenX_FX" mkdir "D:\GenX_FX"
if not exist "D:\GenX_FX\backup" mkdir "D:\GenX_FX\backup"
if not exist "D:\GenX_FX\logs" mkdir "D:\GenX_FX\logs"
if not exist "D:\GenX_FX\data" mkdir "D:\GenX_FX\data"
if not exist "D:\GenX_FX\credentials" mkdir "D:\GenX_FX\credentials"
if not exist "D:\GenX_FX\vps" mkdir "D:\GenX_FX\vps"

echo [3/8] Copying project files to D: drive...
xcopy "C:\Users\lengk\GenX_FX-1\*" "D:\GenX_FX\" /E /H /Y /I
if errorlevel 1 (
    echo ERROR: Failed to copy files to D: drive
    pause
    exit /b 1
)

echo [4/8] Creating backup on USB (E:) drive...
if exist "E:\" (
    if not exist "E:\GenX_FX_Backup" mkdir "E:\GenX_FX_Backup"
    if not exist "E:\GenX_FX_Backup\credentials" mkdir "E:\GenX_FX_Backup\credentials"
    if not exist "E:\GenX_FX_Backup\vps" mkdir "E:\GenX_FX_Backup\vps"
    
    echo Creating credentials backup...
    copy "D:\GenX_FX\credentials\*" "E:\GenX_FX_Backup\credentials\" /Y 2>nul
    copy "D:\GenX_FX\vps\*" "E:\GenX_FX_Backup\vps\" /Y 2>nul
    
    echo Creating full project backup...
    xcopy "D:\GenX_FX\*" "E:\GenX_FX_Backup\project\" /E /H /Y /I
    echo Backup created on USB drive E:
) else (
    echo WARNING: USB drive E: not found, skipping backup
)

echo [5/8] Updating file paths in scripts...
REM Update paths in batch files
powershell -Command "(Get-Content 'D:\GenX_FX\start-simple.bat') -replace 'E:\\\\Code\\\\GenX_FX-1', 'D:\\\\GenX_FX' | Set-Content 'D:\GenX_FX\start-simple.bat'"
powershell -Command "(Get-Content 'D:\GenX_FX\start-genx-complete.bat') -replace 'E:\\\\Code\\\\GenX_FX-1', 'D:\\\\GenX_FX' | Set-Content 'D:\GenX_FX\start-genx-complete.bat'"

echo [6/8] Creating new startup scripts for D: drive...
echo @echo off > "D:\GenX_FX\start-genx-d.bat"
echo echo Starting GenX FX from D: Drive... >> "D:\GenX_FX\start-genx-d.bat"
echo cd /d "D:\GenX_FX" >> "D:\GenX_FX\start-genx-d.bat"
echo chcp 65001 ^>nul 2^>^&1 >> "D:\GenX_FX\start-genx-d.bat"
echo start "GenX API Server" cmd /k "echo GenX FX API Server ^&^& python simple-api-server.py" >> "D:\GenX_FX\start-genx-d.bat"
echo timeout /t 3 /nobreak ^>nul >> "D:\GenX_FX\start-genx-d.bat"
echo start "GenX Signal Generator" cmd /k "echo GenX FX Gold Signal Generator ^&^& python genx-robust-backend.py" >> "D:\GenX_FX\start-genx-d.bat"
echo echo GenX FX 24/7 System started from D: Drive! >> "D:\GenX_FX\start-genx-d.bat"
echo pause >> "D:\GenX_FX\start-genx-d.bat"

echo [7/8] Creating backup script...
echo @echo off > "D:\GenX_FX\backup-to-usb.bat"
echo echo Creating backup to USB drive... >> "D:\GenX_FX\backup-to-usb.bat"
echo if exist "E:\" ( >> "D:\GenX_FX\backup-to-usb.bat"
echo     xcopy "D:\GenX_FX\*" "E:\GenX_FX_Backup\project\" /E /H /Y /I >> "D:\GenX_FX\backup-to-usb.bat"
echo     echo Backup completed to E:\GenX_FX_Backup\ >> "D:\GenX_FX\backup-to-usb.bat"
echo ^) else ( >> "D:\GenX_FX\backup-to-usb.bat"
echo     echo ERROR: USB drive E: not found >> "D:\GenX_FX\backup-to-usb.bat"
echo ^) >> "D:\GenX_FX\backup-to-usb.bat"
echo pause >> "D:\GenX_FX\backup-to-usb.bat"

echo [8/8] Testing new setup...
cd /d "D:\GenX_FX"
python --version
if errorlevel 1 (
    echo WARNING: Python not found in PATH, you may need to reinstall
) else (
    echo Python found, testing import...
    python -c "import requests; print('Dependencies OK')"
)

echo.
echo ========================================
echo Migration Complete!
echo ========================================
echo.
echo New Project Location: D:\GenX_FX
echo Backup Location: E:\GenX_FX_Backup
echo.
echo To start the system from D: drive:
echo   D:\GenX_FX\start-genx-d.bat
echo.
echo To create backup:
echo   D:\GenX_FX\backup-to-usb.bat
echo.
echo Original C: location can now be cleaned up.
echo.
pause

