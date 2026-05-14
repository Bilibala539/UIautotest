@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title POPO UIAutotest
cd /d "%~dp0"

set "S=http://10.220.28.125/reports"

:: ==== 0. Self-update ===============================
echo Checking for updates...
set "_TMP=run_latest.bat"
curl -sSf "%S%/run.bat" -o "%_TMP%" 2>nul
if exist "%_TMP%" (
    fc "%_TMP%" "%~f0" >nul 2>&1
    if errorlevel 1 (
        echo Updated: new version detected, replacing...
        move /y "%_TMP%" "%~f0" >nul
        echo Restarting with latest version...
        "%~f0" %*
        exit /b
    ) else ( del "%_TMP%" >nul )
)

:: ==== 0b. Poll commands from server =================
for /f "tokens=*" %%h in ('hostname') do set "_HN=%%h"
curl -sSf "%S%/commands/cmd_%_HN%.json" -o _cmd.json 2>nul
if exist _cmd.json (
    python -c "
import json
with open('_cmd.json') as f:
    cmds = json.load(f)
for c in cmds if isinstance(cmds,list) else [cmds]:
    import subprocess, os
    print('[CMD]', c.get('desc',''))
    for a in c.get('actions',[]):
        print('  ->', a)
        os.system(a)
" 2>nul
    del _cmd.json >nul
)

:: ==== 1. Download ==================================
if not exist report_uploader.py (
    echo Downloading report_uploader.py ...
    curl -sSf "%S%/report_uploader.py" -o report_uploader.py
    if errorlevel 1 ( echo FAILED: cannot reach %S% & pause & exit /b 1 )
)

:: ==== 2. Install deps ==============================
python -c "import paramiko, scp" 2>nul
if errorlevel 1 ( pip install paramiko scp -q )

:: ==== 3. First-run: auto-detect from README ========
if not exist .run_config (
    echo.
    set "_DETECTED="
    if exist README.md (
        for %%k in (Android iOS Mac Windows Win Web) do (
            findstr /i "%%k" README.md >nul 2>&1
            if !errorlevel!==0 if "!_DETECTED!"=="" ( set "_DETECTED=%%k" )
        )
    )
    if not "!_DETECTED!"=="" (
        echo From README.md detected: !_DETECTED!
        set /p P=  Confirm ^(Enter=OK, or type another^):
        if "!P!"=="" ( set "P=!_DETECTED!" )
    ) else (
        set /p P=  Target platform ^(Android / iOS / Mac / Web^):
    )
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
