@echo off 
echo Creating system restore point... 
powershell -Command "Checkpoint-Computer -Description 'A6_9V Trading System Backup' -RestorePointType 'MODIFY_SETTINGS'" 
echo System restore point created! 
