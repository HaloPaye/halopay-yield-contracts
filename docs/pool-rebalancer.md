# Liquidity Pool Rebalancer

## Overview
The `PoolRebalancer` module (`agent/src/domain/pool_rebalancer.py`) handles programmatic portfolio drift monitoring and generates balancing actions across multi-asset Stellar/Soroban liquidity pools.

## Features
- **Drift Detection & Dead Zone Tolerance:**
  Ignores minor fluctuations within `dead_zone_pct` (default: 2%) to minimize unnecessary transaction fees and slippage on Stellar.
- **Unallocated Asset Liquidation:**
  Correctly identifies assets currently held in the portfolio that are absent from the `target_weights` mapping and schedules them for liquidation down to zero.
- **New Asset Allocation:**
  Identifies target assets currently unheld (0 balance) and schedules appropriate buy/deposit orders.
- **Auto Weight Normalization:**
  Normalizes target weights if specified as raw ratios or non-unitary sums.
- **Negative Balance & Weight Guards:**
  Rejects invalid negative balance inputs and negative target weight configurations.
- **Precision & Dust Filtering:**
  Applies 7-decimal Soroban precision rounding (`0.0000001`) and filters out actions smaller than `min_trade_size`.

## Usage Example

```python
from decimal import Decimal
from src.domain.pool_rebalancer import PoolRebalancer

rebalancer = PoolRebalancer(dead_zone_pct=Decimal("0.02"))

current_balances = {
    "USDC": Decimal("700"),
    "XLM": Decimal("300"),
}

target_weights = {
    "USDC": Decimal("0.50"),
    "XLM": Decimal("0.50"),
}

actions = rebalancer.compute_rebalance_actions(current_balances, target_weights)
# actions == [("USDC", Decimal("-200.0000000")), ("XLM", Decimal("200.0000000"))]
```

## Test Coverage
Verified by `agent/tests/test_pool_rebalancer.py`:
- Empty / zero inputs handling.
- Negative balances and weights validation.
- Dead-zone suppression.
- Unallocated asset liquidation.
- New target asset inclusion.
- Target weight normalization.
