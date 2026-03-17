# FactoryPulse Lite

**Predictive Maintenance for ASEAN SME Resilience**

V HACK USM 2026 | Case Study 1 | ML Track (Time-Series / RUL Estimation) | SDG 9.4

FactoryPulse Lite predicts machine failure before it freezes production. It reads multivariate sensor data, estimates Remaining Useful Life (RUL), classifies machine health, detects degradation change-points, benchmarks itself on official NASA data, and ranks maintenance priority in an operator-friendly dashboard.

## Quick Start

**One command** installs dependencies, trains the model, builds the evaluation report, and launches the dashboard:

| Platform | Command |
|----------|---------|
| **Linux / macOS** | `bash setup.sh` |
| **Windows (CMD)** | `setup.bat` |
| **Windows (PowerShell)** | `powershell -ExecutionPolicy Bypass -File setup.ps1` |

> Requires **Python 3.11+**. The app opens at `http://localhost:8501`.

<details>
<summary>Manual setup (step by step)</summary>

**Linux / macOS**
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/train.py
python scripts/evaluate.py
streamlit run app/Home.py
```

**Windows (PowerShell)**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/train.py
python scripts/evaluate.py
streamlit run app/Home.py
```

**Windows (CMD)**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
python scripts\train.py
python scripts\evaluate.py
streamlit run app/Home.py
```
</details>

## What It Does

| Feature | Description |
|---------|-------------|
| **RUL Prediction** | XGBoost regression estimates cycles until failure |
| **Health Classification** | 4 states: Healthy / Watchlist / Impaired / Critical |
| **Change-Point Detection** | PELT algorithm finds when degradation started |
| **Top Drivers** | Model-weighted drift analysis identifies degrading sensors |
| **Maintenance Planner** | Priority queue with action windows and protected value |
| **Explainability** | Plain-language summaries for non-technical operators |
| **Benchmarking** | Official CMAPSS test scoring, baselines, robustness, and latency artifacts |

## Validation Snapshot

Trained on NASA CMAPSS FD001 (100 turbofan engines, run-to-failure).

| Metric | Value |
|--------|-------|
| Hold-out RMSE | 18.23 cycles |
| Hold-out MAE | 13.47 cycles |
| Official test RMSE | 17.67 cycles |
| Official test MAE | 12.96 cycles |
| Validation set | 4,712 samples (25% unit hold-out) |
| Official test set | 100 engines |
| Features | 168 rolling-window statistics |
| Inference window | 15 cycles |

Additional evidence is written to `models/evaluation_report.json`, including:

- baseline comparisons
- robustness stress tests
- end-to-end inference latency
- benchmark generation timestamp and dataset metadata

## Architecture

```text
Sensor CSV -> Preprocessing -> Rolling-window features (168)
  -> XGBoost RUL regression -> Health scoring (sensor drift + RUL blend)
  -> Change-point detection (PELT) -> Dashboard + Judging Brief (Streamlit + Plotly)
  -> Evaluation report (official test, baselines, robustness, latency)
```

## Project Structure

```text
app/                    Streamlit pages
  Home.py               Landing / command center
  pages/
    1_Fleet_Overview.py
    2_Machine_Detail.py
    3_Maintenance_Planner.py
    4_Judging_Brief.py
src/factorypulse/       Core Python package
  data/                 Loading and preprocessing
  features/             Rolling-window feature engineering
  models/               Training, inference, health scoring, evaluation
  services/             Scoring and planning
  dashboard/            UI components and charts
  explain/              Plain-language summaries
scripts/                Cross-platform train and evaluate entry points
configs/                App and model configuration (YAML)
assets/                 Demo fleet data, sample uploads, architecture diagram
models/                 Trained artifacts and evaluation report
docs/                   Judging brief and deployment playbook
tests/                  Pytest test suites
Makefile                install / test / train / evaluate / app
```

## Try It: Upload Your Own Machine

The dashboard accepts CMAPSS-compatible sensor CSV files. Three sample files are included with different degradation profiles:

| File | Machine state | What you'll see |
|------|--------------|-----------------|
| `assets/sample-upload-healthy.csv` | Healthy (97/100) | Stable sensors, 125+ cycles remaining |
| `assets/sample-upload-warning.csv` | Watchlist (71/100) | Early drift, about 77 cycles remaining |
| `assets/sample-upload-critical.csv` | Impaired (35/100) | Heavy degradation, about 17 cycles remaining |

**How to try it**
1. Run the app with `make app`
2. On any page, open the sidebar and upload a sample CSV
3. The uploaded machine replaces the demo fleet across all pages
4. Click **Reset to demo fleet** in the sidebar to go back to the 5-machine demo
5. On Machine Detail, use the dropdown to switch between machines when viewing the demo fleet

CSV format: must have columns `unit_id`, `cycle`, `op_setting_1-3`, `sensor_1` through `sensor_21`. Minimum 15 rows.

## Tech Stack

- **Model**: XGBoost (500 trees, depth 4, learning rate 0.03)
- **Features**: pandas rolling windows (mean, std, min, max, delta, EMA, slope)
- **Health**: Blended score (30% sensor drift + 70% RUL position)
- **Change-point**: ruptures (PELT, L2 cost)
- **Validation**: official CMAPSS test benchmark, baselines, robustness stress tests, pytest
- **Dashboard**: Streamlit + Plotly
- **Data**: NASA CMAPSS FD001

## Commands

| Command | Description |
|---------|-------------|
| `make install` | Install Python dependencies |
| `make test` | Run test suites |
| `make train` | Train XGBoost model on CMAPSS FD001 |
| `make evaluate` | Generate the evaluation report and benchmark table |
| `make app` | Launch Streamlit dashboard |

## Judge-Facing Assets

- `docs/judging-brief.md`
- `docs/deployment-playbook.md`
- `models/evaluation_report.json`

## License

Built for V HACK USM 2026. Not for commercial use.
