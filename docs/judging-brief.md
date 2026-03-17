# FactoryPulse Lite Judging Brief

## Target customer

FactoryPulse Lite is designed for ASEAN small and medium manufacturers that run a small number of critical rotating assets and cannot afford full smart-factory retrofits. The most practical beachhead is food processing and light manufacturing plants with 5-20 motors, pumps, or compressors.

## Why they buy

- Reactive maintenance creates multi-day production stoppages.
- Preventive replacement wastes parts, labor, and shutdown windows.
- Existing enterprise predictive-maintenance stacks are too expensive and operationally heavy for SMEs.

FactoryPulse Lite gives those operators a lower-friction path: start with CSV uploads, prove value on one line, then expand to sensor gateways and routine scoring.

## Evidence package

- Official NASA CMAPSS FD001 benchmark reporting is generated into `models/evaluation_report.json`.
- Baseline comparisons show whether the deployed model meaningfully beats simpler regressors.
- Robustness tests simulate missing data, noisy sensors, and channel dropout to reflect real industrial conditions.
- The dashboard exposes remaining life, health state, top degradation drivers, protected value, and maintenance urgency.

## Commercial model

- Pilot: fixed-fee deployment for a single line and 3-5 critical assets.
- Expansion: per-asset subscription with optional retraining and reporting support.
- Services: add-on for sensor onboarding, threshold tuning, and maintenance workflow integration.

## Sustainability plan

- Reduce emergency breakdown waste by catching degradation earlier.
- Extend useful part life by avoiding premature replacement.
- Minimize retraining waste through scheduled quarterly review instead of constant model churn.
- Track deployment KPIs: avoided downtime, false alarms, maintenance lead time, and protected production value.

## Operating model

- Daily: score new trajectories and flag at-risk machines.
- Weekly: maintenance planner review with operations lead.
- Monthly: inspect input quality and sensor health.
- Quarterly: review thresholds, retrain if drift is material, and refresh benchmark results.
