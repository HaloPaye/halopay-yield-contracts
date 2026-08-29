# Security Policy

## Vulnerability Reporting
Please do not disclose security vulnerabilities publicly. Email all findings to security@halopay.example.com. We will respond within 48 hours.

## On-Chain Safety Limits
The HaloPay Yield Contract implements strict on-chain safeguards:
1. **Max Allocation**: The contract enforces a hard global cap. A maximum of 80% of total deposits can be allocated to external pools at any given time.
2. **Allowlist**: Funds can only be allocated to destinations explicitly whitelisted by the Admin.
3. **Authorization**: Strict `require_auth()` checks ensure the Agent cannot change the allowlist, and the Admin cannot submit allocations directly.
