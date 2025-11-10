@echo off
echo ========================================
echo   GenX_FX Log Viewer
echo ========================================

echo Select log type:
echo 1. Container logs (real-time)
echo 2. Application logs
echo 3. Trading signals log
echo 4. Error logs
echo 5. All logs summary

choice /c 12345 /n /m "Enter choice (1-5): "

if errorlevel 5 goto ALL_LOGS
if errorlevel 4 goto ERROR_LOGS  
if errorlevel 3 goto SIGNAL_LOGS
if errorlevel 2 goto APP_LOGS
if errorlevel 1 goto CONTAINER_LOGS

:CONTAINER_LOGS
echo.
echo Container Logs (Press Ctrl+C to exit):
echo =====================================
docker logs -f genx-fx-enhanced
goto END

:APP_LOGS
echo.
echo Application Logs:
echo =================
if exist logs\genx_system.log (
    type logs\genx_system.log | more
) else (
    echo No application logs found
)
goto END

:SIGNAL_LOGS
echo.
echo Trading Signals Log:
echo ===================
if exist signal_output\trading.log (
    type signal_output\trading.log | more
) else (
    echo No signal logs found
)
goto END

:ERROR_LOGS
echo.
echo Error Logs:
echo ===========
if exist logs\errors.log (
    type logs\errors.log | more
) else (
    echo No error logs found
)
goto END

:ALL_LOGS
echo.
echo System Summary:
echo ===============
echo Container Status:
docker ps | findstr genx
echo.
echo Recent Container Logs:
docker logs --tail 20 genx-fx-enhanced 2>nul
echo.
echo Disk Usage:
dir logs signal_output 2>nul
goto END

:END
echo.
pause