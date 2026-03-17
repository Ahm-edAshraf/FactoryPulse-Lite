"""Health scoring, status mapping, and change-point detection."""

from __future__ import annotations

from functools import lru_cache
import numpy as np
import pandas as pd
import ruptures as rpt

from factorypulse.config import CONFIG_ROOT, load_yaml_config


def _sensor_columns(frame: pd.DataFrame) -> list[str]:
    return [column for column in frame.columns if column.startswith("sensor_")]


def build_health_index(frame: pd.DataFrame) -> pd.Series:
    sensor_columns = _sensor_columns(frame)
    if not sensor_columns:
        return pd.Series([100.0] * len(frame), index=frame.index)

    window = max(2, min(5, len(frame)))
    baseline = frame[sensor_columns].head(window).mean()
    drift = (frame[sensor_columns] - baseline).abs().mean(axis=1)
    severity = drift.clip(lower=0, upper=20) / 20
    return 100 - severity * 100


def compute_health_score(frame: pd.DataFrame) -> float:
    health_index = build_health_index(frame)
    return float(np.clip(health_index.iloc[-1], 0.0, 100.0))


@lru_cache(maxsize=1)
def _health_thresholds() -> dict[str, float]:
    config = load_yaml_config(CONFIG_ROOT / "app.yaml")
    return config.get(
        "health",
        {"healthy_min": 75, "watchlist_min": 50, "impaired_min": 25, "rul_reference": 125},
    )


def blend_health_score(sensor_health_score: float, predicted_rul: float) -> float:
    thresholds = _health_thresholds()
    rul_reference = max(float(thresholds.get("rul_reference", 125)), 1.0)
    rul_component = np.clip((predicted_rul / rul_reference) * 100, 0, 100)
    blended_score = min(sensor_health_score, (sensor_health_score * 0.3) + (rul_component * 0.7))
    return float(np.clip(blended_score, 0.0, 100.0))


def map_health_state(health_score: float) -> str:
    thresholds = _health_thresholds()
    if health_score >= float(thresholds.get("healthy_min", 75)):
        return "Healthy"
    if health_score >= float(thresholds.get("watchlist_min", 50)):
        return "Watchlist"
    if health_score >= float(thresholds.get("impaired_min", 25)):
        return "Impaired"
    return "Critical"


def detect_change_point(frame: pd.DataFrame) -> int | None:
    if len(frame) < 6:
        return None

    health_signal = (100 - build_health_index(frame)).to_numpy(dtype=float).reshape(-1, 1)
    algo = rpt.Pelt(model="l2").fit(health_signal)
    breakpoints = algo.predict(pen=max(3, len(frame) * 0.8))

    for breakpoint in breakpoints:
        if breakpoint < len(frame):
            return int(frame.iloc[breakpoint - 1]["cycle"])
    return None


def top_degradation_drivers(frame: pd.DataFrame, top_k: int = 3) -> list[str]:
    sensor_columns = _sensor_columns(frame)
    if not sensor_columns:
        return []

    baseline = frame[sensor_columns].head(max(2, min(5, len(frame)))).mean()
    latest = frame[sensor_columns].iloc[-1]
    scale = baseline.abs().replace(0, 1.0).fillna(1.0)
    impact = ((latest - baseline).abs() / scale).sort_values(ascending=False)
    return [str(column) for column in impact.head(top_k).index]


def recommend_action(health_state: str, predicted_rul: float) -> str:
    if health_state == "Critical" or predicted_rul <= 10:
        return "Schedule maintenance immediately and prepare spare parts."
    if health_state == "Impaired" or predicted_rul <= 25:
        return "Inspect the machine today and lock a maintenance slot this week."
    if health_state == "Watchlist" or predicted_rul <= 50:
        return "Monitor daily and plan the next maintenance window."
    return "Machine is stable; continue routine monitoring."
