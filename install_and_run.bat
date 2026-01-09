@echo off
echo ==========================================
echo      Personal Multilingual LLM Setup
echo ==========================================

echo [1/3] Checking for Python...
python --version
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    pause
    exit /b
)

echo.
echo [2/3] Installing Dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies.
    pause
    exit /b
)

echo.
echo [3/3] Launching App...
echo.
echo CHOOSE ACCESS MODE:
echo 1. Local Network (Home Wi-Fi only)
echo 2. Public URL (Anywhere - requires internet)
echo.
set /p mode="Enter 1 or 2: "

if "%mode%"=="2" (
    echo.
    echo Starting Public Tunnel...
    python run_with_public_url.py
) else (
    echo.
    echo To access on MOBILE (Wi-Fi):
    echo 1. Connect phone to same Wi-Fi.
    echo 2. Find your PC's IP address (run 'ipconfig' in cmd).
    echo 3. Open phone browser to: http://[YOUR_IP]:8501
    echo.
    streamlit run app.py --server.address 0.0.0.0
)

pause
