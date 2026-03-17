"""Schema utilities for sensor frames and model outputs."""

from __future__ import annotations

from typing import Iterable

import pandas as pd
from pydantic import BaseModel, Field


BASE_COLUMNS = [
    "unit_id",
    "cycle",
    "op_setting_1",
    "op_setting_2",
    "op_setting_3",
]
SENSOR_COLUMNS = [f"sensor_{index}" for index in range(1, 22)]
CMAPSS_COLUMNS = BASE_COLUMNS + SENSOR_COLUMNS
MIN_REQUIRED_COLUMNS = set(BASE_COLUMNS + ["sensor_1", "sensor_2"])


def missing_required_columns(columns: Iterable[str]) -> list[str]:
    present = set(columns)
    return sorted(MIN_REQUIRED_COLUMNS - present)


def validate_sensor_frame(frame: pd.DataFrame) -> pd.DataFrame:
    missing = missing_required_columns(frame.columns)
    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"missing required columns: {missing_text}")
    return frame.copy()


class MachinePrediction(BaseModel):
    machine_id: str
    predicted_rul: float = Field(ge=0)
    health_score: float = Field(ge=0, le=100)
    health_state: str
    change_point: int | None
    top_drivers: list[str]
    recommended_action: str


class ModelMetrics(BaseModel):
    rmse: float = Field(ge=0)
    mae: float = Field(ge=0)
    validation_samples: int = Field(ge=1)
    inference_window: int = Field(ge=1)
