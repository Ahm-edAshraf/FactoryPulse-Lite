"""Data access helpers for demo and uploaded machine trajectories."""

from __future__ import annotations

from pathlib import Path
import json

import pandas as pd

from factorypulse.config import CONFIG_ROOT, MODEL_ROOT, RAW_DATA_ROOT, load_yaml_config
from factorypulse.data.loaders import ensure_cmapss_files, load_cmapss_split
from factorypulse.data.preprocessing import prepare_sensor_frame
from factorypulse.services.scoring import score_machine_frame
from factorypulse.services.planner import rank_machines


def load_app_config() -> dict:
    return load_yaml_config(CONFIG_ROOT / "app.yaml")


def load_model_metrics() -> dict:
    metrics_path = MODEL_ROOT / "metrics.json"
    if not metrics_path.exists():
        return {}
    return json.loads(metrics_path.read_text(encoding="utf-8"))


def load_demo_catalog() -> pd.DataFrame:
    project_root = Path(__file__).resolve().parents[3]
    catalog = pd.read_csv(project_root / "assets" / "demo-machines.csv")
    return catalog


def _demo_trajectory_asset_path() -> Path:
    return Path(__file__).resolve().parents[3] / "assets" / "demo-trajectories.csv"


def load_demo_base_frame() -> pd.DataFrame:
    demo_asset = _demo_trajectory_asset_path()
    if demo_asset.exists():
        return prepare_sensor_frame(pd.read_csv(demo_asset))

    raw_paths = ensure_cmapss_files(RAW_DATA_ROOT / "cmapss", subset_id="FD001")
    frame = load_cmapss_split(raw_paths["train"])
    return prepare_sensor_frame(frame)


def build_demo_fleet(window_size: int) -> list[dict]:
    catalog = load_demo_catalog()
    base_frame = load_demo_base_frame()
    fleet: list[dict] = []

    for row in catalog.to_dict(orient="records"):
        machine_frame = base_frame[base_frame["unit_id"] == int(row["machine_id"])]
        max_cycle = int(machine_frame["cycle"].max())
        display_cycle = max(window_size, int(max_cycle * float(row["progress_ratio"])))
        visible_frame = machine_frame[machine_frame["cycle"] <= display_cycle].reset_index(drop=True)
        prediction, roi_value = score_machine_frame(
            visible_frame,
            window_size=window_size,
            failure_cost=float(row["failure_cost"]),
            maintenance_cost=float(row["maintenance_cost"]),
        )
        fleet.append(
            {
                **row,
                "frame": visible_frame,
                "prediction": prediction,
                "roi_value": roi_value,
            }
        )

    return list(rank_fleet(fleet))


def rank_fleet(fleet: list[dict]) -> list[dict]:
    ranked_predictions = rank_machines([item["prediction"] for item in fleet])
    ordered_ids = [prediction.machine_id for prediction in ranked_predictions]
    return sorted(fleet, key=lambda item: ordered_ids.index(item["prediction"].machine_id))


def parse_uploaded_frame(uploaded_file) -> pd.DataFrame:
    frame = pd.read_csv(uploaded_file)
    prepared = prepare_sensor_frame(frame)
    if prepared["unit_id"].nunique() != 1:
        raise ValueError("uploaded CSV must contain exactly one machine trajectory")
    return prepared


def resolve_window_size(default_window_size: int) -> int:
    metrics = load_model_metrics()
    return int(metrics.get("inference_window", default_window_size))


def get_active_fleet(window_size: int) -> list[dict]:
    """Return the uploaded fleet if one exists in session state, otherwise the demo fleet."""
    import streamlit as st

    if "uploaded_fleet" in st.session_state:
        return st.session_state["uploaded_fleet"]

    fleet = build_demo_fleet(window_size=window_size)
    return fleet


def render_sidebar_upload(window_size: int) -> None:
    """Render upload widget + reset button in sidebar. Stores fleet in session state."""
    import streamlit as st

    with st.sidebar:
        st.markdown("### Upload CSV")
        uploaded_file = st.file_uploader("Single machine trajectory", type=["csv"], key="csv_upload")
        st.caption("Try: `assets/sample-upload-critical.csv`")

        if uploaded_file is not None:
            try:
                uploaded_frame = parse_uploaded_frame(uploaded_file)
                prediction, roi_value = score_machine_frame(uploaded_frame, window_size=window_size)
                uploaded_item = {
                    "machine_id": int(prediction.machine_id),
                    "display_name": uploaded_file.name.replace(".csv", ""),
                    "line_name": "Uploaded machine",
                    "scenario": "Custom upload",
                    "frame": uploaded_frame,
                    "prediction": prediction,
                    "roi_value": roi_value,
                }
                st.session_state["uploaded_fleet"] = [uploaded_item]
                st.session_state["selected_machine"] = uploaded_item
            except ValueError as error:
                st.error(f"Upload error: {error}")
            except Exception as error:
                st.error(f"Scoring error: {error}")

        if "uploaded_fleet" in st.session_state:
            st.markdown("---")
            if st.button("↩ Reset to demo fleet", use_container_width=True):
                del st.session_state["uploaded_fleet"]
                if "selected_machine" in st.session_state:
                    del st.session_state["selected_machine"]
                st.rerun()
