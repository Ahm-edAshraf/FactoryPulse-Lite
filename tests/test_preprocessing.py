from pathlib import Path
import sys

import pandas as pd
import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


CMAPSS_COLUMNS = [
    "unit_id",
    "cycle",
    "op_setting_1",
    "op_setting_2",
    "op_setting_3",
    *[f"sensor_{index}" for index in range(1, 22)],
]


def _write_cmapss_like_file(path: Path) -> None:
    rows = [
        "1 1 0.1 0.2 0.3 " + " ".join(str(value) for value in range(1, 22)),
        "1 2 0.2 0.3 0.4 " + " ".join(str(value + 1) for value in range(1, 22)),
    ]
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def test_load_cmapss_split_returns_expected_columns(tmp_path: Path) -> None:
    from factorypulse.data.loaders import load_cmapss_split

    sample_file = tmp_path / "train_FD001.txt"
    _write_cmapss_like_file(sample_file)

    frame = load_cmapss_split(sample_file)

    assert list(frame.columns) == CMAPSS_COLUMNS
    assert frame.shape == (2, len(CMAPSS_COLUMNS))


def test_prepare_sensor_frame_fills_missing_values() -> None:
    from factorypulse.data.preprocessing import prepare_sensor_frame

    frame = pd.DataFrame(
        {
            "unit_id": [1, 1, 1],
            "cycle": [1, 2, 3],
            "op_setting_1": [0.1, None, 0.3],
            "op_setting_2": [0.2, 0.2, 0.2],
            "op_setting_3": [0.3, 0.3, None],
            "sensor_1": [10.0, None, 12.0],
            "sensor_2": [5.0, 5.5, None],
        }
    )

    prepared = prepare_sensor_frame(frame)

    assert prepared.isna().sum().sum() == 0
    assert prepared.loc[1, "sensor_1"] == 10.0
    assert prepared.loc[2, "sensor_2"] == 5.5


def test_validate_sensor_frame_rejects_missing_required_columns() -> None:
    from factorypulse.schemas import validate_sensor_frame

    malformed = pd.DataFrame({"unit_id": [1], "sensor_1": [1.0]})

    with pytest.raises(ValueError, match="missing required columns"):
        validate_sensor_frame(malformed)


def test_parse_uploaded_frame_rejects_multiple_machine_ids(tmp_path: Path) -> None:
    from factorypulse.dashboard.data import parse_uploaded_frame

    csv_file = tmp_path / "upload.csv"
    pd.DataFrame(
        {
            "unit_id": [1, 1, 2, 2],
            "cycle": [1, 2, 1, 2],
            "op_setting_1": [0.1, 0.1, 0.2, 0.2],
            "op_setting_2": [0.2, 0.2, 0.2, 0.2],
            "op_setting_3": [0.3, 0.3, 0.3, 0.3],
            "sensor_1": [10, 11, 9, 8],
            "sensor_2": [5, 5.5, 6, 6.5],
        }
    ).to_csv(csv_file, index=False)

    with pytest.raises(ValueError, match="exactly one machine"):
        parse_uploaded_frame(csv_file)
