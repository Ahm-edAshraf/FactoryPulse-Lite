"""Benchmarking and robustness evaluation for the RUL model."""

from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path
import time

import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

from factorypulse.config import CONFIG_ROOT, MODEL_ROOT, RAW_DATA_ROOT, load_yaml_config
from factorypulse.data.loaders import ensure_cmapss_files, load_cmapss_split, load_rul_truth
from factorypulse.data.preprocessing import prepare_sensor_frame
from factorypulse.features.build_features import build_inference_features, build_training_features
from factorypulse.models.infer import load_model_artifacts, predict_machine_state
from factorypulse.models.train_rul import split_by_unit


def _load_training_payload(config_path: str | Path | None = None) -> dict[str, object]:
    config = load_yaml_config(config_path or CONFIG_ROOT / "model.yaml")
    subset_id = config.get("dataset", {}).get("subset", "FD001")
    window_size = int(config.get("features", {}).get("window_size", 15))
    rul_cap = int(config.get("features", {}).get("rul_cap", 125))
    validation_fraction = float(config.get("training", {}).get("validation_fraction", 0.25))
    random_state = int(config.get("training", {}).get("random_state", 42))

    raw_paths = ensure_cmapss_files(RAW_DATA_ROOT / "cmapss", subset_id=subset_id)
    train_frame = prepare_sensor_frame(load_cmapss_split(raw_paths["train"]))
    feature_frame, feature_columns = build_training_features(train_frame, window_size=window_size, rul_cap=rul_cap)
    train_features, validation_features = split_by_unit(
        feature_frame,
        validation_fraction=validation_fraction,
        random_state=random_state,
    )
    return {
        "config": config,
        "subset_id": subset_id,
        "window_size": window_size,
        "random_state": random_state,
        "raw_paths": raw_paths,
        "train_frame": train_frame,
        "feature_columns": feature_columns,
        "train_features": train_features,
        "validation_features": validation_features,
    }


def _predict_test_split(
    model,
    feature_columns: list[str],
    test_frame: pd.DataFrame,
    truths: pd.DataFrame,
    window_size: int,
) -> tuple[list[float], list[float]]:
    predictions: list[float] = []
    actuals: list[float] = []
    for idx, unit_id in enumerate(sorted(test_frame["unit_id"].unique())):
        machine_frame = test_frame[test_frame["unit_id"] == unit_id].reset_index(drop=True)
        inference_features = build_inference_features(
            machine_frame,
            window_size=window_size,
            feature_columns=feature_columns,
        )
        prediction = max(0.0, float(model.predict(inference_features.iloc[[-1]])[0]))
        predictions.append(prediction)
        actuals.append(float(truths.iloc[idx]["rul"]))
    return predictions, actuals


def _metric_snapshot(actuals: list[float], predictions: list[float]) -> dict[str, float]:
    return {
        "rmse": float(root_mean_squared_error(actuals, predictions)),
        "mae": float(mean_absolute_error(actuals, predictions)),
        "samples": len(actuals),
    }


def _baseline_models(random_state: int) -> dict[str, object]:
    return {
        "Mean RUL": DummyRegressor(strategy="mean"),
        "Median RUL": DummyRegressor(strategy="median"),
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(
            n_estimators=160,
            max_depth=16,
            min_samples_leaf=2,
            n_jobs=-1,
            random_state=random_state,
        ),
    }


def _sensor_columns(frame: pd.DataFrame) -> list[str]:
    return [column for column in frame.columns if column.startswith("sensor_")]


def _apply_noise(frame: pd.DataFrame, rng: np.random.Generator, train_frame: pd.DataFrame, noise_scale: float) -> pd.DataFrame:
    noisy = frame.copy()
    sensor_columns = _sensor_columns(noisy)
    reference_scale = train_frame[sensor_columns].std().replace(0, 1.0).fillna(1.0)
    for column in sensor_columns:
        noisy[column] = noisy[column] + rng.normal(0.0, float(reference_scale[column]) * noise_scale, size=len(noisy))
    return noisy


def _apply_missingness(frame: pd.DataFrame, rng: np.random.Generator, missing_ratio: float) -> pd.DataFrame:
    corrupted = frame.copy()
    sensor_columns = _sensor_columns(corrupted)
    if not sensor_columns:
        return corrupted

    corrupted = corrupted.astype({column: float for column in sensor_columns})
    mask = rng.random((len(corrupted), len(sensor_columns))) < missing_ratio
    corrupted.loc[:, sensor_columns] = corrupted[sensor_columns].mask(mask)
    return corrupted


def _apply_sensor_dropout(frame: pd.DataFrame, rng: np.random.Generator, count: int) -> pd.DataFrame:
    corrupted = frame.copy()
    sensor_columns = _sensor_columns(corrupted)
    if not sensor_columns:
        return corrupted

    count = min(count, len(sensor_columns))
    dropped = rng.choice(sensor_columns, size=count, replace=False)
    for column in dropped:
        corrupted[column] = float(corrupted[column].iloc[0])
    return corrupted


def _stress_metrics(
    model,
    feature_columns: list[str],
    train_frame: pd.DataFrame,
    test_frame: pd.DataFrame,
    truths: pd.DataFrame,
    window_size: int,
    base_rmse: float,
) -> list[dict[str, object]]:
    scenarios: list[tuple[str, str, pd.DataFrame]] = []
    rng = np.random.default_rng(42)

    scenarios.append(("noise_2pct", "Gaussian noise at 2% of train-set sensor sigma", _apply_noise(test_frame, rng, train_frame, 0.02)))
    scenarios.append(("missing_5pct", "Random 5% sensor gaps with forward-fill recovery", _apply_missingness(test_frame, rng, 0.05)))
    scenarios.append(("dropout_3_sensors", "Three sensor channels stuck at their initial reading", _apply_sensor_dropout(test_frame, rng, 3)))

    combined = _apply_noise(test_frame, rng, train_frame, 0.015)
    combined = _apply_missingness(combined, rng, 0.03)
    scenarios.append(("combined_shift", "Combined 1.5% noise plus 3% missing sensors", combined))

    reports: list[dict[str, object]] = []
    for scenario_id, label, candidate in scenarios:
        prepared = prepare_sensor_frame(candidate)
        predictions, actuals = _predict_test_split(model, feature_columns, prepared, truths, window_size)
        metrics = _metric_snapshot(actuals, predictions)
        reports.append(
            {
                "scenario_id": scenario_id,
                "label": label,
                "rmse": metrics["rmse"],
                "mae": metrics["mae"],
                "delta_rmse": round(metrics["rmse"] - base_rmse, 3),
            }
        )
    return reports


def _latency_snapshot(sample_frame: pd.DataFrame, repeats: int = 50) -> dict[str, float]:
    durations: list[float] = []
    for _ in range(repeats):
        start = time.perf_counter()
        predict_machine_state(sample_frame)
        durations.append((time.perf_counter() - start) * 1000)
    return {
        "mean_ms": float(np.mean(durations)),
        "p95_ms": float(np.percentile(durations, 95)),
        "repeats": repeats,
    }


def evaluate_model(config_path: str | Path | None = None, model_dir: str | Path | None = None) -> dict[str, object]:
    payload = _load_training_payload(config_path=config_path)
    config = payload["config"]
    subset_id = str(payload["subset_id"])
    window_size = int(payload["window_size"])
    random_state = int(payload["random_state"])
    raw_paths = payload["raw_paths"]
    train_frame = payload["train_frame"]
    feature_columns = payload["feature_columns"]
    train_features = payload["train_features"]
    validation_features = payload["validation_features"]

    model, _, _ = load_model_artifacts(model_dir)
    validation_predictions = model.predict(validation_features[feature_columns])
    validation_metrics = _metric_snapshot(validation_features["rul_target"].tolist(), validation_predictions.tolist())

    test_frame = prepare_sensor_frame(load_cmapss_split(raw_paths["test"]))
    truths = load_rul_truth(raw_paths["truth"])
    official_predictions, actuals = _predict_test_split(model, feature_columns, test_frame, truths, window_size)
    official_metrics = _metric_snapshot(actuals, official_predictions)

    baselines: list[dict[str, object]] = []
    for label, baseline in _baseline_models(random_state=random_state).items():
        baseline.fit(train_features[feature_columns], train_features["rul_target"])
        baseline_predictions, baseline_actuals = _predict_test_split(
            baseline,
            feature_columns,
            test_frame,
            truths,
            window_size,
        )
        metrics = _metric_snapshot(baseline_actuals, baseline_predictions)
        metrics["name"] = label
        baselines.append(metrics)
    baselines.sort(key=lambda item: item["rmse"])

    robustness = _stress_metrics(
        model=model,
        feature_columns=feature_columns,
        train_frame=train_frame,
        test_frame=test_frame,
        truths=truths,
        window_size=window_size,
        base_rmse=official_metrics["rmse"],
    )

    sample_unit = int(sorted(test_frame["unit_id"].unique())[0])
    sample_frame = test_frame[test_frame["unit_id"] == sample_unit].reset_index(drop=True)
    latency = _latency_snapshot(sample_frame)

    best_baseline = baselines[0]
    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "dataset": {
            "subset": subset_id,
            "train_units": int(train_frame["unit_id"].nunique()),
            "test_units": int(test_frame["unit_id"].nunique()),
            "feature_count": len(feature_columns),
            "window_size": window_size,
        },
        "model": {
            "name": "XGBoost RUL regressor",
            "training_config": config,
        },
        "holdout_validation": validation_metrics,
        "official_test": official_metrics,
        "baselines": baselines,
        "robustness": robustness,
        "latency_ms": latency,
        "summary": {
            "best_baseline_name": best_baseline["name"],
            "rmse_gain_vs_best_baseline": round(best_baseline["rmse"] - official_metrics["rmse"], 3),
            "worst_stress_delta_rmse": round(max(item["delta_rmse"] for item in robustness), 3),
        },
    }

    artifact_root = Path(model_dir or MODEL_ROOT)
    artifact_root.mkdir(parents=True, exist_ok=True)
    (artifact_root / "evaluation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    report = evaluate_model()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
