from typing import Any, Dict, List, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class HorizonClientError(Exception):
    """Base exception for Horizon client errors."""
    pass


class HorizonRateLimitError(HorizonClientError):
    """Raised when Horizon returns HTTP 429 Too Many Requests."""
    pass


class HorizonClient:
    """Robust, production-grade client for Stellar Horizon REST API.

    Features connection pooling, automatic retries with exponential backoff,
    rate limit detection, and structured response parsing.
    """

    def __init__(
        self,
        base_url: str = "https://horizon-testnet.stellar.org",
        timeout_seconds: float = 10.0,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        session: Optional[requests.Session] = None,
    ) -> None:
        if not base_url.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http:// or https://")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")

        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

        if session is not None:
            self.session = session
        else:
            self.session = requests.Session()
            retry_strategy = Retry(
                total=max_retries,
                backoff_factor=backoff_factor,
                status_forcelist=[500, 502, 503, 504],
                allowed_methods=["GET", "POST"],
            )
            adapter = HTTPAdapter(
                max_retries=retry_strategy,
                pool_connections=10,
                pool_maxsize=20,
            )
            self.session.mount("https://", adapter)
            self.session.mount("http://", adapter)

    def _get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Internal helper for executing GET requests with error handling."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            resp = self.session.get(
                url, params=params, timeout=self.timeout_seconds
            )
            if resp.status_code == 429:
                raise HorizonRateLimitError(
                    "Horizon API rate limit reached (HTTP 429)"
                )
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            if not isinstance(e, HorizonRateLimitError):
                raise HorizonClientError(f"Horizon request failed: {e}") from e
            raise

    def get_account(self, account_id: str) -> Dict[str, Any]:
        """Fetches account details including balances and sequence numbers."""
        if not account_id:
            raise ValueError("account_id cannot be empty")
        return self._get(f"accounts/{account_id}")

    def get_account_balances(self, account_id: str) -> List[Dict[str, str]]:
        """Extracts and parses asset balances for a specific account."""
        data = self.get_account(account_id)
        raw_balances = data.get("balances", [])
        parsed: List[Dict[str, str]] = []
        for b in raw_balances:
            asset_type = b.get("asset_type")
            if asset_type == "native":
                symbol = "XLM"
            else:
                code = b.get("asset_code", "")
                issuer = b.get("asset_issuer", "")
                symbol = f"{code}:{issuer}" if issuer else code
            parsed.append({"asset": symbol, "balance": b.get("balance", "0")})
        return parsed

    def get_fee_stats(self) -> Dict[str, Any]:
        """Fetches current network fee statistics."""
        return self._get("fee_stats")

    def get_liquidity_pools(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Queries active Stellar liquidity pools."""
        clamped_limit = max(1, min(200, limit))
        data = self._get("liquidity_pools", params={"limit": clamped_limit})
        return data.get("_embedded", {}).get("records", [])

    def close(self) -> None:
        """Closes the underlying requests session."""
        self.session.close()
