@echo off
REM Auto-start PyCharm with consolidated workspace
cd /d "E:\Code\consolidated-workspace"
powershell.exe -ExecutionPolicy Bypass -File "%~dp0start-pycharm.ps1"

