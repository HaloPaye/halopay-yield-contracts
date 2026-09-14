# Security Policy

HaloPay treats on-chain capital preservation, Soroban smart contract authorization, and autonomous agent safety as paramount priorities.

---

## Supported Versions

Only the latest commit on the `main` branch is actively supported and maintained with security updates.

| Component | Target Runtime | Supported |
| :-------- | :------------- | :-------- |
| `contracts/` | Soroban SDK | :white_check_mark: |
| `agent/`     | Python 3.11+   | :white_check_mark: |

---

## Vulnerability Reporting

If you discover a security vulnerability or exploit vector within our Soroban smart contracts or autonomous agent heuristics, **please DO NOT open a public GitHub issue or PR.**

Please disclose vulnerabilities responsibly:

* **Email:** [security@halopay.io](mailto:security@halopay.io)
* **Response SLA:** Our protocol team will acknowledge receipt of your disclosure within **24 hours**.
* **Remediation Window:** Critical vulnerabilities will be triaged and addressed within **48–72 hours**.

### Report Requirements
1. Clear description of the vulnerability (e.g., reentrancy, arithmetic overflow/underflow, share dilution, unauthorized cross-contract call).
2. Proof of Concept (PoC) code or Soroban CLI invocation steps replicating the issue.
3. Assessment of potential impact on merchant vault deposits.

---

## On-Chain Safety Limits & Architecture Guards

The HaloPay Yield Contract implements strict, defense-in-depth on-chain safeguards:

1. **Hard Allocation Cap:** A non-negotiable contract-level limit ensures that a maximum of 80% of total merchant deposits can be allocated to external yield strategies at any time. The remaining 20% remains in liquid reserve for merchant redemptions.
2. **Admin-Controlled Destination Allowlist:** Funds can ONLY be routed to external liquidity pools or AMMs explicitly registered in the contract's verified allowlist by governance multi-sig.
3. **Strict Authorization Boundaries:** 
   * `require_auth()` checks ensure the off-chain Agent cannot alter the allowlist or change contract ownership.
   * Admin accounts cannot directly trigger arbitrary fund transfers bypassing vault accounting.
4. **Timelock Execution:** Critical governance changes (such as adding new liquidity adapters or upgrading contract WASM bytecode) enforce a mandatory 24-hour timelock delay.
5. **Emergency Circuit Breaker:** Admin keys retain the capability to pause allocations instantly in the event of an anomalous market event or pool exploit on the Stellar network.

