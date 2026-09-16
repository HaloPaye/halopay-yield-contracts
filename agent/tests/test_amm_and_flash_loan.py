import os
import sys
from decimal import Decimal

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.domain.amm_calculator import AmmCalculator  # noqa: E402
from src.infrastructure.horizon_stream import HorizonStreamWatcher  # noqa: E402
from src.domain.pool_adapter import PoolAdapter  # noqa: E402
from src.domain.flash_loan_detector import FlashLoanDetector  # noqa: E402


def test_amm_calculator_get_amount_out():
    calc = AmmCalculator(fee_fraction=Decimal("0.003"))
    amount_in = Decimal("100")
    reserve_in = Decimal("10000")
    reserve_out = Decimal("20000")

    amount_out = calc.get_amount_out(amount_in, reserve_in, reserve_out)
    assert amount_out > Decimal("0")
    assert amount_out < Decimal("200")  # slightly less than 2x due to impact + fee


def test_amm_calculator_price_impact():
    calc = AmmCalculator()
    impact = calc.calculate_price_impact(Decimal("100"), Decimal("10000"))
    assert impact == Decimal("0.0099010")


def test_horizon_stream_backoff():
    watcher = HorizonStreamWatcher(
        "https://horizon.stellar.org", initial_backoff_sec=1.0, max_backoff_sec=10.0
    )
    assert not watcher.is_connected

    watcher.on_connect()
    assert watcher.is_connected

    delay1 = watcher.on_disconnect()
    assert delay1 == 1.0
    assert not watcher.is_connected

    delay2 = watcher.on_disconnect()
    assert delay2 == 2.0


def test_pool_adapter_ranking():
    adapter = PoolAdapter("Soroswap")
    pools = [
        {"id": "pool_small", "reserve_a": 1000, "reserve_b": 2000, "fee_bps": 30},
        {"id": "pool_large", "reserve_a": 50000, "reserve_b": 50000, "fee_bps": 25},
    ]
    ranked = adapter.rank_pools_by_depth(pools)
    assert ranked[0]["pool_id"] == "pool_large"
    assert ranked[0]["fee_rate"] == Decimal("0.0025")
    assert ranked[1]["pool_id"] == "pool_small"


def test_flash_loan_detector():
    detector = FlashLoanDetector(
        max_volume_ratio=Decimal("3.0"), max_price_deviation=Decimal("0.08")
    )

    # Normal swap
    normal = detector.inspect_swap(
        historical_mean_volume=Decimal("1000"),
        tx_volume=Decimal("1200"),
        pre_price=Decimal("1.0"),
        post_price=Decimal("1.01"),
    )
    assert not normal["flagged"]

    # Flash loan spike
    spike = detector.inspect_swap(
        historical_mean_volume=Decimal("1000"),
        tx_volume=Decimal("15000"),  # 15x
        pre_price=Decimal("1.0"),
        post_price=Decimal("1.25"),  # 25% shift
    )
    assert spike["flagged"]
    assert "Flash loan anomaly detected" in spike["reason"]
