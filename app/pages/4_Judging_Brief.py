from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from factorypulse.dashboard.cards import (
    apply_global_styles,
    render_bullet_panel,
    render_metric_card,
    render_page_header,
    render_panel,
    render_sidebar_brand,
)
from factorypulse.dashboard.data import load_evaluation_report


def _short_number(value: float) -> str:
    return f"{value:.2f}"


st.set_page_config(page_title="Judging Brief | FactoryPulse", page_icon="⚙️", layout="wide")
apply_global_styles()
render_sidebar_brand()

report = load_evaluation_report()
if not report:
    st.error("Missing evaluation artifacts.")
    st.caption("Run `python scripts/evaluate.py` after training, then refresh this page.")
    st.stop()

official = report.get("official_test", {})
summary = report.get("summary", {})
latency = report.get("latency_ms", {})
dataset = report.get("dataset", {})
baselines = pd.DataFrame(report.get("baselines", []))
robustness = pd.DataFrame(report.get("robustness", []))

render_page_header(
    title="Judging Brief",
    subtitle="A compact view of the submission story: benchmark strength, SME fit, rollout path, and risk profile.",
    eyebrow="Submission evidence",
    chips=[
        ("Dataset", str(dataset.get("subset", "FD001"))),
        ("Official RMSE", _short_number(official.get("rmse", 0.0))),
        ("Baseline gap", _short_number(summary.get("rmse_gain_vs_best_baseline", 0.0))),
    ],
)

c1, c2, c3 = st.columns(3)
with c1:
    render_metric_card("Official benchmark", _short_number(official.get("rmse", 0.0)), "RMSE on 100 CMAPSS test engines")
with c2:
    render_metric_card("Model edge", _short_number(summary.get("rmse_gain_vs_best_baseline", 0.0)), "RMSE better than best baseline")
with c3:
    render_metric_card("Runtime fit", f"{latency.get('p95_ms', 0):.1f} ms", "p95 single-machine inference latency")

st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

overview_tab, rollout_tab, evidence_tab = st.tabs(["Overview", "Rollout", "Evidence"])

with overview_tab:
    left, right = st.columns([1.15, 0.85], gap="large")
    with left:
        render_panel(
            "One-line case",
            "A practical predictive-maintenance tool for SMEs that cannot afford full smart-factory upgrades, "
            "but still need earlier maintenance decisions on critical rotating assets.",
        )
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        render_bullet_panel(
            "Why it is competitive",
            [
                "Benchmark-backed instead of demo-only: official NASA test scoring is built into the repo.",
                "Operator-facing instead of model-only: RUL, health, drivers, and actions are shown together.",
                "Low-friction deployment: can start with CSVs before any deeper sensor integration.",
            ],
        )
    with right:
        render_bullet_panel(
            "What judges should remember",
            [
                "Strong technical validation with a clear baseline margin.",
                "Good fit for ASEAN SME cost constraints and maintenance reality.",
                "Modular enough for a pilot, but still honest about current CMAPSS grounding.",
            ],
        )

with rollout_tab:
    left, right = st.columns(2, gap="large")
    with left:
        render_bullet_panel(
            "Beachhead market",
            [
                "Food processing and light manufacturing SMEs.",
                "Best fit: 5-20 critical motors, pumps, or compressors.",
                "Buyer: plant manager or operations lead who owns downtime risk.",
            ],
        )
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        render_bullet_panel(
            "Pilot path",
            [
                "Start with one production line and 3-5 critical assets.",
                "Use historical or daily-exported sensor CSVs first.",
                "Measure avoided downtime and maintenance timing over one quarter.",
            ],
        )
    with right:
        render_bullet_panel(
            "Sustainability and operations",
            [
                "Reduces premature part replacement and emergency breakdown waste.",
                "Monthly input review, quarterly threshold review, retrain only when drift matters.",
                "Human approval stays in the loop before maintenance work is triggered.",
            ],
        )
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        render_panel(
            "Commercial model",
            "Low-friction pilot first, then charge per monitored asset with optional support for retraining, "
            "reporting, and maintenance workflow tuning.",
        )

with evidence_tab:
    top, bottom = st.columns([1.1, 0.9], gap="large")
    with top:
        render_bullet_panel(
            "Benchmark summary",
            [
                f"Official RMSE: {_short_number(official.get('rmse', 0.0))}",
                f"Official MAE: {_short_number(official.get('mae', 0.0))}",
                f"Best baseline gap: {_short_number(summary.get('rmse_gain_vs_best_baseline', 0.0))} RMSE",
                f"Worst stress-test uplift: +{_short_number(summary.get('worst_stress_delta_rmse', 0.0))} RMSE",
            ],
        )
    with bottom:
        render_panel(
            "Interpretation",
            "The model is not just better than naive baselines. It keeps most of its performance under missing-data, "
            "noise, and sensor-dropout scenarios, which is the more relevant signal for a real SME deployment.",
        )

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    baseline_view = baselines.rename(
        columns={
            "name": "Model",
            "rmse": "RMSE",
            "mae": "MAE",
            "samples": "Samples",
        }
    )[["Model", "RMSE", "MAE", "Samples"]]
    robustness_view = robustness.rename(
        columns={
            "label": "Scenario",
            "rmse": "RMSE",
            "mae": "MAE",
            "delta_rmse": "RMSE delta",
        }
    )[["Scenario", "RMSE", "MAE", "RMSE delta"]]

    table_left, table_right = st.columns(2, gap="large")
    with table_left:
        st.markdown("### Baselines")
        st.dataframe(baseline_view, use_container_width=True, hide_index=True)
    with table_right:
        st.markdown("### Stress tests")
        st.dataframe(robustness_view, use_container_width=True, hide_index=True)
