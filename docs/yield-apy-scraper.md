# Yield APY Scraper & Aggregator

## Overview
The `ApyAggregator` module (`agent/src/domain/apy_aggregator.py`) computes rolling annualized percentage yields (APY) and statistical metrics across DeFi liquidity pools on Stellar and Soroban.

## Security Hardening
- **Flash-Loan Outlier Clamping:** Guards against sudden, artificial return spikes engineered by attackers via flash-loan manipulation. Daily returns exceeding `max_daily_return` (default: 10%) are automatically clamped, and `anomaly_detected` is flagged.
- **Extreme Loss Flooring:** Bounded against negative returns (`min_daily_return`) to prevent arithmetic distortion from black-swan pool drains.
- **Annualized Ceiling:** Hard cap of `max_allowed_apy` (default: 500% APY) prevents astronomical APY projections from disrupting autonomous treasury rebalancing models.
- **Input Sanitization:** Filters out non-numeric, `NaN`, and infinite return values before calculating portfolio statistics.
- **Compound Interest Support:** Supports both simple annualized APR and exponential compounding with overflow protection.

## Usage Example

```python
from decimal import Decimal
from src.domain.apy_aggregator import ApyAggregator

aggregator = ApyAggregator(lookback_periods=7)

daily_returns = [
    Decimal("0.0005"),
    Decimal("0.0006"),
    Decimal("0.0007"),
    Decimal("0.0004"),
]

# Simple rolling APY
apy = aggregator.calculate_rolling_apy(daily_returns)

# Compounded APY
compound_apy = aggregator.calculate_rolling_apy(daily_returns, compound=True)

# Compute statistical dispersion and anomaly flags
apy, stddev, is_anomaly = aggregator.compute_summary_stats(daily_returns)
```
