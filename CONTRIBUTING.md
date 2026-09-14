# Contributing to HaloPay Yield Contracts & Agent

Thank you for your interest in contributing to the **HaloPay Yield Contracts & Agent** repository! This project combines on-chain Soroban Smart Contracts (Rust) that serve as a decentralized treasury for unbanked merchants, and an autonomous Python orchestrator that continuously analyzes liquidity pools on the Stellar network.

To maintain architectural integrity, contract safety, and smooth collaboration, please follow our contribution guidelines below.

---

## 🚀 How to Contribute

### 1. Select an Open Issue
* Browse issues labeled `status: ready-for-dev`, `good first issue`, or `help wanted`.
* Read through the issue's **Context**, **Technical Requirements**, and **Acceptance Criteria**.

### 2. Request Assignment Before Starting Work
* **Please do not begin coding or open unsolicited PRs without an assigned issue.** This prevents duplicated work across contributors.
* Comment on the issue explaining your implementation strategy. A maintainer will assign the issue to you.

### 3. Branching Strategy
* Create your feature branch off `main`:
  ```bash
  git checkout -b feat/issue-<issue_number>-<short-description>
  ```
  *Examples:*
  * `feat/issue-35-timelock-guard`
  * `fix/issue-41-horizon-retry-backoff`
  * `test/issue-49-pool-mock-fixtures`

### 4. Pull Request Standards
* **Title Format:** PR titles MUST follow the format:
  ```text
  [#<issue_number>] <Imperative description of change>
  ```
  *Example:* `[#35] Implement 24-hour timelock delay for strategy upgrades`
* **Issue Linking:** Explicitly link the issue in the PR description:
  ```text
  Closes #<issue_number>
  ```
* **Scope:** Keep PRs tightly focused on the assigned issue. Separate smart contract modifications from Python agent improvements where applicable.

---

## 🛠️ Local Development & Quality Gates

All pull requests trigger our continuous integration (CI) pipeline. Ensure all tests and linters pass before requesting review:

### 1. Smart Contract Verification (Rust / Soroban)
```bash
# Build Soroban WASM artifacts
make build-wasm

# Run Soroban contract unit and integration tests
make test-contracts
# or: cargo test --manifest-path contracts/Cargo.toml
```

### 2. Python Agent Verification (Python 3.11+)
```bash
# Run pytest test suite
make test-agent
# or: pytest agent/tests/

# Format, lint, and type-check
make lint
# or: black --check agent/ && flake8 agent/ && mypy agent/
```

### 3. Full Simulation Loop
```bash
make simulate
```

---

## 🏛️ Domain-Driven Design (DDD) Layout

To maintain enterprise modularity, adhere to the established domain boundaries:

### On-Chain Contracts (`/contracts`)
* `contracts/src/core/`: Core vault domain logic, balance math, and yield accounting.
* `contracts/src/interfaces/`: Interface and trait definitions for external AMMs and SDEX liquidity pools.
* `contracts/src/state/`: Soroban instance storage keys, data types, and state migration logic.
* `contracts/src/security/`: Destination allowlists, access control guards, and timelock mechanisms.

### Off-Chain Intelligence Agent (`/agent`)
* `agent/src/domain/`: Heuristic scoring models, risk evaluation engines, and yield algorithms.
* `agent/src/infrastructure/`: Horizon REST clients, Soroban RPC consumers, and external feeds.
* `agent/src/application/`: Decision loop, allocation execution manager, and event listeners.
* `agent/src/config/`: Environment variable validation and structured JSON logging.

---

## 📜 Code of Conduct & Licensing

* **Respect & Professionalism:** Treat all community members, reviewers, and maintainers with courtesy.
* **Licensing:** Contributions to this repository are licensed under the **Apache License, Version 2.0**. By submitting code, you agree to license your work under these terms.

