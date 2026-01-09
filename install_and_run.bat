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
echo Make sure Ollama is running in another window!
echo.
echo To access on MOBILE:
echo 1. Connect phone to same Wi-Fi.
echo 2. Find your PC's IP address (run 'ipconfig' in cmd).
echo 3. Open phone browser to: http://[YOUR_IP]:8501
echo.
streamlit run app.py --server.address 0.0.0.0

pause
