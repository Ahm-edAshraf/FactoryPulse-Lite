# FactoryPulse Lite

**Predictive Maintenance for ASEAN SME Resilience**

V HACK USM 2026 · Case Study 1 · ML Track (Time-Series / RUL Estimation) · SDG 9.4

FactoryPulse Lite predicts machine failure before it freezes production. It reads multivariate sensor data, estimates Remaining Useful Life (RUL), classifies machine health, detects degradation change-points, and ranks maintenance priority — all in an operator-friendly dashboard.

## Quick Start

```bash
# 1. Create a virtual environment
python -m venv .venv && source .venv/bin/activate

# 2. Install dependencies
make install

# 3. Train the model (downloads NASA CMAPSS FD001 automatically)
make train

# 4. Launch the dashboard
make app
```

The app opens at `http://localhost:8501`.

## What It Does

| Feature | Description |
|---------|-------------|
| **RUL Prediction** | XGBoost regression estimates cycles until failure |
| **Health Classification** | 4 states: Healthy / Watchlist / Impaired / Critical |
| **Change-Point Detection** | PELT algorithm finds when degradation started |
| **Top Drivers** | Feature importance identifies which sensors are degrading |
| **Maintenance Planner** | Priority queue with action windows and protected value |
| **Explainability** | Plain-language summaries for non-technical operators |

## Model Performance

Trained on NASA CMAPSS FD001 (100 turbofan engines, run-to-failure).

| Metric | Value |
|--------|-------|
| RMSE | 18.33 cycles |
| MAE | 13.31 cycles |
| Validation set | 4,712 samples (25% hold-out) |
| Features | 170 rolling-window statistics |
| Inference window | 15 cycles |

## Architecture

```
Sensor CSV → Preprocessing → Rolling-window features (170)
  → XGBoost RUL regression → Health scoring (sensor drift + RUL blend)
  → Change-point detection (PELT) → Dashboard (Streamlit + Plotly)
```

## Project Structure

```
├── app/                    Streamlit pages
│   ├── Home.py             Landing / command center
│   └── pages/
│       ├── 1_Fleet_Overview.py
│       ├── 2_Machine_Detail.py
│       └── 3_Maintenance_Planner.py
├── src/factorypulse/       Core Python package
│   ├── data/               Loading & preprocessing
│   ├── features/           Rolling-window feature engineering
│   ├── models/             Training, inference, health scoring
│   ├── services/           Scoring & planning
│   ├── dashboard/          UI components & charts
│   └── explain/            Plain-language summaries
├── configs/                App & model configuration (YAML)
├── assets/                 Demo fleet data & architecture diagram
├── models/                 Trained artifacts (metrics, features, config)
├── tests/                  Pytest test suites
├── docs/pitch/             Slide deck & presentation script
└── Makefile                install / test / train / app
```

## Tech Stack

- **Model**: XGBoost (250 trees, depth 6, lr 0.05)
- **Features**: pandas rolling windows (mean, std, min, max, delta, EMA, slope)
- **Health**: Blended score (30% sensor drift + 70% RUL position)
- **Change-point**: ruptures (PELT, L2 cost)
- **Validation**: Pydantic schemas, pytest
- **Dashboard**: Streamlit + Plotly
- **Data**: NASA CMAPSS FD001

## Commands

| Command | Description |
|---------|-------------|
| `make install` | Install Python dependencies |
| `make test` | Run test suites |
| `make train` | Train XGBoost model on CMAPSS FD001 |
| `make app` | Launch Streamlit dashboard |

## License

Built for V HACK USM 2026. Not for commercial use.
