@echo off
if exist "C:\Program Files\JetBrains\PyCharm 2024.3.2\bin\pycharm64.exe" (
    start "" "C:\Program Files\JetBrains\PyCharm 2024.3.2\bin\pycharm64.exe" "C:\Users\lengk\GenX_FX_Remote"
) else (
    echo PyCharm not found at: C:\Program Files\JetBrains\PyCharm 2024.3.2\bin\pycharm64.exe
    echo Please check your PyCharm installation
    pause
)
