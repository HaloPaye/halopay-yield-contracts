# HALOPAY YIELD CONTRACTS: BUILD INSTRUCTIONS

You are an expert AI coding agent. Your task is to build `halopay-yield-contracts`, a complete, production-ready, hybrid monorepo consisting of a Rust Soroban smart contract and a Python AI agent. Read this entire prompt carefully. It contains exhaustive instructions, exact specifications, and strict constraints. You must not ask the user any questions, invent undocumented interfaces, or deviate from this specification.

## 1. GOAL AND SUCCESS CRITERIA
**Goal:** Build an autonomous decentralized treasury for the HaloPay ecosystem. Unbanked merchants hold digital aid (USDC) in static offline wallets earning nothing. This system puts those idle balances to work. The on-chain Soroban contract securely vaults the merchant USDC. The off-chain Python agent analyzes live yield opportunities across the Stellar Decentralized Exchange (SDEX) and Automated Market Makers (AMMs), then instructs the vault to allocate idle funds into a chosen opportunity.

**Target Audience:** Humanitarian aid NGOs, unbanked offline merchants, and hackathon judges verifying the technical implementation.

**Success Criteria (Definition of Done):**
The project is complete when a human operator can execute the following exact commands in order and observe the specified outputs:
1. `soroban contract build` (Compiles the Rust contract to an optimized `.wasm` file successfully).
2. `soroban contract deploy --wasm target/wasm32-unknown-unknown/release/halopay_treasury.wasm --source admin --network testnet` (Deploys to Stellar Testnet and outputs a Contract ID starting with `C...`).
3. `cargo test` (Passes all unit and adversarial test cases for the contract).
4. `python -m pytest tests/` (Passes all Python scoring and limit tests).
5. `python src/main.py --mode simulation` (Runs the full decision loop against the testnet contract, logs the SDEX analysis, scores opportunities, and gracefully exits with `[SIMULATION] Decision recorded. No transactions submitted.` without touching funds).

## 2. SYSTEM ARCHITECTURE
The system is a hybrid monorepo with two distinct boundaries:

**A. On-Chain Treasury Vault (Rust/Soroban):**
Lives on the Stellar blockchain. It owns the custody of merchant funds. It exposes strict interfaces to deposit funds, withdraw funds, and allocate funds to DeFi pools. It enforces all cryptographic authorization and hard safety limits. It sits on-chain because it must act as an immutable, trustless escrow that cannot be bypassed.

**B. Off-Chain Yield Agent (Python):**
Lives off-chain on a traditional server. It owns the analytical logic. It pulls pricing and liquidity data from Stellar Horizon endpoints, scores them using a deterministic formula, and constructs transaction payloads. It sits off-chain because querying REST APIs and running complex AI scoring heuristics is impossible (and prohibitively expensive) to execute natively inside a blockchain execution environment.

**Cycle Walkthrough:**
1. **Idle Balance Detected:** The Python Agent queries the Soroban contract state via the Stellar Horizon RPC and detects 500 unallocated USDC belonging to Merchant A.
2. **Opportunity Analyzed:** The Agent queries the SDEX order books for XLM/USDC and AQUA/USDC AMM pools.
3. **Transaction Signed:** The Agent calculates that XLM/USDC offers a 4.2% yield with sufficient liquidity. It constructs a transaction calling the contract's `allocate` function.
4. **Contract Invoked:** The Agent submits the transaction to the Stellar Testnet.
5. **Funds Allocated:** The Soroban contract receives the call. It verifies the signature, ensures the destination AMM is on the on-chain allowlist, ensures the 500 USDC does not exceed the 80% maximum allocation cap, and executes the cross-contract call to move the 500 USDC to the AMM.
6. **Position Recorded:** The contract updates its internal ledger and emits an `AllocationExecuted` event.
7. **Funds Withdrawn:** Later, an authorized administrator submits a `withdraw` transaction, pulling the principal plus yield back from the AMM to the merchant's wallet.

## 3. TRUST AND AUTHORITY MODEL
The AI Agent is completely untrusted by design. It can only propose actions. The smart contract enforces all safety constraints.

**Signers and Roles:**
*   **Admin:** A highly privileged keypair that deploys the contract, configures the allowlist, and executes merchant withdrawals.
*   **Agent (Proposer):** A low-privileged keypair. The contract only allows this keypair to invoke the `allocate` function. It cannot withdraw funds, alter the allowlist, or change contract configurations.

**Separation of Powers:**
The Agent proposes an allocation to a specific AMM contract ID. The Soroban contract authorizes this only if the AMM contract ID matches the Admin's pre-configured allowlist. The Agent is never the sole authority over where funds go.

**Hard Limits Enforced On-Chain (Contract Level):**
The `allocate` function must strictly panic (abort the transaction) if any of these conditions are met:
1.  **Maximum Allocation Per Transaction:** Cannot exceed 1,000 USDC in a single call.
2.  **Maximum Proportion:** Cannot allocate an amount that leaves the treasury's liquid USDC balance below 20% of its total historical deposits (an 80% max allocation ceiling).
3.  **Minimum Balance:** A strict floor of 100 USDC must remain unallocated globally at all times to handle emergency offline settlements.
4.  **Allowlist:** The `destination_amm_address` must exist in the `ALLOWLIST` storage map.

**Compromise Scenario:**
If the Agent's private key is stolen, the attacker can only force the contract to allocate funds to *already approved* AMM pools up to the 80% ceiling. They cannot steal funds, route funds to their own addresses, or drain the 20% emergency reserve.

## 4. REPOSITORY AND FILE STRUCTURE
You must create exactly this tree, with no missing files and no placeholder directories.

```text
.
├── .gitignore                          (Excludes dependencies, build artifacts, and secrets)
├── README.md                           (Project overview and setup instructions)
├── .env.example                        (Template showing required environment variables)
├── contracts/
│   ├── Cargo.toml                      (Rust dependencies and workspace configuration)
│   ├── src/
│   │   ├── lib.rs                      (Entry point exposing contract functions)
│   │   ├── storage.rs                  (Data types and storage keys)
│   │   ├── errors.rs                   (Custom error enums)
│   │   ├── events.rs                   (Event emission logic)
│   │   └── admin.rs                    (Admin-only configuration logic)
│   └── tests/
│       ├── test_deposit.rs             (Unit tests for depositing)
│       ├── test_allocate.rs            (Unit tests covering all hard limits and allowlist)
│       └── test_withdraw.rs            (Unit tests for administrative withdrawals)
└── agent/
    ├── requirements.txt                (Python package dependencies and versions)
    ├── src/
    │   ├── __init__.py                 (Package marker)
    │   ├── main.py                     (Entry point containing the loop and mode selection)
    │   ├── data_fetcher.py             (Queries Stellar Horizon for AMM and DEX data)
    │   ├── scorer.py                   (Deterministic formula for scoring yield opportunities)
    │   ├── contract_client.py          (Constructs and submits Soroban transactions)
    │   └── logger.py                   (Structured JSON logging configuration)
    └── tests/
        ├── test_scorer.py              (Unit tests verifying deterministic scoring logic)
        └── test_limits.py              (Unit tests verifying agent respects local disqualifications)
```

## 5. DEPENDENCIES AND TOOLCHAIN
**Rust / Soroban:**
*   Rust Toolchain: `stable` (via rustup), target: `wasm32-unknown-unknown`
*   Soroban CLI: Version `20.0.0-rc2` (Installed via `cargo install --locked soroban-cli`)
*   Crates (in `contracts/Cargo.toml`): `soroban-sdk = "20.0.0-rc2"`
*   *Why:* Soroban is the only official smart contract platform for Stellar, and `20.0.0-rc2` is the standard target.
*   Build command: `soroban contract build` (Produces optimized WASM). Deployed to `testnet`.

**Python:**
*   Python Version: `3.11`
*   Packages (in `agent/requirements.txt`):
    *   `stellar-sdk==9.0.0` (Official Stellar Horizon and Soroban RPC client)
    *   `requests==2.31.0` (For fetching external API data if Horizon is insufficient)
    *   `pytest==8.1.1` (For running agent unit tests)
*   *Why:* We use `stellar-sdk` over raw HTTP calls because it provides built-in XDR serialization and transaction signing required for Soroban. Do not use alternative async wrappers; stick to the standard synchronous client for predictability.

## 6. CONTRACT SPECIFICATION
The contract is named `YieldTreasuryContract`.

**Data Types & Storage Layout:**
*   `Admin` (Type: `Address`, Tier: `Instance`): The contract owner.
*   `Agent` (Type: `Address`, Tier: `Instance`): The authorized proposer.
*   `Allowlist` (Type: `Map<Address, bool>`, Tier: `Persistent`): Approved DeFi contract addresses.
*   `TotalDeposits` (Type: `u128`, Tier: `Persistent`): Total historical USDC deposited.
*   `TotalAllocated` (Type: `u128`, Tier: `Persistent`): Total USDC currently deployed in DeFi.

**Errors (in `errors.rs`):**
*   `NotAuthorized` (Caller is not Admin/Agent)
*   `ExceedsTransactionCap` (Allocation > 1000)
*   `ExceedsGlobalCap` (Allocation pushes TotalAllocated > 80% of TotalDeposits)
*   `BreachesMinimumFloor` (Allocation leaves liquid balance < 100)
*   `DestinationNotAllowed` (Target address not in Allowlist)
*   `InsufficientBalance` (Attempting to allocate more than liquid holdings)

**Events (in `events.rs`):**
*   `FundsAllocated`: Fields `{ agent: Address, destination: Address, amount: u128 }`
*   `FundsWithdrawn`: Fields `{ admin: Address, amount: u128 }`

**Functions (in `lib.rs`):**
1.  `init(env: Env, admin: Address, agent: Address)`
    *   Validates: Must only be called once. Stores Admin and Agent. Returns `()`.
2.  `add_allowlist(env: Env, target: Address)`
    *   Validates: Caller is Admin. Stores `target` as `true` in Allowlist. Returns `()`.
3.  `deposit(env: Env, amount: u128)`
    *   Validates: None (anyone can deposit). Transfers `amount` of USDC from caller to contract. Increments `TotalDeposits`. Returns `()`.
4.  `allocate(env: Env, destination: Address, amount: u128)`
    *   Validates: Caller is Agent. `destination` is in Allowlist. `amount <= 1000`. `TotalAllocated + amount <= TotalDeposits * 0.8`. `(TotalDeposits - TotalAllocated) - amount >= 100`.
    *   Action: Invokes `destination` cross-contract to deposit `amount`. Increments `TotalAllocated`. Emits `FundsAllocated`. Returns `()`.
5.  `withdraw(env: Env, amount: u128, to: Address)`
    *   Validates: Caller is Admin. Action: Transfers `amount` from contract to `to`. Returns `()`.
6.  `get_position(env: Env) -> (u128, u128)`
    *   Validates: None. Returns `(TotalDeposits, TotalAllocated)`.

## 7. AGENT SPECIFICATION
**Data Sources:**
The agent reads from the Stellar Horizon `/liquidity_pools` endpoint using `stellar-sdk` to find AMM reserves.

**Scoring Formula:**
`Score = (ReserveA / ReserveB) * 100` (A simplistic yield proxy based on pool imbalance for the hackathon context).

**Disqualifications (Outright Rejection):**
*   Liquidity Floor: If total pool reserves are less than 10,000 units, discard.
*   Unknown Assets: If either asset in the pool is not native XLM or a known USDC asset issuer, discard.
*   Thin Markets: If the spread is wider than 2%, discard.

**The Decision Loop (in `main.py`):**
*   **Interval:** Runs exactly once every 60 seconds. `time.sleep(60 - elapsed)`. If `elapsed > 60`, it logs a warning and sleeps for 1 second.
*   **Successful Inaction:** If the highest score is below 1.5, the agent logs `[NO_ACTION] Best score 1.2 is below threshold. Doing nothing.` This is a valid success.
*   **Recording:** Before any Soroban transaction is constructed, the agent logs a JSON payload containing the exact inputs: `{ "timestamp": "...", "pool_id": "...", "score": 1.6, "decision": "ALLOCATE" }`.

**Model Outputs:**
If any LLM or heuristic model is used to dynamically adjust the score threshold, its output must strictly be parsed as a float. If the output is malformed, missing, or negative, the agent must discard the model output, default to a strict threshold of `2.0`, and log the fallback.

## 8. SAFETY MODES AND DEFAULTS
The agent supports three modes passed as a command-line argument (`--mode`):
1.  **`simulation` (DEFAULT):** The full loop runs. Horizon is queried, scores are calculated, logs are written. Soroban transactions are NEVER constructed or signed.
2.  **`proposal`:** Transactions are constructed in memory and their base64 XDR representations are logged for visual approval, but `submit_transaction` is never called.
3.  **`live`:** Transactions are fully signed and submitted to the network.

**Enforcement:**
The `simulation` mode is hardcoded as the default in `main.py`'s `argparse` configuration. Every log line emitted by `logger.py` must prefix the message with `[SIMULATION]`, `[PROPOSAL]`, or `[LIVE]`. The function that calls `stellar-sdk`'s `submit_transaction` must begin with an explicit `if mode != "live": return`.

## 9. BUILD STEPS
Execute these steps strictly in order. Do not skip ahead.

1.  **Initialize Git and Ignore files:** Create the directories and write `.gitignore` to prevent committing secrets or `target/`.
2.  **Scaffold Rust Contract:** Write `Cargo.toml`, `lib.rs`, `storage.rs`, `errors.rs`, `events.rs`.
3.  **Compile Contract:** Run `soroban contract build`. Output must show successful compilation of `halopay_treasury.wasm`.
4.  **Write Contract Tests:** Write `contracts/tests/*.rs`.
5.  **Test Contract:** Run `cargo test`. Output must show `test result: ok.`.
6.  **Scaffold Python Agent:** Write `requirements.txt` and run `pip install -r agent/requirements.txt`.
7.  **Write Agent Logic:** Write the Python files in `agent/src/`.
8.  **Write Agent Tests:** Write `agent/tests/*.py`.
9.  **Test Agent:** Run `python -m pytest agent/tests/`. Output must show `passed`.
10. **E2E Simulation:** Run `python agent/src/main.py --mode simulation`. Output must show structured logs evaluating a pool and stopping before submission.

## 10. TESTING
**Contract Tests (`contracts/tests/`):**
*   Test successful initialization, deposits, and withdrawals.
*   Adversarial Test 1: Call `allocate` with a keypair that is not the Agent (Expect `NotAuthorized`).
*   Adversarial Test 2: Call `allocate` with an amount of 1500 (Expect `ExceedsTransactionCap`).
*   Adversarial Test 3: Call `allocate` targeting an AMM address not added by `add_allowlist` (Expect `DestinationNotAllowed`).
*   Adversarial Test 4: Call `allocate` draining the balance to 50 USDC (Expect `BreachesMinimumFloor`).
*   Adversarial Test 5: A replayed or duplicated instruction.
*   Adversarial Test 6: A withdrawal by the wrong party.

**Agent Tests (`agent/tests/`):**
*   Provide a mocked Horizon JSON response with < 10,000 liquidity. Assert the scorer returns a disqualification.
*   Provide a mocked Horizon JSON response with a fixed input. Assert the scorer outputs the exact expected deterministic float.

**E2E Test Network:**
Testing is performed against the Stellar Testnet. The agent must use the public Soroban RPC URL `https://soroban-testnet.stellar.org`. Accounts are funded using the public Friendbot via `https://friendbot.stellar.org/?addr={public_key}`.

## 11. ENVIRONMENT, KEYS AND SECRETS
**Required Environment Variables (in `.env`):**
*   `STELLAR_NETWORK`: Must be `TESTNET`.
*   `AGENT_SECRET_KEY`: The ed25519 secret key starting with `S...`.
*   `CONTRACT_ID`: The deployed `C...` address of the Soroban treasury.

**Rules:**
Keys must be read using Python's `os.environ.get()`. If `AGENT_SECRET_KEY` is missing or empty, the `main.py` entrypoint must execute `sys.exit("CRITICAL ERROR: AGENT_SECRET_KEY environment variable is missing. Cannot boot.")`.
There is NO fallback signer.
The `.gitignore` must contain `.env`.
Secret keys must never be passed to the `logger.py` functions. No key is ever committed, hardcoded, or printed.

## 12. OBSERVABILITY
**Log Format:**
Logs must be structured JSON printed to `stdout`.
Example: `{"timestamp": "2026-08-28T12:00:00Z", "mode": "[LIVE]", "level": "INFO", "event": "SCORE_EVALUATED", "pool": "CD3...", "score": 2.1, "decision": "ALLOCATE_500"}`

**Reconstruction:**
Every allocation must be reconstructable afterwards from logs plus on-chain events alone: what was seen, what was scored, what was chosen, what was rejected and why. 

**Inspection:**
To inspect current positions and total allocated at any moment, a person runs `soroban contract read --id {CONTRACT_ID} --network testnet --key get_position`.

## 13. FALLBACK DOCTRINE
If you face an unknown state, follow these exact instructions:
*   **Unreachable Endpoint / Rate Limit:** If Horizon returns 429, 500, or times out, catch the exception, log `{"event": "NETWORK_ERROR", "action": "SLEEP_AND_RETRY"}`, and sleep for 60 seconds. Do not crash. Do not retry immediately.
*   **Malformed Response / Empty Response:** If Horizon returns JSON missing expected keys (e.g., `reserves`), log `{"event": "PARSE_ERROR", "action": "DISCARD_POOL"}` and skip that pool.
*   **Transaction Submit Failure:** If `submit_transaction` throws an error, log the error and stop the current loop iteration. Do NOT blindly retry the transaction.
*   **Transaction Unconfirmed:** If a transaction submits but does not confirm within the expected window, log `{"event": "UNCONFIRMED_TX", "action": "DO_NOTHING"}` and wait for the next loop.
*   **Undocumented SDK Method:** If you think an SDK method exists but it throws `AttributeError`, fall back to making a raw HTTP GET request using the `requests` library to the public Horizon REST API, and log `{"event": "SDK_FALLBACK", "action": "RAW_HTTP"}`.
*   **Insufficient Balance / Unknown Value:** If you cannot determine the total deposits, or if the balance is insufficient, default to assuming `0` and halt allocation. Do nothing.
*   **Rule:** The building agent must never stop to ask the user a question. The building agent must never invent an undocumented interface and proceed as if it were real. If something cannot be verified from within the prompt itself, use a documented fallback and log which path you took. For anything touching funds, the fallback is always to stop and do nothing, never to retry blindly and never to proceed on an assumption.

## 14. VERSION CONTROL DISCIPLINE
You must make granular, atomic Git commits throughout the build process.
*   **Git Identity:** Before making the first commit, ensure the git config is set to `git config user.name "0dillon"` and `git config user.email "dillonofili667@gmail.com"`.
*   **Forbidden Commands:** Do not use `git add .`, `git add -A`, or `git add *`. Blanket staging of the working tree is forbidden.
*   **Staging:** You must specify exact file paths: `git add contracts/src/lib.rs`.
*   **Frequency:** Commit after every meaningful change, not once at the end. If a step touched files belonging to two separate concerns, that is two commits. 
*   **Message Format:** `feat(scope): action and reason`. Example: `feat(contracts): implement allowlist to restrict external cross-contract calls`. The message must state what changed and why, rather than restating the filename.
*   **Hygiene:** Run `git status` before moving to the next build step to ensure the working tree is clean. The `.gitignore` must be written and committed first before any source code, so no secret, build artifact, or dependency directory is ever committed.
*   **Pushing:** The local directory is already cloned from GitHub. At the end of every successful build step, you must push the commits to the remote repository using `git push origin main`.

## 15. VERIFICATION AND PROOF
To prove the system works to a judge or outsider:
1.  The Python agent logs will output `{"event": "TRANSACTION_SUBMITTED", "tx_hash": "abc123def..."}`.
2.  The user copies that `tx_hash` and pastes it into Stellar Expert (https://stellar.expert/explorer/testnet).
3.  The block explorer will visually confirm that the `allocate` function was called on the `CONTRACT_ID`, and that the smart contract successfully invoked the DeFi pool.
4.  If a link fails to resolve immediately, present the message: "The Stellar network is processing the ledger. Please check the transaction hash `[HASH]` on stellar.expert in 5 seconds." Do not offer a broken HTTP link as proof.

## 16. WHAT NOT TO BUILD (OUT OF SCOPE)
Do NOT build any of the following. If you are tempted to add them, stop.
*   Do NOT build a Web UI, React frontend, or terminal dashboard (TUI). The JSON logs are sufficient.
*   Do NOT implement actual complex AI models (like neural networks or LLMs) for the scoring formula. Stick strictly to the simple math proxy defined in Section 7.
*   Do NOT build a database (PostgreSQL/SQLite) for the agent. The agent is entirely stateless and reads the current truth directly from the blockchain.
*   Do NOT implement withdrawal logic in the Python agent. Withdrawals are handled manually by the Admin via the CLI.
