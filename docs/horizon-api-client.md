# Horizon API Client

## Overview
The `HorizonClient` module (`agent/src/infrastructure/horizon_client.py`) provides an enterprise-ready HTTP integration layer for interacting with Stellar Horizon REST APIs.

## Capabilities & Architecture
- **Connection Pooling:** Uses underlying persistent `requests.Session` with HTTP adapter connection pooling (10 connections, max pool size 20) to eliminate TCP/TLS handshake overhead during continuous polling.
- **Exponential Backoff & Retries:** Automatically handles transient network dropouts and gateway errors (500, 502, 503, 504) via configurable retry policies.
- **Rate Limit Detection:** Detects HTTP 429 Too Many Requests and raises dedicated `HorizonRateLimitError` for backpressure signaling.
- **Structured Resource Parsing:** Normalizes account balances (separating native XLM from alphanumeric credit tokens) and paginated liquidity pool queries.

## Usage Example

```python
from src.infrastructure.horizon_client import HorizonClient

client = HorizonClient(
    base_url="https://horizon-testnet.stellar.org",
    timeout_seconds=10.0,
    max_retries=3,
)

# Fetch fee stats
stats = client.get_fee_stats()

# Query liquidity pools
pools = client.get_liquidity_pools(limit=50)

# Retrieve normalized account balances
balances = client.get_account_balances("GCALKSGAZRJLSUEJT3M5W6LN4R7XQOLIRCOS6ZA6EDZVTZDBIIPPFKJ6")

client.close()
```
