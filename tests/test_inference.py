from pathlib import Path
import sys

import joblib
import pandas as pd
from sklearn.dummy import DummyRegressor


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def _machine_frame() -> pd.DataFrame:
    rows = []
    for cycle in range(1, 7):
        rows.append(
            {
                "unit_id": 1,
                "cycle": cycle,
                "op_setting_1": 0.1,
                "op_setting_2": 0.2,
                "op_setting_3": 0.3,
                "sensor_1": 100 - cycle,
                "sensor_2": 50 + cycle,
                "sensor_3": 10 + cycle,
            }
        )
    return pd.DataFrame(rows)


def test_predict_machine_state_returns_expected_schema(tmp_path: Path) -> None:
    from factorypulse.features.build_features import build_training_features
    from factorypulse.models.infer import predict_machine_state

    training_frame = _machine_frame()
    training_features, feature_columns = build_training_features(training_frame, window_size=3, rul_cap=5)

    model = DummyRegressor(strategy="constant", constant=12)
    model.fit(training_features[feature_columns], training_features["rul_target"])

    artifact_dir = tmp_path / "models"
    artifact_dir.mkdir()
    joblib.dump(model, artifact_dir / "rul_xgb.joblib")
    (artifact_dir / "feature_columns.json").write_text(__import__("json").dumps(feature_columns), encoding="utf-8")
    (artifact_dir / "metrics.json").write_text("{}", encoding="utf-8")

    result = predict_machine_state(training_frame, model_dir=artifact_dir, window_size=3)

    assert result.machine_id == "1"
    assert result.predicted_rul == 12.0
    assert result.health_state in {"Healthy", "Watchlist", "Impaired", "Critical"}
    assert isinstance(result.top_drivers, list)
    assert result.recommended_action


def test_predict_machine_state_rejects_short_trajectories(tmp_path: Path) -> None:
    from factorypulse.features.build_features import build_training_features
    from factorypulse.models.infer import predict_machine_state

    training_frame = _machine_frame()
    training_features, feature_columns = build_training_features(training_frame, window_size=3, rul_cap=5)

    model = DummyRegressor(strategy="constant", constant=12)
    model.fit(training_features[feature_columns], training_features["rul_target"])

    artifact_dir = tmp_path / "models"
    artifact_dir.mkdir()
    joblib.dump(model, artifact_dir / "rul_xgb.joblib")
    (artifact_dir / "feature_columns.json").write_text(__import__("json").dumps(feature_columns), encoding="utf-8")
    (artifact_dir / "metrics.json").write_text("{}", encoding="utf-8")

    short_frame = _machine_frame().head(2)

    with __import__("pytest").raises(ValueError, match="at least"):
        predict_machine_state(short_frame, model_dir=artifact_dir, window_size=3)


def test_predict_machine_state_rejects_missing_feature_columns(tmp_path: Path) -> None:
    from factorypulse.features.build_features import build_training_features
    from factorypulse.models.infer import predict_machine_state

    training_frame = _machine_frame()
    training_features, feature_columns = build_training_features(training_frame, window_size=3, rul_cap=5)

    model = DummyRegressor(strategy="constant", constant=12)
    model.fit(training_features[feature_columns], training_features["rul_target"])

    artifact_dir = tmp_path / "models"
    artifact_dir.mkdir()
    joblib.dump(model, artifact_dir / "rul_xgb.joblib")
    (artifact_dir / "feature_columns.json").write_text(__import__("json").dumps(feature_columns), encoding="utf-8")
    (artifact_dir / "metrics.json").write_text("{}", encoding="utf-8")

    malformed = _machine_frame().drop(columns=["sensor_3"])

    with __import__("pytest").raises(ValueError, match="missing input columns"):
        predict_machine_state(malformed, model_dir=artifact_dir, window_size=3)


def test_predict_machine_state_rejects_missing_identifier_columns(tmp_path: Path) -> None:
    from factorypulse.features.build_features import build_training_features
    from factorypulse.models.infer import predict_machine_state

    training_frame = _machine_frame()
    training_features, feature_columns = build_training_features(training_frame, window_size=3, rul_cap=5)

    model = DummyRegressor(strategy="constant", constant=12)
    model.fit(training_features[feature_columns], training_features["rul_target"])

    artifact_dir = tmp_path / "models"
    artifact_dir.mkdir()
    joblib.dump(model, artifact_dir / "rul_xgb.joblib")
    (artifact_dir / "feature_columns.json").write_text(__import__("json").dumps(feature_columns), encoding="utf-8")
    (artifact_dir / "metrics.json").write_text("{}", encoding="utf-8")

    malformed = _machine_frame().drop(columns=["cycle"])

    with __import__("pytest").raises(ValueError, match="missing input columns"):
        predict_machine_state(malformed, model_dir=artifact_dir, window_size=3)
