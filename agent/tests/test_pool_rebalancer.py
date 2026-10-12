from decimal import Decimal
import pytest
from src.domain.pool_rebalancer import PoolRebalancer


def test_rebalancer_init_validation() -> None:
    with pytest.raises(ValueError, match="dead_zone_pct cannot be negative"):
        PoolRebalancer(dead_zone_pct=Decimal("-0.01"))

    with pytest.raises(ValueError, match="min_trade_size cannot be negative"):
        PoolRebalancer(min_trade_size=Decimal("-0.0001"))


def test_rebalancer_empty_inputs() -> None:
    rebalancer = PoolRebalancer()
    assert rebalancer.compute_rebalance_actions({}, {}) == []
    assert (
        rebalancer.compute_rebalance_actions({"USDC": Decimal("100")}, {})
        == []
    )
    assert (
        rebalancer.compute_rebalance_actions({}, {"USDC": Decimal("1.0")})
        == []
    )


def test_rebalancer_zero_total_value() -> None:
    rebalancer = PoolRebalancer()
    current = {"USDC": Decimal("0"), "XLM": Decimal("0")}
    targets = {"USDC": Decimal("0.5"), "XLM": Decimal("0.5")}
    assert rebalancer.compute_rebalance_actions(current, targets) == []


def test_rebalancer_negative_balance_raises() -> None:
    rebalancer = PoolRebalancer()
    with pytest.raises(
        ValueError, match="Balance for asset USDC cannot be negative"
    ):
        rebalancer.compute_rebalance_actions(
            {"USDC": Decimal("-10"), "XLM": Decimal("50")},
            {"USDC": Decimal("0.5"), "XLM": Decimal("0.5")},
        )


def test_rebalancer_negative_weight_raises() -> None:
    rebalancer = PoolRebalancer()
    with pytest.raises(
        ValueError, match="Target weight for asset USDC cannot be negative"
    ):
        rebalancer.compute_rebalance_actions(
            {"USDC": Decimal("100"), "XLM": Decimal("100")},
            {"USDC": Decimal("-0.2"), "XLM": Decimal("1.2")},
        )


def test_rebalancer_balanced_portfolio_no_actions() -> None:
    rebalancer = PoolRebalancer(dead_zone_pct=Decimal("0.02"))
    current = {"USDC": Decimal("500"), "XLM": Decimal("500")}
    targets = {"USDC": Decimal("0.50"), "XLM": Decimal("0.50")}
    actions = rebalancer.compute_rebalance_actions(current, targets)
    assert actions == []


def test_rebalancer_dead_zone_suppression() -> None:
    rebalancer = PoolRebalancer(dead_zone_pct=Decimal("0.05"))
    # USDC weight is 52%, target is 50%. Difference is 2% < 5% dead zone.
    current = {"USDC": Decimal("520"), "XLM": Decimal("480")}
    targets = {"USDC": Decimal("0.50"), "XLM": Decimal("0.50")}
    actions = rebalancer.compute_rebalance_actions(current, targets)
    assert actions == []


def test_rebalancer_unallocated_held_asset_liquidated() -> None:
    # Portfolio holds asset BTC that is NOT in the target weights.
    rebalancer = PoolRebalancer(dead_zone_pct=Decimal("0.01"))
    current = {
        "USDC": Decimal("500"),
        "XLM": Decimal("300"),
        "BTC": Decimal("200"),
    }
    targets = {"USDC": Decimal("0.60"), "XLM": Decimal("0.40")}
    actions = rebalancer.compute_rebalance_actions(current, targets)

    action_dict = dict(actions)
    # BTC should be sold down to 0 (-200)
    assert action_dict["BTC"] == Decimal("-200.0000000")
    # USDC target is 600, currently 500 (+100)
    assert action_dict["USDC"] == Decimal("100.0000000")
    # XLM target is 400, currently 300 (+100)
    assert action_dict["XLM"] == Decimal("100.0000000")


def test_rebalancer_new_asset_bought() -> None:
    # Target includes an asset ETH currently not held.
    rebalancer = PoolRebalancer(dead_zone_pct=Decimal("0.01"))
    current = {"USDC": Decimal("1000")}
    targets = {"USDC": Decimal("0.70"), "ETH": Decimal("0.30")}
    actions = rebalancer.compute_rebalance_actions(current, targets)

    action_dict = dict(actions)
    assert action_dict["USDC"] == Decimal("-300.0000000")
    assert action_dict["ETH"] == Decimal("300.0000000")


def test_rebalancer_target_weight_normalization() -> None:
    # Target weights given as ratios that don't sum to 1.0 (e.g. 50:50)
    rebalancer = PoolRebalancer(dead_zone_pct=Decimal("0.02"))
    current = {"USDC": Decimal("700"), "XLM": Decimal("300")}
    targets = {"USDC": Decimal("50"), "XLM": Decimal("50")}
    actions = rebalancer.compute_rebalance_actions(current, targets)

    action_dict = dict(actions)
    assert action_dict["USDC"] == Decimal("-200.0000000")
    assert action_dict["XLM"] == Decimal("200.0000000")
