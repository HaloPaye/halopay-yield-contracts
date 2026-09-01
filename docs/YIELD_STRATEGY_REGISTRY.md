# Yield Strategy Registry & Adapter Architecture

## 1. Overview

The **Yield Strategy Registry** serves as the central control plane and safety framework for managing automated capital allocations across decentralized yield protocols within the HaloPay ecosystem on Stellar Soroban.

The system combines on-chain Soroban smart contracts (`YieldTreasuryContract`) enforcing hard security boundaries with off-chain autonomous evaluation agents orchestrating optimal yield discovery across Soroban liquidity pools and lending primitives.

```
+--------------------------------------------------------------------+
|                         HaloPay Admin                              |
+--------------------------------------------------------------------+
                                  |
                                  | Admin Auth (require_auth)
                                  v
+--------------------------------------------------------------------+
|                      Yield Strategy Registry                       |
|               (Allowlisted Strategies & Risk Limits)                |
+--------------------------------------------------------------------+
                                  ^
                                  | Agent Auth (allocate)
+------------------------+        |
|  Yield Decision Agent  |--------+
|  (Off-Chain Optimizer) |
+------------------------+
                                  | Cross-Contract Invocation
                                  v
+--------------------------------------------------------------------+
|                    Soroban Yield Protocol Adapters                  |
|     +------------------+  +------------------+  +----------------+  |
|     |  AMM Pool Adap.  |  |  Lending Adapter |  | Vault Adapter  |  |
|     +------------------+  +------------------+  +----------------+  |
+--------------------------------------------------------------------+
```

---

## 2. Strategy Registration Lifecycle

Yield destinations (protocols, liquidity pools, or external vault adapters) must be explicitly registered and authorized before any capital can be routed to them.

### 2.1 Governance and Registration
Only the designated contract administrator (`Admin`) can register destinations into the persistent allowlist:

1. **Admin Authorization**: The caller must sign the transaction matching the address stored under `DataKey::Admin`.
2. **Allowlist Inclusion**: Calling `add_allowlist(env, destination_address)` sets `DataKey::Allowlist(destination_address)` to `true` in persistent storage.
3. **Immutability & Safety**: Non-allowlisted addresses are rejected at the smart contract level with `TreasuryError::DestinationNotAllowed`.

### 2.2 Registration Interface
```rust
pub fn add_allowlist(env: Env, target: Address) -> Result<(), TreasuryError> {
    auth::add_allowlist(&env, target)
}
```

---

## 3. Soroban Yield Adapter Patterns

Yield adapters abstract the interaction mechanics of underlying yield venues (e.g., AMMs, lending markets, liquid staking) into a standardized interface for treasury execution.

### 3.1 Standard Adapter Interface Specification
Each adapter contract implements a standard yield lifecycle trait:

```rust
pub trait YieldAdapterTrait {
    /// Deposits specified amount of assets into the underlying protocol
    fn deposit(env: Env, from: Address, amount: u128) -> Result<u128, AdapterError>;

    /// Redeems / withdraws principal and accrued yield back to the treasury
    fn withdraw(env: Env, to: Address, amount: u128) -> Result<u128, AdapterError>;

    /// Returns the net value (principal + yield) held by this contract
    fn get_balance(env: Env, account: Address) -> u128;

    /// Returns current annualized yield estimate (basis points)
    fn get_estimated_apy(env: Env) -> u32;
}
```

### 3.2 Cross-Contract Invocation Pattern
When the treasury contract executes an allocation:
1. Verifies that the destination address exists in the allowlist.
2. Invokes the destination contract adapter via Soroban's cross-contract call mechanism:
```rust
// Client invocation pattern for registered adapters
let client = YieldAdapterClient::new(&env, &destination);
client.deposit(&env.current_contract_address(), &amount);
```

---

## 4. Safety Boundaries & Risk Limits

To guarantee solvency and protect user deposits against smart contract risks, extreme market volatility, or malicious behavior, strict mathematical boundaries are enforced on-chain.

| Safety Parameter | Value / Formula | Error Variant | Description |
| :--- | :--- | :--- | :--- |
| **Transaction Cap** | `1,000` units | `ExceedsTransactionCap` | Hard maximum amount allowed in a single allocation transaction. |
| **Global Allocation Cap** | `80%` of Total Deposits (`(total_deposits * 8) / 10`) | `ExceedsGlobalCap` | Maximum proportion of total treasury deposits that can be allocated across all strategies. |
| **Minimum Liquidity Floor** | `100` units | `BreachesMinimumFloor` | Unallocated reserve balance required to remain in treasury for immediate withdrawals. |
| **Balance Availability** | `remaining >= amount` | `InsufficientBalance` | Ensures unallocated treasury balance can cover the requested allocation. |
| **Destination Whitelist** | `storage::is_allowed(&env, &destination)` | `DestinationNotAllowed` | Prevents routing funds to unverified or unauthorized contracts. |
| **Agent Authorization** | `agent.require_auth()` | `NotAuthorized` | Verifies cryptographic signature of designated off-chain agent. |

### 4.1 On-Chain Allocation Verification Flow
```rust
pub fn allocate(env: Env, destination: Address, amount: u128) -> Result<(), TreasuryError> {
    let agent = storage::get_agent(&env).ok_or(TreasuryError::NotAuthorized)?;
    agent.require_auth();

    if !storage::is_allowed(&env, &destination) {
        return Err(TreasuryError::DestinationNotAllowed);
    }
    if amount > 1000 {
        return Err(TreasuryError::ExceedsTransactionCap);
    }

    let total_deposits = storage::get_total_deposits(&env);
    let total_allocated = storage::get_total_allocated(&env);

    if total_allocated + amount > (total_deposits * 8) / 10 {
        return Err(TreasuryError::ExceedsGlobalCap);
    }

    let remaining = total_deposits - total_allocated;
    if remaining < amount {
        return Err(TreasuryError::InsufficientBalance);
    }

    if remaining - amount < 100 {
        return Err(TreasuryError::BreachesMinimumFloor);
    }

    storage::set_total_allocated(&env, total_allocated + amount);
    events::emit_funds_allocated(&env, agent, destination, amount);
    Ok(())
}
```

---

## 5. Off-Chain Strategy Evaluation & Scoring

The autonomous yield agent evaluates candidate liquidity pools and yield strategies using strict heuristics before preparing an on-chain allocation transaction.

### 5.1 Pool Evaluation Filters
1. **Asset Whitelist**: Discards pools containing unverified tokens; only native XLM and approved stablecoins (e.g. `USDC`) are considered.
2. **Liquidity Floor**: Candidate pool total liquidity must meet or exceed minimum depth thresholds (e.g., >= 10,000).
3. **Spread Threshold**: Maximum bid-ask spread or pool skewness must not exceed 2% (0.02). Pools exceeding this are rejected with `THIN_MARKET`.
4. **Minimum Score Threshold**: Allocation is only triggered if the pool score meets the minimum score threshold (e.g., >= 1.5).

---

## 6. Telemetry & Observability

The architecture enforces end-to-end observability across on-chain contract events and off-chain agent telemetry.

### 6.1 On-Chain Soroban Events
The contract emits structured events for all state transitions:

- **Funds Allocated**:
  - Topic: `Symbol("allocate")`
  - Data: `(agent: Address, destination: Address, amount: u128)`
- **Funds Withdrawn**:
  - Topic: `Symbol("withdraw")`
  - Data: `(admin: Address, amount: u128)`

### 6.2 Agent Structured Logging Schema
All agent actions are logged with standardized JSON structure:
```json
{
  "timestamp": "2026-09-01T09:20:00Z",
  "level": "INFO",
  "mode": "live",
  "event": "DECISION_RECORDED",
  "pool_id": "CA3D5KRYC6CB7OWQ6TWYRR3Z4T7GCZXY59GZ",
  "score": 2.45,
  "decision": "ALLOCATE"
}
```

### Key Telemetry Events
- `STARTUP`: Emitted on agent daemon initialization.
- `POOL_DISQUALIFIED`: Emitted when a candidate strategy fails risk or liquidity filters.
- `DECISION_RECORDED`: Emitted when a strategy passes all criteria and initiates execution.
- `SIMULATION_END`: Emitted in simulation mode upon reaching decision state without dispatching live transactions.
- `LOOP_OVERRUN`: Emitted when evaluation cycle duration exceeds interval window.