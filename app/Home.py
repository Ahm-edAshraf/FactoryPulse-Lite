from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from factorypulse.dashboard.cards import (
    apply_global_styles,
    health_badge,
    render_metric_card,
    render_page_header,
    render_panel,
    render_sidebar_brand,
)
from factorypulse.dashboard.copy import APP_SUBTITLE, APP_TITLE
from factorypulse.dashboard.data import get_active_fleet, load_app_config, load_model_metrics, render_sidebar_upload, resolve_window_size

st.set_page_config(page_title="FactoryPulse Lite", page_icon="⚙️", layout="wide")
apply_global_styles()
render_sidebar_brand()

config = load_app_config()
app_config = config.get("app", {})
window_size = resolve_window_size(int(app_config.get("default_window_size", 15)))
metrics = load_model_metrics()

render_sidebar_upload(window_size)

try:
    fleet = get_active_fleet(window_size=window_size)
except FileNotFoundError as error:
    st.error(f"Missing trained artifacts or demo data: {error}")
    st.caption("Run `make train` first, then refresh this page.")
    st.stop()

is_upload = "uploaded_fleet" in st.session_state

health_mix = Counter(item["prediction"].health_state for item in fleet)
protected_value = sum(item["roi_value"] for item in fleet)
highest_risk = fleet[0]

render_page_header(
    title=APP_TITLE,
    subtitle=APP_SUBTITLE,
    eyebrow="Command center",
    chips=[
        ("RMSE", f"{metrics.get('rmse', 0):.1f} cycles"),
        ("MAE", f"{metrics.get('mae', 0):.1f} cycles"),
        ("Fleet", f"{len(fleet)} {'(uploaded)' if is_upload else ''}"),
    ],
)

c1, c2, c3, c4 = st.columns(4)
with c1:
    render_metric_card("Highest risk", highest_risk["display_name"], highest_risk.get("scenario", ""))
with c2:
    render_metric_card("Critical", str(health_mix.get("Critical", 0)), "Need immediate attention")
with c3:
    render_metric_card(
        "At risk",
        str(health_mix.get("Watchlist", 0) + health_mix.get("Impaired", 0)),
        "Watchlist + impaired",
    )
with c4:
    render_metric_card("Protected value", f"${protected_value:,.0f}", "Avoided downtime cost")

st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

left, right = st.columns([1.1, 1])
with left:
    render_panel(
        "What FactoryPulse does",
        "Predicts machine failures before they freeze production. "
        "Translates raw sensor data into plain maintenance actions. "
        "Helps ASEAN SMEs act early — no enterprise smart-factory spend required.",
    )
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    st.markdown("### Fleet snapshot")
    for item in fleet:
        pred = item["prediction"]
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown(
                f"{health_badge(pred.health_state)} &nbsp; **{item['display_name']}**",
                unsafe_allow_html=True,
            )
        with col2:
            st.caption(f"RUL: {pred.predicted_rul:.0f} cycles")
        with col3:
            st.caption(f"Health: {pred.health_score:.0f}/100")

with right:
    render_panel(
        "How to navigate",
        "Fleet Overview — see which machines need attention first. "
        "Machine Detail — understand why a machine is degrading. "
        "Maintenance Planner — schedule interventions and see protected value.",
    )
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    st.image("assets/architecture-diagram.svg", use_container_width=True)
