@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title POPO UIAutotest
cd /d "%~dp0"

set "S=http://10.220.28.125/reports"

:: ==== 1. Download ==================================
if not exist report_uploader.py (
    echo Downloading report_uploader.py ...
    curl -sSf "%S%/report_uploader.py" -o report_uploader.py
    if errorlevel 1 (
        echo FAILED: cannot reach %S%
        pause && exit /b 1
    )
)

:: ==== 2. Install deps ==============================
python -c "import paramiko, scp" 2>nul
if errorlevel 1 ( pip install paramiko scp -q )

:: ==== 3. First-run config ==========================
if not exist .run_config (
    echo.
    echo First-run setup ^(only once^):
    set /p P=  Platform ^(e.g. Android / iOS / Mac / Web^):
    set /p N=  Project name ^(e.g. POPO-Android^):
    echo UPLOADER_PLATFORM=!P!>.run_config
    echo UPLOADER_PROJECT=!N!>>.run_config
)
for /f "tokens=1,2 delims==" %%a in (.run_config) do set %%a=%%b

:: ==== 4. Run tests =================================
echo.
echo Platform: %UPLOADER_PLATFORM%   Project: %UPLOADER_PROJECT%
echo.

if "%~1"=="" (set "T=tests\") else (set "T=%~1")
pytest "%T%" -v -p report_uploader

echo.
echo Done ^>^> http://10.220.28.125/reports/allure-report/history.html
echo.
pause
