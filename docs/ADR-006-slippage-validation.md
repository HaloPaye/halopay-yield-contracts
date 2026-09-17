# ADR-006: Slippage Validation

## Context
Sweeping idle liquidity into Soroban pools can cause slippage.

## Decision
Implement a constant-product invariant check (x * y = k) before dispatch.

## Consequences
Prevents sweeps if slippage exceeds 1.5%.
