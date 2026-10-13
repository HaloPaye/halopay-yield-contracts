# Gas & Fee Estimation Engine

## Overview
The `FeeEstimator` module (`agent/src/domain/fee_estimator.py`) is responsible for tracking network fees and dynamically computing gas parameters for Soroban and Stellar transaction submissions.

## Security Hardening
- **Anti-Spike Clamping:** Limits sudden fee surges up to a maximum multiplier (`max_surge_ratio`) relative to current EMA, defending against fee drain and flash-manipulation attacks.
- **Strict Fee Boundaries:** Hard caps fees between configurable `min_fee` (default: 100 stroops) and `max_fee` (default: 50,000 stroops).
- **Priority Scaling:** Supports granular execution urgency (`LOW`, `NORMAL`, `HIGH`, `CRITICAL`) with multipliers to guarantee transaction inclusion during volatile market windows without unbounded fee commitment.
- **Anomaly Detection:** Sets `spike_detected` flag upon detecting anomalous fee spikes for telemetry and alerting.
- **Defensive Input Validation:** Rejects negative fees, out-of-range alpha smoothing parameters, and invalid bounds.

## Usage Example

```python
from src.domain.fee_estimator import FeeEstimator, PriorityLevel

estimator = FeeEstimator(
    alpha=0.2,
    base_fee=100,
    min_fee=100,
    max_fee=50_000,
    max_surge_ratio=3.0,
)

# Ingest observed network fee
estimator.update_fee(250)

# Retrieve recommended fee by priority
fee = estimator.get_recommended_fee(priority=PriorityLevel.HIGH)
```
