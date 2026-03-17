# Deployment Playbook

## Phase 1: Pilot

- Select one line with 3-5 high-impact assets.
- Ingest historical or daily-exported sensor CSVs.
- Validate RUL quality, maintenance timing, and cost assumptions with the site team.

## Phase 2: Stabilize

- Add low-cost vibration and temperature logging where gaps exist.
- Define failure-cost and maintenance-cost assumptions per asset class.
- Lock alert handling rules for Critical, Impaired, Watchlist, and Healthy states.

## Phase 3: Scale

- Roll out to more assets only after one quarter of measured savings.
- Group machines by asset family and retrain adapters when sensor signatures differ materially.
- Track drift and recalibration centrally so the deployment stays lightweight for each SME site.

## Success metrics

- Reduced unplanned downtime hours.
- Reduced emergency maintenance orders.
- Higher percentage of maintenance completed in planned windows.
- Lower cost per prevented failure compared with current practice.

## Governance

- Keep raw customer data in-site or in a tenant-specific storage boundary.
- Version models and benchmark artifacts together.
- Require human approval before work orders are triggered automatically.
