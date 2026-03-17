"""Model artifact loading and machine-level inference."""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from factorypulse.config import MODEL_ROOT
from factorypulse.features.build_features import build_inference_features
from factorypulse.models.health import (
    blend_health_score,
    compute_health_score,
    detect_change_point,
    map_health_state,
    recommend_action,
    top_degradation_drivers,
)
from factorypulse.schemas import MachinePrediction


@lru_cache(maxsize=4)
def load_model_artifacts(model_dir: str | Path | None = None) -> tuple[Any, list[str], dict[str, Any]]:
    artifact_root = Path(model_dir or MODEL_ROOT)
    model = joblib.load(artifact_root / "rul_xgb.joblib")
    feature_columns = json.loads((artifact_root / "feature_columns.json").read_text(encoding="utf-8"))
    metrics_path = artifact_root / "metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.exists() else {}
    return model, feature_columns, metrics


def predict_machine_state(
    frame: pd.DataFrame,
    model_dir: str | Path | None = None,
    window_size: int = 15,
) -> MachinePrediction:
    model, feature_columns, _ = load_model_artifacts(model_dir)
    required_columns = ["unit_id", "cycle", *sorted({column.rsplit("_", 1)[0] for column in feature_columns})]
    missing_columns = [column for column in required_columns if column not in frame.columns]
    if missing_columns:
        missing_text = ", ".join(missing_columns)
        raise ValueError(f"missing input columns: {missing_text}")

    if len(frame) < window_size:
        raise ValueError(f"machine trajectory must contain at least {window_size} rows")

    inference_features = build_inference_features(frame, window_size=window_size, feature_columns=feature_columns)
    latest_vector = inference_features.iloc[[-1]]
    predicted_rul = max(0.0, float(model.predict(latest_vector)[0]))
    health_score = blend_health_score(compute_health_score(frame), predicted_rul)
    health_state = map_health_state(health_score)
    change_point = detect_change_point(frame)
    top_drivers = model_based_top_drivers(model, latest_vector, feature_columns, fallback_frame=frame)

    return MachinePrediction(
        machine_id=str(frame["unit_id"].iloc[-1]),
        predicted_rul=predicted_rul,
        health_score=health_score,
        health_state=health_state,
        change_point=change_point,
        top_drivers=top_drivers,
        recommended_action=recommend_action(health_state, predicted_rul),
    )


def model_based_top_drivers(model: Any, _latest_vector: pd.DataFrame, feature_columns: list[str], fallback_frame: pd.DataFrame) -> list[str]:
    sensor_drivers = top_degradation_drivers(fallback_frame)

    importances = getattr(model, "feature_importances_", None)
    if importances is None or len(importances) != len(feature_columns):
        return sensor_drivers

    importance_map: dict[str, float] = {}
    for column, importance in zip(feature_columns, importances):
        parts = column.split("_", 2)
        base = "_".join(parts[:2]) if parts[0] == "sensor" else column.rsplit("_", 1)[0]
        importance_map[base] = importance_map.get(base, 0.0) + float(importance)

    drift_scores: dict[str, float] = {}
    sensor_cols = [c for c in fallback_frame.columns if c.startswith("sensor_")]
    baseline_window = max(2, min(5, len(fallback_frame)))
    baseline = fallback_frame[sensor_cols].head(baseline_window).mean()
    latest = fallback_frame[sensor_cols].iloc[-1]
    scale = baseline.abs().replace(0, 1.0).fillna(1.0)
    for col in sensor_cols:
        drift = abs(float(latest[col]) - float(baseline[col])) / float(scale[col])
        model_weight = importance_map.get(col, 0.0)
        drift_scores[col] = drift * (1.0 + model_weight)

    ordered = sorted(drift_scores.items(), key=lambda item: item[1], reverse=True)
    return [name for name, _ in ordered[:3]]
