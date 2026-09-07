# Admin Dashboard API Specification

## Overview
The **HaloPay Yield Administration API** provides a secure, role-gated control plane for monitoring and orchestrating Soroban treasury smart contracts, yield harvesting bots, and liquidity pools.

---

## Role-Based Access Control (RBAC)

All endpoints require cryptographic authentication via Ed25519 payload signatures and SEP-10 JWT bearer tokens.

| Role | Permissions | Access Scope |
| :--- | :--- | :--- |
| **Observer** | Read-only access to pool health, TVL, and yield metrics | Public/Auditor |
| **Operator** | Ability to trigger rebalances and update pool weights within defined limits | Maintainer Bots |
| **Guardian** | Emergency powers: trip circuit breaker, update timelock strategies | Multi-Sig Signers |

---

## API Endpoints

### 1. Vault Health Status
`GET /api/v1/admin/vault/health`

Returns composite solvency, active collateral breakdown, and oracle freshness.

#### Response:
```json
{
  "status": "healthy",
  "vault_address": "CBRW4F2K5M6N...",
  "tvl_usdc": "142500.50",
  "collateral_ratio": 1.042,
  "circuit_breaker_active": false,
  "last_rebalance_ledger": 52918230
}
```

---

### 2. Trigger Strategy Rebalance
`POST /api/v1/admin/vault/rebalance`

Instructs the autonomous rebalancing bot to adjust allocations according to target portfolio weights.

#### Request Body:
```json
{
  "target_weights": {
    "XLM": 0.40,
    "USDC": 0.60
  },
  "max_slippage_bps": 50,
  "nonce": 1694793600
}
```

---

### 3. Emergency Circuit Breaker Control
`POST /api/v1/admin/vault/circuit-breaker`

Trips or restores the vault circuit breaker. Requires Guardian multi-signature authorization.

#### Request Body:
```json
{
  "action": "TRIP",
  "reason": "Oracle price divergence detected across SDEX orderbook",
  "signatures": [
    "sig_guardian_1_ed25519...",
    "sig_guardian_2_ed25519..."
  ]
}
```

---

### 4. Cryptographic Audit Log
`GET /api/v1/admin/audit-log`

Retrieves a chronologically ordered, SHA-256 hash-chained log of all administrative actions.
