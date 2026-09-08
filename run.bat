@echo off
setlocal
chcp 65001 >nul
title TidiTree Web Autotest
cd /d "%~dp0"

if "%~1"=="" (
    set "TEST_TARGET=tests\"
) else (
    set "TEST_TARGET=%~1"
)

python -m pytest "%TEST_TARGET%" -v
set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo Test run completed. Local reports, when enabled, are in output\.
pause
exit /b %EXIT_CODE%
