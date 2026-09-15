# Emergency Withdrawal Circuit Breaker Specification

## Overview
The **Emergency Withdrawal Circuit Breaker** is a smart contract safety mechanism built into the HaloPay Soroban Treasury Vault. It provides fail-safe fund preservation when anomalous off-chain or on-chain conditions threaten liquidity pool solvency.

---

## Circuit Breaker Architecture

```
+-----------------------------------------------------------------------------------+
|                           SOROBAN TREASURY VAULT                                  |
|                                                                                   |
|   +-------------------+        Trip Condition        +------------------------+   |
|   |   Active State    | ---------------------------> |     Paused State       |   |
|   | (Deposits, Yield) |                              |  (Deposits Suspended)  |   |
|   +-------------------+                              +------------------------+   |
|                                                                   |               |
|                                                                   v               |
|                                                      +------------------------+   |
|                                                      |  Emergency Withdrawal  |   |
|                                                      | (Pro-Rata USDC Redeem) |   |
|                                                      +------------------------+   |
+-----------------------------------------------------------------------------------+
```

---

## Trigger Conditions

The circuit breaker trips into `Paused` status when any of the following parameters are breached:
1. **De-peg / Oracle Divergence:** If the price of liquidity pool collateral deviates by more than `5.0%` from the Horizon reference oracle within a 5-minute ledger window.
2. **Abnormal Outflow Spike:** If more than `25%` of total vault TVL is requested for redemption in a single ledger block, triggering rate-gated cool-off.
3. **Flash Loan Anomaly:** Detection of rapid multi-hop price manipulations identified by the Python autonomous surveillance agent (`FlashLoanDetector`).
4. **Manual Governance Trip:** Multi-signature transaction signed by at least 2 of 3 guardian keys.

---

## Invariant Guarantees During Paused State

* **Zero Deposit Allowance:** New deposits and rebalancing swaps are strictly rejected with error code `Error::VaultPaused`.
* **Pro-Rata Share Settlement:** Users may execute `emergency_withdraw(shares)` to redeem their exact proportional entitlement of underlying reserves directly, bypassing AMM routing.
* **No Strategy Lockups:** Capital locked in external Soroswap/Aqua liquidity pools is automatically recalled to the root treasury contract.

---

## Recovery & Resumption Runbook

1. **Root Cause Identification:** Security guardians review audit logs and verify oracle feed health.
2. **State Verification:** Confirm that reserve balances match total share allocations:
   $$\sum \text{UserBalances} \equiv \text{VaultReserve}$$
3. **Unpause Execution:** A 2-of-3 multi-sig invocation calls `unpause_vault()` after a mandatory 24-hour timelock review.
