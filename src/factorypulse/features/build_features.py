"""Reusable time-series feature builders."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd


IDENTIFIER_COLUMNS = ["unit_id", "cycle"]


def _feature_base_columns(frame: pd.DataFrame) -> list[str]:
    excluded = {"unit_id", "cycle", "rul_target"}
    return [column for column in frame.columns if column not in excluded]


def _compute_slope(values: pd.Series) -> float:
    if len(values) < 2:
        return 0.0
    return float((values.iloc[-1] - values.iloc[0]) / (len(values) - 1))


def _build_window_features(frame: pd.DataFrame, window_size: int) -> pd.DataFrame:
    sorted_frame = frame.sort_values(IDENTIFIER_COLUMNS).reset_index(drop=True)
    feature_columns = _feature_base_columns(sorted_frame)
    grouped = sorted_frame.groupby("unit_id", group_keys=False)

    derived_features: dict[str, pd.Series] = {}
    for column in feature_columns:
        rolling = grouped[column].rolling(window=window_size, min_periods=window_size)
        derived_features[f"{column}_mean"] = rolling.mean().reset_index(level=0, drop=True)
        derived_features[f"{column}_std"] = rolling.std(ddof=0).reset_index(level=0, drop=True)
        derived_features[f"{column}_min"] = rolling.min().reset_index(level=0, drop=True)
        derived_features[f"{column}_max"] = rolling.max().reset_index(level=0, drop=True)
        derived_features[f"{column}_delta"] = grouped[column].diff(periods=window_size - 1)
        derived_features[f"{column}_ema"] = grouped[column].transform(lambda series: series.ewm(span=window_size, adjust=False).mean())
        derived_features[f"{column}_slope"] = rolling.apply(_compute_slope, raw=False).reset_index(level=0, drop=True)

    features = pd.concat([sorted_frame[IDENTIFIER_COLUMNS], pd.DataFrame(derived_features)], axis=1)
    return features.dropna().reset_index(drop=True)


def build_training_features(
    frame: pd.DataFrame,
    window_size: int = 5,
    rul_cap: int = 125,
) -> tuple[pd.DataFrame, list[str]]:
    features = _build_window_features(frame, window_size=window_size)

    max_cycles = frame.groupby("unit_id")["cycle"].max().rename("max_cycle")
    features = features.merge(max_cycles, on="unit_id", how="left")
    features["rul_target"] = (features["max_cycle"] - features["cycle"]).clip(lower=0, upper=rul_cap)
    features = features.drop(columns=["max_cycle"])

    feature_columns = [
        column
        for column in features.columns
        if column not in {"unit_id", "cycle", "rul_target"}
    ]
    ordered_columns = ["unit_id", "cycle", *feature_columns, "rul_target"]
    return features[ordered_columns], feature_columns


def build_inference_features(
    frame: pd.DataFrame,
    window_size: int,
    feature_columns: Iterable[str],
) -> pd.DataFrame:
    feature_frame = _build_window_features(frame, window_size=window_size)
    ordered = list(feature_columns)
    return feature_frame.reindex(columns=ordered, fill_value=0.0)
