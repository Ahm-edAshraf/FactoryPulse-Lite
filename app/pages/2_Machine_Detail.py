from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from factorypulse.dashboard.cards import (
    apply_global_styles,
    health_badge,
    render_metric_card,
    render_page_header,
    render_panel,
    render_sidebar_brand,
)
from factorypulse.dashboard.charts import health_timeline_chart, rul_gauge_chart, sensor_trend_chart
from factorypulse.dashboard.data import build_demo_fleet, load_app_config, load_model_metrics, resolve_window_size
from factorypulse.explain.summarize import summarize_prediction

st.set_page_config(page_title="Machine Detail | FactoryPulse", page_icon="⚙️", layout="wide")
apply_global_styles()
render_sidebar_brand()

app_config = load_app_config().get("app", {})
window_size = resolve_window_size(int(app_config.get("default_window_size", 15)))

if "selected_machine" not in st.session_state:
    try:
        st.session_state["selected_machine"] = build_demo_fleet(window_size=window_size)[0]
    except FileNotFoundError as error:
        st.error(f"Missing artifacts: {error}")
        st.caption("Run `make train` first.")
        st.stop()

selected = st.session_state["selected_machine"]
prediction = selected["prediction"]
frame = selected["frame"]
metrics = load_model_metrics()

render_page_header(
    title=selected["display_name"],
    subtitle=f"{selected['line_name']} · {selected['scenario']}",
    eyebrow="Machine detail",
    chips=[
        ("Status", prediction.health_state),
        ("RUL", f"{prediction.predicted_rul:.0f} cycles"),
        ("Change-point", str(prediction.change_point or "—")),
    ],
)

# ── Top: badge + gauge side by side ──
top_l, top_r = st.columns([1.2, 0.8])
with top_l:
    st.markdown(health_badge(prediction.health_state), unsafe_allow_html=True)
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    render_panel("Operator summary", summarize_prediction(prediction, selected["display_name"]))
with top_r:
    st.plotly_chart(rul_gauge_chart(prediction.predicted_rul), use_container_width=True)

# ── Metrics row ──
c1, c2, c3 = st.columns(3)
with c1:
    render_metric_card("Health score", f"{prediction.health_score:.0f}/100", "Proximity to healthy baseline")
with c2:
    cp = prediction.change_point if prediction.change_point is not None else "—"
    render_metric_card("Change-point", str(cp), "Cycle where drift began")
with c3:
    drivers = ", ".join(d.replace("_", " ") for d in prediction.top_drivers[:3])
    render_metric_card("Top drivers", drivers, prediction.recommended_action)

st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

# ── Charts side by side ──
ch_l, ch_r = st.columns(2)
with ch_l:
    st.markdown("## Sensor drift")
    st.plotly_chart(
        sensor_trend_chart(frame, prediction.top_drivers or ["sensor_1", "sensor_2", "sensor_3"]),
        use_container_width=True,
    )
with ch_r:
    st.markdown("## Health timeline")
    st.plotly_chart(health_timeline_chart(frame, prediction.change_point), use_container_width=True)

# ── Technical details collapsed ──
with st.expander("Technical details"):
    st.caption(
        f"Validation RMSE {metrics.get('rmse', 0):.2f} · MAE {metrics.get('mae', 0):.2f} · "
        f"Window {metrics.get('inference_window', 15)} cycles · NASA CMAPSS FD001"
    )
    st.json(
        {
            "machine_id": prediction.machine_id,
            "predicted_rul": prediction.predicted_rul,
            "health_score": prediction.health_score,
            "health_state": prediction.health_state,
            "change_point": prediction.change_point,
            "top_drivers": prediction.top_drivers,
        }
    )
