from pathlib import Path
import sys

import pandas as pd


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def _trajectory() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "unit_id": [1] * 8,
            "cycle": list(range(1, 9)),
            "sensor_1": [10.0, 10.1, 10.2, 10.4, 11.0, 12.0, 13.0, 14.5],
            "sensor_2": [20.0, 20.0, 20.1, 20.2, 20.8, 21.5, 22.2, 23.0],
            "sensor_3": [30.0, 30.0, 30.1, 30.1, 30.4, 31.0, 32.0, 33.0],
        }
    )


def test_health_score_is_between_zero_and_hundred() -> None:
    from factorypulse.models.health import compute_health_score

    score = compute_health_score(_trajectory())

    assert 0.0 <= score <= 100.0


def test_health_score_drops_with_stronger_degradation() -> None:
    from factorypulse.models.health import compute_health_score

    mild = _trajectory().copy()
    severe = _trajectory().copy()
    severe["sensor_1"] = severe["sensor_1"] * 1.5

    assert compute_health_score(severe) < compute_health_score(mild)


def test_detect_change_point_returns_valid_cycle_or_none() -> None:
    from factorypulse.models.health import detect_change_point

    change_point = detect_change_point(_trajectory())

    assert change_point is None or change_point in set(_trajectory()["cycle"])


def test_map_health_state_is_deterministic() -> None:
    from factorypulse.models.health import map_health_state

    assert map_health_state(85) == "Healthy"
    assert map_health_state(60) == "Watchlist"
    assert map_health_state(35) == "Impaired"
    assert map_health_state(10) == "Critical"


def test_blend_health_score_penalizes_low_remaining_life() -> None:
    from factorypulse.models.health import blend_health_score

    high_rul = blend_health_score(sensor_health_score=92, predicted_rul=110)
    low_rul = blend_health_score(sensor_health_score=92, predicted_rul=18)

    assert low_rul < high_rul
