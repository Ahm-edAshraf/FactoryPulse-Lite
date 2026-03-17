"""Chart builders for the FactoryPulse dashboard (dark theme)."""

from __future__ import annotations

import plotly.graph_objects as go
import pandas as pd

from factorypulse.models.health import build_health_index

_BG = "rgba(0,0,0,0)"
_GRID = "rgba(255,255,255,0.04)"
_TEXT = "#8b92a5"
_TEXT_LIGHT = "#f0f2f5"
_TEAL = "#00d4aa"
_AMBER = "#f0b429"
_ORANGE = "#e8734a"
_RED = "#ef4444"
_BLUE = "#3b82f6"


def _dark_layout(figure: go.Figure, height: int | None = None) -> go.Figure:
    layout_kwargs: dict = {
        "margin": {"l": 16, "r": 16, "t": 32, "b": 16},
        "plot_bgcolor": _BG,
        "paper_bgcolor": _BG,
        "font": {"family": "DM Sans, sans-serif", "color": _TEXT, "size": 12},
        "xaxis": {"gridcolor": _GRID, "zeroline": False, "tickfont": {"color": _TEXT}},
        "yaxis": {"gridcolor": _GRID, "zeroline": False, "tickfont": {"color": _TEXT}},
    }
    if height:
        layout_kwargs["height"] = height
    figure.update_layout(**layout_kwargs)
    return figure


def sensor_trend_chart(frame: pd.DataFrame, sensors: list[str]) -> go.Figure:
    figure = go.Figure()
    palette = [_TEAL, _ORANGE, _BLUE]
    sensor_frame = frame.copy()
    baseline_window = max(3, min(12, len(sensor_frame)))

    for index, sensor in enumerate(sensors):
        if sensor not in sensor_frame.columns:
            continue
        baseline = float(sensor_frame[sensor].head(baseline_window).mean())
        denominator = abs(baseline) if abs(baseline) > 1e-6 else 1.0
        normalized = ((sensor_frame[sensor] - baseline) / denominator) * 100
        figure.add_trace(
            go.Scatter(
                x=sensor_frame["cycle"],
                y=normalized,
                mode="lines",
                name=sensor.replace("_", " ").title(),
                line={"width": 2.5, "color": palette[index % len(palette)]},
            )
        )

    figure.update_layout(
        xaxis_title="Cycle",
        yaxis_title="Drift from baseline (%)",
        legend={"font": {"color": _TEXT}},
        hovermode="x unified",
    )
    return _dark_layout(figure, height=320)


def health_timeline_chart(frame: pd.DataFrame, change_point: int | None) -> go.Figure:
    health_index = build_health_index(frame)
    figure = go.Figure()

    figure.add_hrect(y0=75, y1=100, fillcolor="rgba(0,212,170,0.05)", line_width=0)
    figure.add_hrect(y0=50, y1=75, fillcolor="rgba(240,180,41,0.05)", line_width=0)
    figure.add_hrect(y0=30, y1=50, fillcolor="rgba(232,115,74,0.05)", line_width=0)
    figure.add_hrect(y0=0, y1=30, fillcolor="rgba(239,68,68,0.05)", line_width=0)

    figure.add_trace(
        go.Scatter(
            x=frame["cycle"],
            y=health_index,
            mode="lines",
            name="Health",
            line={"width": 2.5, "color": _TEAL},
            fill="tozeroy",
            fillcolor="rgba(0,212,170,0.08)",
        )
    )

    if change_point is not None:
        figure.add_vline(x=change_point, line_dash="dash", line_color=_RED, line_width=1.5)
        figure.add_annotation(
            x=change_point, y=95, text="Change-point", showarrow=False,
            bgcolor="rgba(21,24,35,0.9)", bordercolor="rgba(255,255,255,0.1)",
            font={"color": _TEXT_LIGHT, "size": 11},
        )

    figure.update_layout(
        xaxis_title="Cycle",
        yaxis_title="Health score",
        yaxis_range=[0, 100],
        showlegend=False,
        hovermode="x unified",
    )
    return _dark_layout(figure, height=320)


def rul_gauge_chart(predicted_rul: float) -> go.Figure:
    figure = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=predicted_rul,
            number={"suffix": " cycles", "font": {"size": 28, "color": _TEXT_LIGHT, "family": "Sora, sans-serif"}},
            gauge={
                "axis": {"range": [0, 130], "tickwidth": 1, "tickcolor": "rgba(255,255,255,0.1)"},
                "bar": {"color": _TEAL, "thickness": 0.35},
                "bgcolor": "rgba(255,255,255,0.03)",
                "borderwidth": 1,
                "bordercolor": "rgba(255,255,255,0.08)",
                "steps": [
                    {"range": [0, 25], "color": "rgba(239,68,68,0.15)"},
                    {"range": [25, 60], "color": "rgba(240,180,41,0.12)"},
                    {"range": [60, 130], "color": "rgba(0,212,170,0.10)"},
                ],
            },
            title={"text": "Remaining Useful Life", "font": {"size": 14, "color": _TEXT}},
        )
    )
    figure.update_layout(
        margin={"l": 10, "r": 10, "t": 48, "b": 10},
        paper_bgcolor=_BG,
        height=260,
    )
    return figure


def fleet_health_bar_chart(fleet_rows: list[dict]) -> go.Figure:
    ordered = list(reversed(fleet_rows))
    colors = {
        "Healthy": _TEAL,
        "Watchlist": _AMBER,
        "Impaired": _ORANGE,
        "Critical": _RED,
    }
    figure = go.Figure(
        data=[
            go.Bar(
                x=[item["prediction"].health_score for item in ordered],
                y=[item["display_name"] for item in ordered],
                orientation="h",
                marker_color=[colors.get(item["prediction"].health_state, _TEAL) for item in ordered],
                text=[f"{item['prediction'].predicted_rul:.0f} cyc" for item in ordered],
                textposition="outside",
                textfont={"color": _TEXT, "size": 11},
            )
        ]
    )
    figure.update_layout(
        xaxis_title="Health score",
        yaxis_title="",
        showlegend=False,
        xaxis_range=[0, 105],
    )
    return _dark_layout(figure, height=280)
