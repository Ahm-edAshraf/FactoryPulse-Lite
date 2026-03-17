@echo off
echo === FactoryPulse Lite Setup ===
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Install Python 3.11+ first.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo Using: %%i
echo.

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

echo Installing dependencies...
pip install -q -r requirements.txt

if not exist "models\rul_xgb.joblib" (
    echo.
    echo Training model ^(first run only, ~30 seconds^)...
    python scripts\train.py
)

if not exist "models\evaluation_report.json" (
    echo.
    echo Building evaluation report...
    python scripts\evaluate.py
)

echo.
echo === Ready! ===
echo Starting dashboard...
echo.
streamlit run app/Home.py
