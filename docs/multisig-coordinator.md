# Multi-Sig Threshold Coordinator

## Overview
The `MultiSigCoordinator` module (`agent/src/domain/multisig_coordinator.py`) coordinates multi-signature proposal aggregation, threshold governance verification, and execution authorization for Soroban contracts.

## Edge-Case Protections
- **Duplicate Signer Deduplication:** Prevents malicious or misconfigured signers from submitting multiple signatures to artificially inflate their accumulated threshold weight.
- **Nonce-Based Replay Protection:** Consumes unique proposal nonces upon execution (`used_nonces`), permanently barring replay attacks.
- **Strict Timestamp Expiry:** Rejects signature attachments and quorum evaluations for proposals that have surpassed their `expiration_timestamp`.
- **Threshold Hierarchies:** Maps granular authorization tiers (`low`, `med`, `high`) corresponding to Stellar account threshold rules.

## Usage Example

```python
from src.domain.multisig_coordinator import MultiSigCoordinator, MultiSigProposal

coordinator = MultiSigCoordinator(low_threshold=1, med_threshold=2, high_threshold=3)
coordinator.register_signer("GA1...", weight=1)
coordinator.register_signer("GA2...", weight=1)

proposal = MultiSigProposal(
    proposal_id="prop_001",
    action="emergency_rebalance",
    payload={"target_pool": "pool_usdc_xlm"},
    nonce=101,
    expiration_timestamp=1780000000.0,
)

coordinator.add_signature(proposal, "GA1...", "sig_hex_1")
coordinator.add_signature(proposal, "GA2...", "sig_hex_2")

if coordinator.execute_proposal(proposal, required_level="med"):
    # Submit transaction to Soroban contract
    pass
```
