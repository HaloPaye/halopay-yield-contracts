from decimal import Decimal
from src.domain.pool_rebalancer import PoolRebalancer
from src.infrastructure.metrics_collector import MetricsCollector
from src.domain.apy_aggregator import ApyAggregator
from src.domain.slippage_guard import SlippageGuard


def test_pool_rebalancer_actions() -> None:
    rebalancer = PoolRebalancer(dead_zone_pct=Decimal("0.05"))
    current = {"USDC": Decimal("700"), "XLM": Decimal("300")}
    targets = {"USDC": Decimal("0.50"), "XLM": Decimal("0.50")}
    actions = rebalancer.compute_rebalance_actions(current, targets)
    assert len(actions) == 2


def test_metrics_collector() -> None:
    collector = MetricsCollector()
    collector.inc_counter("tx_success", 2)
    assert collector.get_counter("tx_success") == 2
    collector.set_gauge("apy_yield", 0.085)
    assert collector.get_gauge("apy_yield") == 0.085


def test_apy_aggregator() -> None:
    aggregator = ApyAggregator(lookback_periods=3)
    returns = [Decimal("0.0002"), Decimal("0.0003"), Decimal("0.0004")]
    apy = aggregator.calculate_rolling_apy(returns)
    assert apy > Decimal("0.10")


def test_slippage_guard() -> None:
    guard = SlippageGuard(max_allowed_slippage=Decimal("0.02"))
    assert guard.evaluate_order_slippage(Decimal("1.00"), Decimal("1.01"))
    assert not guard.evaluate_order_slippage(Decimal("1.00"), Decimal("1.05"))
