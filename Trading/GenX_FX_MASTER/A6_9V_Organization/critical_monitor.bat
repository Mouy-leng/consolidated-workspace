@echo off 
:loop 
timeout /t 60 /nobreak >nul 
echo Checking for critical events... 
goto loop 
