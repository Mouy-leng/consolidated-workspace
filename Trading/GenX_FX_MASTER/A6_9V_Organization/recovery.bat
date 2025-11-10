@echo off 
echo A6_9V Organization Recovery System 
echo ================================== 
echo Available backups: 
dir /b backup\daily 
echo. 
set /p backup_name="Enter backup name to restore: " 
echo Restoring from backup: %backup_name 
xcopy "backup\daily\%backup_name\GenX_FX\A6_9V_Organization\" /E /I /Y 
echo Recovery completed! 
pause 
