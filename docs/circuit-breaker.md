# Emergency Withdrawal Circuit Breaker

## Overview
The `EmergencyCircuitBreaker` module (`agent/src/domain/circuit_breaker.py`) provides sub-millisecond, O(1) stateful execution guards for automated Soroban yield contracts and agent pipelines.

## Architecture & Performance
- **Zero I/O Critical Path:** State evaluations (`is_operational()`) execute purely in-memory with zero disk or network bottlenecks.
- **Three-State Machine:**
  - `CLOSED`: Normal operation; transactions proceed unimpeded.
  - `OPEN`: Tripped state; initiates emergency capital preservation protocols and disables non-emergency contract invocations.
  - `HALF_OPEN`: Probationary recovery period following expiration of `recovery_timeout_seconds`.
- **Probationary Failure Protection:** A single operational failure while in `HALF_OPEN` immediately trips the circuit back to `OPEN`.
- **Manual Emergency Override:** Direct programmatic switch to trip or reset system state during emergency maintenance.
- **Telemetry Observability:** Emits structured metrics reporting state transitions and failure counts.

## Usage Example

```python
from src.domain.circuit_breaker import EmergencyCircuitBreaker

breaker = EmergencyCircuitBreaker(
    failure_threshold=3,
    recovery_timeout_seconds=30.0,
    half_open_success_threshold=2,
)

if not breaker.is_operational():
    # Trigger emergency fallback or withdraw funds
    trigger_emergency_withdrawal()
else:
    try:
        execute_vault_rebalance()
        breaker.record_success()
    except Exception:
        breaker.record_failure()
```
