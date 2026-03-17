#!/usr/bin/env bash
set -e

echo "=== FactoryPulse Lite Setup ==="
echo ""

if ! command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
    echo "ERROR: Python not found. Install Python 3.11+ first."
    exit 1
fi

PY=$(command -v python3 || command -v python)
echo "Using: $PY ($($PY --version 2>&1))"
echo ""

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    $PY -m venv .venv
fi

source .venv/bin/activate

echo "Installing dependencies..."
pip install -q -r requirements.txt

if [ ! -f "models/rul_xgb.joblib" ]; then
    echo ""
    echo "Training model (first run only, ~30 seconds)..."
    PYTHONPATH=src python -m factorypulse.models.train_rul
fi

echo ""
echo "=== Ready! ==="
echo "Starting dashboard..."
echo ""
PYTHONPATH=src streamlit run app/Home.py
