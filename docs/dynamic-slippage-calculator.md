# Dynamic Slippage Calculator

## Overview
The `DynamicSlippageCalculator` module (`agent/src/domain/slippage.py`) calculates expected price impact and dynamic slippage bounds across Soroban AMM liquidity pools and decentralized exchanges (SDEX).

## Features
- **Proportional Impact Calculation:** Models price impact dynamically based on trade size relative to current pool liquidity:
  $$\text{Impact} = \left(\frac{\text{trade\_amount}}{\text{pool\_liquidity}}\right) \times \text{volatility\_multiplier}$$
- **Safety Bounds Enforcement:** Clamps evaluated slippage between configurable `min_slippage` and `max_slippage` parameters.
- **Strict Input Validation:** Gracefully defaults to safety caps (`max_slippage`) if given non-positive amounts, zero pool reserves, or non-positive volatility multipliers.
- **Slippage Evaluation:** `is_slippage_acceptable` validates whether executed swap prices deviate beyond user tolerance thresholds.
- **Backward Compatibility:** Retains the legacy `calculate_slippage(volume: float) -> float` interface.

## Usage Example

```python
from decimal import Decimal
from src.domain.slippage import DynamicSlippageCalculator

calculator = DynamicSlippageCalculator(
    min_slippage=Decimal("0.005"),  # 0.5%
    max_slippage=Decimal("0.05"),   # 5.0%
)

# Compute slippage for a 500 USDC swap on a 50,000 USDC pool with standard volatility
slippage = calculator.compute_slippage(
    trade_amount=Decimal("500"),
    pool_liquidity=Decimal("50000"),
    volatility_multiplier=Decimal("1.0"),
)
assert slippage == Decimal("0.01")  # 1.0%

# Verify executed price against 1.5% maximum allowable slippage
is_valid = calculator.is_slippage_acceptable(
    expected_price=Decimal("1.00"),
    executed_price=Decimal("0.99"),
    allowed_slippage=Decimal("0.015"),
)
assert is_valid is True
```

## Test Coverage
Comprehensive unit test cases are provided in `agent/tests/test_dynamic_slippage.py`, asserting:
- Legacy helper backwards compatibility.
- Bounds configuration & error handling on invalid intervals.
- Normal, min-clamped, max-clamped, and volatility-scaled calculations.
- Zero/negative parameter fallbacks.
- Exact boundary price verification.
