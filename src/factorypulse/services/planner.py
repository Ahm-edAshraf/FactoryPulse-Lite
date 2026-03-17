"""Maintenance prioritization and ROI helpers."""

from __future__ import annotations

from factorypulse.schemas import MachinePrediction


def rank_machines(predictions: list[MachinePrediction]) -> list[MachinePrediction]:
    return sorted(predictions, key=lambda item: (item.health_score, item.predicted_rul, item.machine_id))


def estimate_avoided_downtime_value(predicted_rul: float, failure_cost: float, maintenance_cost: float) -> float:
    urgency_factor = 1 + max(0.0, 25 - predicted_rul) / 25
    return max(0.0, failure_cost * urgency_factor - maintenance_cost)
