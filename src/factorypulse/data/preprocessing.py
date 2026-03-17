"""Preprocessing helpers for sensor data."""

from __future__ import annotations

import pandas as pd

from factorypulse.schemas import validate_sensor_frame


def prepare_sensor_frame(frame: pd.DataFrame) -> pd.DataFrame:
    prepared = validate_sensor_frame(frame)
    prepared = prepared.sort_values(["unit_id", "cycle"]).reset_index(drop=True)

    numeric_columns = prepared.columns
    prepared[numeric_columns] = prepared[numeric_columns].apply(pd.to_numeric, errors="coerce")
    prepared[numeric_columns] = prepared.groupby("unit_id", group_keys=False)[numeric_columns].ffill()
    prepared[numeric_columns] = prepared[numeric_columns].fillna(prepared.median(numeric_only=True))
    return prepared
