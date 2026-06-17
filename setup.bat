@echo off
chcp 65001 >nul 2>nul
echo ============================================================
echo   UIAutotest Environment Setup
echo ============================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.12 first.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo [INFO] %%i

:: Create venv
if not exist "venv\Scripts\python.exe" (
    echo [STEP 1/4] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create venv
        pause
        exit /b 1
    )
    echo   [OK] venv created
) else (
    echo [STEP 1/4] venv already exists, skip
)

:: Upgrade pip
echo [STEP 2/4] Upgrading pip...
venv\Scripts\python -m pip install --upgrade pip -q

:: Install dependencies
echo [STEP 3/4] Installing packages (5-10 min first time)...
venv\Scripts\pip install -r requirements_full.txt -q
if errorlevel 1 (
    echo [WARN] Some packages failed, retrying one by one...
    for /f "tokens=*" %%p in (requirements_full.txt) do (
        venv\Scripts\pip install "%%p" -q 2>nul
    )
)
echo   [OK] Dependencies installed

:: Verify
echo [STEP 4/4] Verifying key packages...
venv\Scripts\python -c "import cv2; print('  opencv:', cv2.__version__)"
venv\Scripts\python -c "import numpy; print('  numpy:', numpy.__version__)"
venv\Scripts\python -c "import pytest; print('  pytest:', pytest.__version__)"
venv\Scripts\python -c "import pyautogui; print('  pyautogui:', pyautogui.__version__)"

echo.
echo ============================================================
echo   Setup complete!
echo ============================================================
echo.
echo Usage:
echo   Serial:   venv\Scripts\python -m pytest tests\checklist\ --timeout=180
echo   Parallel: venv\Scripts\python run_parallel.py -n 4
echo.
echo Prerequisites:
echo   1. MuMu Emulator 12 installed
echo   2. POPO App installed on emulator
echo   3. Emulator resolution set to 540x960
echo.
