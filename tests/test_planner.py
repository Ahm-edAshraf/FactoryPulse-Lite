from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def test_rank_machines_prioritizes_highest_risk_first() -> None:
    from factorypulse.schemas import MachinePrediction
    from factorypulse.services.planner import rank_machines

    predictions = [
        MachinePrediction(machine_id="A", predicted_rul=30, health_score=75, health_state="Watchlist", change_point=None, top_drivers=["sensor_1"], recommended_action="Plan soon"),
        MachinePrediction(machine_id="B", predicted_rul=8, health_score=20, health_state="Critical", change_point=12, top_drivers=["sensor_2"], recommended_action="Stop soon"),
        MachinePrediction(machine_id="C", predicted_rul=18, health_score=45, health_state="Impaired", change_point=10, top_drivers=["sensor_3"], recommended_action="Inspect now"),
    ]

    ranked = rank_machines(predictions)

    assert [item.machine_id for item in ranked] == ["B", "C", "A"]


def test_estimate_avoided_downtime_increases_with_failure_cost() -> None:
    from factorypulse.services.planner import estimate_avoided_downtime_value

    low = estimate_avoided_downtime_value(predicted_rul=10, failure_cost=500, maintenance_cost=150)
    high = estimate_avoided_downtime_value(predicted_rul=10, failure_cost=1500, maintenance_cost=150)

    assert high > low
