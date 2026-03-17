from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from factorypulse.dashboard.cards import (
    apply_global_styles,
    health_badge,
    render_machine_row,
    render_metric_card,
    render_page_header,
    render_sidebar_brand,
)
from factorypulse.dashboard.charts import fleet_health_bar_chart
from factorypulse.dashboard.data import build_demo_fleet, load_app_config, parse_uploaded_frame, resolve_window_size
from factorypulse.services.scoring import score_machine_frame

st.set_page_config(page_title="Fleet Overview | FactoryPulse", page_icon="⚙️", layout="wide")
apply_global_styles()
render_sidebar_brand()

app_config = load_app_config().get("app", {})
window_size = resolve_window_size(int(app_config.get("default_window_size", 15)))

with st.sidebar:
    st.markdown("### Upload CSV")
    uploaded_file = st.file_uploader("Single machine trajectory", type=["csv"])
    st.caption("Format: `assets/sample-upload.csv`")

if uploaded_file is not None:
    try:
        uploaded_frame = parse_uploaded_frame(uploaded_file)
        prediction, roi_value = score_machine_frame(uploaded_frame, window_size=window_size)
    except ValueError as error:
        st.error(f"Could not score upload: {error}")
        st.stop()
    except Exception as error:
        st.error(f"Upload error: {error}")
        st.stop()
    st.session_state["selected_machine"] = {
        "machine_id": prediction.machine_id,
        "display_name": uploaded_file.name,
        "line_name": "Uploaded machine",
        "scenario": "Custom upload",
        "frame": uploaded_frame,
        "prediction": prediction,
        "roi_value": roi_value,
    }
    fleet = [st.session_state["selected_machine"]]
else:
    try:
        fleet = build_demo_fleet(window_size=window_size)
    except FileNotFoundError as error:
        st.error(f"Missing artifacts: {error}")
        st.caption("Run `make train` first.")
        st.stop()

top = fleet[0]
st.session_state.setdefault("selected_machine", top)

health_mix = Counter(item["prediction"].health_state for item in fleet)
protected_value = sum(item["roi_value"] for item in fleet)
avg_health = sum(item["prediction"].health_score for item in fleet) / len(fleet)

render_page_header(
    title="Fleet Overview",
    subtitle="Machine priority ranked by health state and remaining life.",
    eyebrow="Priority board",
    chips=[
        ("Top risk", top["display_name"]),
        ("Shortest RUL", f"{top['prediction'].predicted_rul:.0f} cyc"),
        ("Protected", f"${protected_value:,.0f}"),
    ],
)

c1, c2, c3, c4 = st.columns(4)
with c1:
    render_metric_card("Critical", str(health_mix.get("Critical", 0)), "Immediate service")
with c2:
    render_metric_card("Impaired", str(health_mix.get("Impaired", 0)), "Significant degradation")
with c3:
    render_metric_card("Watchlist", str(health_mix.get("Watchlist", 0)), "Schedule before peak")
with c4:
    render_metric_card("Avg health", f"{avg_health:.0f}/100", "Fleet average")

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

left, right = st.columns([1.5, 1])

with left:
    st.markdown("## Priority queue")
    for rank, item in enumerate(fleet, start=1):
        pred = item["prediction"]
        render_machine_row(
            rank=rank,
            name=item["display_name"],
            meta=f"{item['line_name']} · {item['scenario']}",
            badge_html=health_badge(pred.health_state),
            rul=f"{pred.predicted_rul:.0f} cyc",
            health=f"{pred.health_score:.0f}",
            cost=f"${item['roi_value']:,.0f}",
        )
        if st.button("Inspect →", key=f"inspect-{item['machine_id']}"):
            st.session_state["selected_machine"] = item
            st.toast(f"Loaded {item['display_name']}")

with right:
    st.markdown("## Health distribution")
    st.plotly_chart(fleet_health_bar_chart(fleet), use_container_width=True)
