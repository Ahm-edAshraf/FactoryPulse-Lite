"""Shared copy and labels for the FactoryPulse dashboard."""

from __future__ import annotations

APP_TITLE = "FactoryPulse Lite"
APP_SUBTITLE = "Predict machine failure before it freezes production — explainable RUL countdowns for ASEAN SME operators."

HEALTH_STATE_COPY = {
    "Healthy": "Operating normally. Routine checks only.",
    "Watchlist": "Early wear detected. Plan a maintenance window.",
    "Impaired": "Degrading. Inspect before next peak shift.",
    "Critical": "High failure risk. Intervene immediately.",
}

PITCH_POINTS = [
    "Predict failures before they halt production.",
    "Translate sensor data into plain maintenance actions.",
    "Help SMEs act early without enterprise spend.",
]
