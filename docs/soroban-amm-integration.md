# Soroban Contract AMM Integration

## Overview
The `AmmCalculator` module (`agent/src/domain/amm_calculator.py`) models constant product ($x \times y = k$) Automated Market Maker liquidity pools and Soroswap contracts on Stellar Protocol 28.

## Edge-Case Protections & Features
- **Symmetric Swap Calculations:** Implements exact output derivation (`get_amount_in`), preventing pool reserve exhaustion when users or rebalancers request exact token disbursements.
- **Liquidity Minting & Minimum Share Locking:** Follows Soroban / Uniswap standard of locking the first 1,000 dead shares upon initial deposit ($\sqrt{A \times B} - 1000$) to protect subsequent liquidity providers from inflation attacks.
- **Proportional Liquidity Redemption:** Exact calculation of withdrawn reserves (`calculate_lp_burn`) with 7-decimal Soroban precision rounding (`0.0000001`).
- **Defensive Division by Zero:** Validates fee fractions within $[0.0, 1.0)$ and guards against zero or negative reserve parameters.

## Usage Example

```python
from decimal import Decimal
from src.domain.amm_calculator import AmmCalculator

calc = AmmCalculator(fee_fraction=Decimal("0.003"))

# Calculate swap output
amount_out = calc.get_amount_out(
    amount_in=Decimal("100"),
    reserve_in=Decimal("10000"),
    reserve_out=Decimal("20000"),
)

# Calculate required input for exact output
amount_in = calc.get_amount_in(
    amount_out=Decimal("500"),
    reserve_in=Decimal("10000"),
    reserve_out=Decimal("20000"),
)
```
