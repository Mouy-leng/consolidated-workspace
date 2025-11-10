@echo off
echo ==========================================
echo A6_9V ORGANIZATION - LAPTOP OPTIMIZATION
echo ==========================================
echo Optimizing laptop for 24/7 LIVE trading...
echo.

REM Disable sleep mode
powercfg -change -standby-timeout-ac 0
powercfg -change -standby-timeout-dc 0
powercfg -change -hibernate-timeout-ac 0
powercfg -change -hibernate-timeout-dc 0
powercfg -change -monitor-timeout-ac 0
powercfg -change -monitor-timeout-dc 0

REM Set high performance power plan
powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c

REM Disable Windows Update automatic restart
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" /v NoAutoRebootWithLoggedOnUsers /t REG_DWORD /d 1 /f

REM Disable automatic maintenance
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\Maintenance" /v MaintenanceDisabled /t REG_DWORD /d 1 /f

REM Set network adapter to never sleep
powercfg -setacvalueindex SCHEME_CURRENT 19cbb8fa-d23c-4a2b-86a0-9d2a9e6fb8c9 17aaa29b-8b43-4bdd-8e04-25276aa3a95f 0

echo.
echo ✅ LAPTOP OPTIMIZATION COMPLETED!
echo.
echo Power Settings:
echo - Sleep Mode: DISABLED
echo - Hibernate: DISABLED
echo - Monitor Timeout: DISABLED
echo - Power Plan: HIGH PERFORMANCE
echo - Windows Update Restart: DISABLED
echo - Automatic Maintenance: DISABLED
echo.
echo ⚠️  LIVE TRADING SYSTEM PROTECTED ⚠️
echo Your $25 FBS Markets account is safe!
echo.
pause
