"""Turn model outputs into plain-language maintenance explanations."""

from __future__ import annotations

from factorypulse.schemas import MachinePrediction


def summarize_prediction(prediction: MachinePrediction, machine_name: str) -> str:
    driver_text = ", ".join(driver.replace("_", " ") for driver in prediction.top_drivers[:3]) or "sensor drift"
    return (
        f"{machine_name} is currently in a {prediction.health_state.lower()} state with roughly "
        f"{prediction.predicted_rul:.0f} cycles remaining. The strongest degradation signals are coming from "
        f"{driver_text}, so the recommended next step is: {prediction.recommended_action}"
    )
