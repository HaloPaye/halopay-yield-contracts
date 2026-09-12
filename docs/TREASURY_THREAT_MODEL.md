# HaloPay Treasury Smart Contract Threat Model

## 1. Executive Summary
This document provides the risk analysis and threat matrix for the HaloPay on-chain Soroban Treasury Vault.

## 2. Attack Vectors & Mitigations

| Threat | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Share Inflation / Dilution** | Early depositor steals vault shares | Minimum initial shares minted to dead address and fixed-point math |
| **Reentrancy on Transfers** | Drain vault funds | Soroban reentrancy protection and checks-effects-interactions pattern |
| **Malicious Strategy Parameter Upgrade** | Steal or misallocate funds | 24-hour mandatory governance timelock delay |
| **Oracle Pricing Stale/Manipulated** | Incorrect share valuation | Staleness bounds check and circuit breaker triggering |
| **Guardian Key Compromise** | Unauthorized pause | Multi-signature guardian scheme required |

## 3. Incident Response
In case of detected anomaly:
1. Automated guardian calls `circuit_breaker::pause()`.
2. Admin inspection window begins.
3. Post-mortem published before `resume()`.
