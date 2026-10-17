@echo off
title Piano Player
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import sys; assert sys.version_info >= (3, 12)" >nul 2>&1
    if not errorlevel 1 (
        ".venv\Scripts\python.exe" launcher.py %*
        goto :done
    )
)
py -3 -c "import sys; assert sys.version_info >= (3, 12)" >nul 2>&1
if not errorlevel 1 (
    py -3 launcher.py %*
    goto :done
)
python -c "import sys; assert sys.version_info >= (3, 12)" >nul 2>&1
if not errorlevel 1 (
    python launcher.py %*
    goto :done
)
echo Python 3.12+ was not found. Install Python from https://www.python.org/downloads/
pause
exit /b 1
:done
if errorlevel 1 (
    echo Application could not start. See the message above, then run run.bat again.
    pause
    exit /b 1
)
exit /b 0
