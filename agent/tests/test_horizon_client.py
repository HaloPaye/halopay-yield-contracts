from unittest.mock import MagicMock
import pytest
import requests
from src.infrastructure.horizon_client import (
    HorizonClient,
    HorizonClientError,
    HorizonRateLimitError,
)


def test_horizon_client_init_validation() -> None:
    with pytest.raises(ValueError, match="base_url must start with"):
        HorizonClient(base_url="ftp://invalid.url")

    with pytest.raises(ValueError, match="timeout_seconds must be positive"):
        HorizonClient(timeout_seconds=0)


def test_get_account_and_balances() -> None:
    mock_session = MagicMock(spec=requests.Session)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "GACCOUNT123",
        "sequence": "1001",
        "balances": [
            {"asset_type": "native", "balance": "100.50"},
            {
                "asset_type": "credit_alphanum4",
                "asset_code": "USDC",
                "asset_issuer": "GISSUER456",
                "balance": "5000.00",
            },
        ],
    }
    mock_session.get.return_value = mock_response

    client = HorizonClient(session=mock_session)
    account = client.get_account("GACCOUNT123")
    assert account["id"] == "GACCOUNT123"

    balances = client.get_account_balances("GACCOUNT123")
    assert len(balances) == 2
    assert balances[0] == {"asset": "XLM", "balance": "100.50"}
    assert balances[1] == {"asset": "USDC:GISSUER456", "balance": "5000.00"}


def test_get_account_empty_id_raises() -> None:
    client = HorizonClient()
    with pytest.raises(ValueError, match="account_id cannot be empty"):
        client.get_account("")


def test_get_fee_stats() -> None:
    mock_session = MagicMock(spec=requests.Session)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "last_ledger_base_fee": "100",
        "fee_charged": {"min": "100", "mode": "100", "p95": "200"},
    }
    mock_session.get.return_value = mock_response

    client = HorizonClient(session=mock_session)
    stats = client.get_fee_stats()
    assert stats["last_ledger_base_fee"] == "100"


def test_get_liquidity_pools() -> None:
    mock_session = MagicMock(spec=requests.Session)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "_embedded": {
            "records": [
                {"id": "pool1", "total_shares": "1000"},
                {"id": "pool2", "total_shares": "2000"},
            ]
        }
    }
    mock_session.get.return_value = mock_response

    client = HorizonClient(session=mock_session)
    pools = client.get_liquidity_pools(limit=10)
    assert len(pools) == 2
    assert pools[0]["id"] == "pool1"


def test_rate_limit_error_handling() -> None:
    mock_session = MagicMock(spec=requests.Session)
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_session.get.return_value = mock_response

    client = HorizonClient(session=mock_session)
    with pytest.raises(HorizonRateLimitError, match="rate limit reached"):
        client.get_fee_stats()


def test_generic_request_error_handling() -> None:
    mock_session = MagicMock(spec=requests.Session)
    mock_session.get.side_effect = requests.exceptions.ConnectionError(
        "Network unreachable"
    )

    client = HorizonClient(session=mock_session)
    with pytest.raises(HorizonClientError, match="Horizon request failed"):
        client.get_fee_stats()
