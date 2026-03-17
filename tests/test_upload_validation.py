from pathlib import Path
import json
import sys

import joblib
import pandas as pd
import pytest
from sklearn.dummy import DummyRegressor


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def _artifact_dir(tmp_path: Path) -> Path:
    from factorypulse.features.build_features import build_training_features

    frame = pd.DataFrame(
        {
            "unit_id": [1, 1, 1],
            "cycle": [1, 2, 3],
            "op_setting_1": [0.1, 0.1, 0.1],
            "op_setting_2": [0.2, 0.2, 0.2],
            "op_setting_3": [0.3, 0.3, 0.3],
            "sensor_1": [10.0, 10.5, 11.0],
            "sensor_2": [5.0, 5.5, 6.0],
            "sensor_3": [7.0, 7.2, 7.4],
        }
    )
    features, feature_columns = build_training_features(frame, window_size=2, rul_cap=5)
    model = DummyRegressor(strategy="constant", constant=10)
    model.fit(features[feature_columns], features["rul_target"])

    artifact_dir = tmp_path / "models"
    artifact_dir.mkdir()
    joblib.dump(model, artifact_dir / "rul_xgb.joblib")
    (artifact_dir / "feature_columns.json").write_text(json.dumps(feature_columns), encoding="utf-8")
    (artifact_dir / "metrics.json").write_text(json.dumps({"inference_window": 2}), encoding="utf-8")
    return artifact_dir


def test_required_model_input_columns_fall_back_without_artifacts(tmp_path: Path) -> None:
    from factorypulse.models.infer import required_model_input_columns
    from factorypulse.schemas import CMAPSS_COLUMNS

    assert required_model_input_columns(tmp_path) == CMAPSS_COLUMNS


def test_required_model_input_columns_read_feature_artifacts(tmp_path: Path) -> None:
    from factorypulse.models.infer import required_model_input_columns

    artifact_dir = _artifact_dir(tmp_path)

    assert required_model_input_columns(artifact_dir) == [
        "unit_id",
        "cycle",
        "op_setting_1",
        "op_setting_2",
        "op_setting_3",
        "sensor_1",
        "sensor_2",
        "sensor_3",
    ]


def test_parse_uploaded_frame_rejects_missing_model_columns(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from factorypulse.dashboard.data import parse_uploaded_frame

    csv_file = tmp_path / "upload.csv"
    pd.DataFrame(
        {
            "unit_id": [1, 1],
            "cycle": [1, 2],
            "op_setting_1": [0.1, 0.1],
            "op_setting_2": [0.2, 0.2],
            "op_setting_3": [0.3, 0.3],
            "sensor_1": [10.0, 10.5],
            "sensor_2": [5.0, 5.5],
        }
    ).to_csv(csv_file, index=False)

    monkeypatch.setattr(
        "factorypulse.dashboard.data.required_model_input_columns",
        lambda: [
            "unit_id",
            "cycle",
            "op_setting_1",
            "op_setting_2",
            "op_setting_3",
            "sensor_1",
            "sensor_2",
            "sensor_3",
        ],
    )
    monkeypatch.setattr("factorypulse.dashboard.data.required_window_size", lambda default=15: 2)

    with pytest.raises(ValueError, match="CMAPSS-compatible schema"):
        parse_uploaded_frame(csv_file)


def test_parse_uploaded_frame_rejects_short_files_for_model_window(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from factorypulse.dashboard.data import parse_uploaded_frame

    csv_file = tmp_path / "upload.csv"
    pd.DataFrame(
        {
            "unit_id": [1, 1],
            "cycle": [1, 2],
            "op_setting_1": [0.1, 0.1],
            "op_setting_2": [0.2, 0.2],
            "op_setting_3": [0.3, 0.3],
            "sensor_1": [10.0, 10.5],
            "sensor_2": [5.0, 5.5],
            "sensor_3": [7.0, 7.2],
        }
    ).to_csv(csv_file, index=False)

    monkeypatch.setattr(
        "factorypulse.dashboard.data.required_model_input_columns",
        lambda: [
            "unit_id",
            "cycle",
            "op_setting_1",
            "op_setting_2",
            "op_setting_3",
            "sensor_1",
            "sensor_2",
            "sensor_3",
        ],
    )
    monkeypatch.setattr("factorypulse.dashboard.data.required_window_size", lambda default=15: 3)

    with pytest.raises(ValueError, match="at least 3 rows"):
        parse_uploaded_frame(csv_file)
