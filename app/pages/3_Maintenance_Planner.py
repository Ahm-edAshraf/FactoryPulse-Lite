from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from factorypulse.dashboard.cards import (
    apply_global_styles,
    health_badge,
    render_machine_row,
    render_metric_card,
    render_page_header,
    render_panel,
    render_sidebar_brand,
)
from factorypulse.dashboard.data import get_active_fleet, load_app_config, render_sidebar_upload, resolve_window_size


def _window(state: str) -> str:
    return {
        "Critical": "0-24 h",
        "Impaired": "This week",
        "Watchlist": "Next shutdown",
        "Healthy": "Routine",
    }.get(state, "Review")


st.set_page_config(page_title="Maintenance Planner | FactoryPulse", page_icon="⚙️", layout="wide")
apply_global_styles()
render_sidebar_brand()

app_config = load_app_config().get("app", {})
window_size = resolve_window_size(int(app_config.get("default_window_size", 15)))

render_sidebar_upload(window_size)

try:
    fleet = get_active_fleet(window_size=window_size)
except FileNotFoundError as error:
    st.error(f"Missing artifacts: {error}")
    st.caption("Run `make train` first.")
    st.stop()

rows = []
for rank, item in enumerate(fleet, start=1):
    pred = item["prediction"]
    rows.append({
        "#": rank,
        "Machine": item["display_name"],
        "Line": item["line_name"],
        "State": pred.health_state,
        "RUL": round(pred.predicted_rul, 1),
        "Health": round(pred.health_score, 1),
        "Window": _window(pred.health_state),
        "Saved ($)": round(item["roi_value"], 0),
        "Action": pred.recommended_action,
    })

df = pd.DataFrame(rows)
total_value = float(df["Saved ($)"].sum())
top = df.iloc[0]
at_risk = int(df["State"].isin(["Critical", "Impaired", "Watchlist"]).sum())

render_page_header(
    title="Maintenance Planner",
    subtitle="Service queue ordered by urgency. Schedule interventions to protect production value.",
    eyebrow="Action schedule",
    chips=[
        ("Next up", str(top["Machine"])),
        ("Protected", f"${total_value:,.0f}"),
        ("At risk", str(at_risk)),
    ],
)

c1, c2, c3 = st.columns(3)
with c1:
    render_metric_card("Immediate", str(top["Machine"]), str(top["Window"]))
with c2:
    render_metric_card("Protected value", f"${total_value:,.0f}", "Downtime cost avoided")
with c3:
    render_metric_card("At risk", str(at_risk), "Machines needing attention")

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

left, right = st.columns([1.4, 1])

with left:
    st.markdown("## Service queue")
    for item in fleet:
        pred = item["prediction"]
        rank = next(r["#"] for r in rows if r["Machine"] == item["display_name"])
        render_machine_row(
            rank=rank,
            name=item["display_name"],
            meta=f"{item['line_name']} · Window: {_window(pred.health_state)}",
            badge_html=health_badge(pred.health_state),
            rul=f"{pred.predicted_rul:.0f} cyc",
            health=f"{pred.health_score:.0f}",
            cost=f"${item['roi_value']:,.0f}",
        )

with right:
    render_panel(
        "Scheduling logic",
        "Critical → immediate intervention (0-24h). "
        "Impaired → this week. "
        "Watchlist → next planned shutdown. "
        "Healthy → routine schedule.",
    )

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
with st.expander("Full planning table"):
    st.dataframe(df, use_container_width=True, hide_index=True)
