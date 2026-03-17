Write-Host "=== FactoryPulse Lite Setup ===" -ForegroundColor Cyan
Write-Host ""

$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Host "ERROR: Python not found. Install Python 3.11+ first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Using: $(python --version 2>&1)"
Write-Host ""

if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

& .venv\Scripts\Activate.ps1

Write-Host "Installing dependencies..."
pip install -q -r requirements.txt

if (-not (Test-Path "models\rul_xgb.joblib")) {
    Write-Host ""
    Write-Host "Training model (first run only, ~30 seconds)..."
    $env:PYTHONPATH = "src"
    python -m factorypulse.models.train_rul
}

$env:PYTHONPATH = "src"
Write-Host ""
Write-Host "=== Ready! ===" -ForegroundColor Green
Write-Host "Starting dashboard..."
Write-Host ""
streamlit run app/Home.py
