"""Train the baseline Remaining Useful Life regressor."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

from factorypulse.config import CONFIG_ROOT, INTERIM_DATA_ROOT, MODEL_ROOT, RAW_DATA_ROOT, ensure_project_directories, load_yaml_config
from factorypulse.data.loaders import ensure_cmapss_files, load_cmapss_split
from factorypulse.data.preprocessing import prepare_sensor_frame
from factorypulse.features.build_features import build_training_features
from factorypulse.schemas import ModelMetrics


def split_by_unit(frame: pd.DataFrame, validation_fraction: float, random_state: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    unit_ids = frame["unit_id"].drop_duplicates().tolist()
    train_ids, validation_ids = train_test_split(unit_ids, test_size=validation_fraction, random_state=random_state)
    train_frame = frame[frame["unit_id"].isin(train_ids)].reset_index(drop=True)
    validation_frame = frame[frame["unit_id"].isin(validation_ids)].reset_index(drop=True)
    return train_frame, validation_frame


def train_model(config_path: str | Path | None = None) -> ModelMetrics:
    ensure_project_directories()
    config = load_yaml_config(config_path or CONFIG_ROOT / "model.yaml")

    subset_id = config.get("dataset", {}).get("subset", "FD001")
    window_size = int(config.get("features", {}).get("window_size", 15))
    rul_cap = int(config.get("features", {}).get("rul_cap", 125))
    validation_fraction = float(config.get("training", {}).get("validation_fraction", 0.25))
    random_state = int(config.get("training", {}).get("random_state", 42))
    xgb_params = config.get("model", {})

    raw_paths = ensure_cmapss_files(RAW_DATA_ROOT / "cmapss", subset_id=subset_id)
    train_frame = prepare_sensor_frame(load_cmapss_split(raw_paths["train"]))
    INTERIM_DATA_ROOT.mkdir(parents=True, exist_ok=True)
    train_frame.to_csv(INTERIM_DATA_ROOT / f"train_{subset_id}_prepared.csv", index=False)
    feature_frame, feature_columns = build_training_features(train_frame, window_size=window_size, rul_cap=rul_cap)
    train_features, validation_features = split_by_unit(feature_frame, validation_fraction=validation_fraction, random_state=random_state)

    model = XGBRegressor(
        objective="reg:squarederror",
        n_estimators=int(xgb_params.get("n_estimators", 250)),
        max_depth=int(xgb_params.get("max_depth", 6)),
        learning_rate=float(xgb_params.get("learning_rate", 0.05)),
        subsample=float(xgb_params.get("subsample", 0.9)),
        colsample_bytree=float(xgb_params.get("colsample_bytree", 0.9)),
        random_state=random_state,
        n_jobs=int(xgb_params.get("n_jobs", 4)),
    )
    model.fit(train_features[feature_columns], train_features["rul_target"])

    predictions = model.predict(validation_features[feature_columns])
    metrics = ModelMetrics(
        rmse=float(root_mean_squared_error(validation_features["rul_target"], predictions)),
        mae=float(mean_absolute_error(validation_features["rul_target"], predictions)),
        validation_samples=len(validation_features),
        inference_window=window_size,
    )

    MODEL_ROOT.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_ROOT / "rul_xgb.joblib")
    (MODEL_ROOT / "feature_columns.json").write_text(json.dumps(feature_columns, indent=2), encoding="utf-8")
    (MODEL_ROOT / "metrics.json").write_text(metrics.model_dump_json(indent=2), encoding="utf-8")
    (MODEL_ROOT / "training_config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    return metrics


def main() -> None:
    metrics = train_model()
    print(metrics.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
