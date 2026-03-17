"""High-level scoring helpers for machine trajectories."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from factorypulse.models.infer import predict_machine_state
from factorypulse.schemas import MachinePrediction
from factorypulse.services.planner import estimate_avoided_downtime_value


def score_machine_frame(
    frame: pd.DataFrame,
    model_dir: str | Path | None = None,
    window_size: int = 15,
    failure_cost: float = 1500,
    maintenance_cost: float = 300,
) -> tuple[MachinePrediction, float]:
    prediction = predict_machine_state(frame, model_dir=model_dir, window_size=window_size)
    roi_value = estimate_avoided_downtime_value(
        predicted_rul=prediction.predicted_rul,
        failure_cost=failure_cost,
        maintenance_cost=maintenance_cost,
    )
    return prediction, roi_value
