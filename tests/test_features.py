from pathlib import Path
import sys

import pandas as pd


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def _sample_sensor_frame() -> pd.DataFrame:
    rows = []
    for unit_id in (1, 2):
        for cycle in range(1, 7):
            rows.append(
                {
                    "unit_id": unit_id,
                    "cycle": cycle,
                    "op_setting_1": 0.1 * unit_id,
                    "op_setting_2": 0.2,
                    "op_setting_3": 0.3,
                    "sensor_1": 100 - cycle - unit_id,
                    "sensor_2": 50 + cycle,
                    "sensor_3": 10 * unit_id + cycle,
                }
            )
    return pd.DataFrame(rows)


def test_build_training_features_returns_deterministic_columns() -> None:
    from factorypulse.features.build_features import build_training_features

    frame = _sample_sensor_frame()

    features_a, columns_a = build_training_features(frame, window_size=3, rul_cap=4)
    features_b, columns_b = build_training_features(frame, window_size=3, rul_cap=4)

    assert columns_a == columns_b
    assert list(features_a.columns) == list(features_b.columns)


def test_build_training_features_respects_window_size() -> None:
    from factorypulse.features.build_features import build_training_features

    frame = _sample_sensor_frame()

    features, _ = build_training_features(frame, window_size=3, rul_cap=4)

    assert set(features["cycle"]) == {3, 4, 5, 6}


def test_build_training_features_caps_rul_target() -> None:
    from factorypulse.features.build_features import build_training_features

    frame = _sample_sensor_frame()

    features, _ = build_training_features(frame, window_size=3, rul_cap=2)

    assert features["rul_target"].max() == 2


def test_build_inference_features_matches_training_column_order() -> None:
    from factorypulse.features.build_features import (
        build_inference_features,
        build_training_features,
    )

    frame = _sample_sensor_frame()
    training_features, feature_columns = build_training_features(frame, window_size=3, rul_cap=4)
    inference_features = build_inference_features(frame, window_size=3, feature_columns=feature_columns)

    assert list(inference_features.columns) == feature_columns
    assert set(feature_columns).issubset(training_features.columns)
