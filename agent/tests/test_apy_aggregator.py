from decimal import Decimal
import pytest
from src.domain.apy_aggregator import ApyAggregator


def test_apy_aggregator_init_validation() -> None:
    with pytest.raises(ValueError, match="lookback_periods must be greater"):
        ApyAggregator(lookback_periods=0)

    with pytest.raises(ValueError, match="max_allowed_apy must be positive"):
        ApyAggregator(max_allowed_apy=Decimal("0"))

    with pytest.raises(ValueError, match="min_daily_return must be less"):
        ApyAggregator(
            min_daily_return=Decimal("0.2"), max_daily_return=Decimal("0.1")
        )


def test_apy_aggregator_empty_and_invalid_inputs() -> None:
    aggregator = ApyAggregator()
    assert aggregator.calculate_rolling_apy([]) == Decimal("0")
    invalid_inputs = ["invalid", "nan", None]
    assert aggregator.calculate_rolling_apy(invalid_inputs) == Decimal("0")


def test_apy_aggregator_standard_returns() -> None:
    aggregator = ApyAggregator(lookback_periods=3)
    returns = [Decimal("0.0002"), Decimal("0.0003"), Decimal("0.0004")]
    apy = aggregator.calculate_rolling_apy(returns)
    assert apy > Decimal("0.10")
    assert not aggregator.anomaly_detected


def test_apy_aggregator_flash_loan_spike_clamping() -> None:
    aggregator = ApyAggregator(
        lookback_periods=3,
        max_daily_return=Decimal("0.05"),
        max_allowed_apy=Decimal("2.0"),
    )
    # Huge spike of 500% daily return (flash loan manipulation)
    returns = [Decimal("0.001"), Decimal("0.001"), Decimal("5.00")]
    apy = aggregator.calculate_rolling_apy(returns)
    assert aggregator.anomaly_detected is True
    # 5.00 should have been clamped to 0.05
    # avg = (0.001 + 0.001 + 0.05) / 3 = 0.01733...
    # * 365 = ~6.32, clamped to max_allowed_apy 2.0
    assert apy <= Decimal("2.0")


def test_apy_aggregator_compound_interest() -> None:
    aggregator = ApyAggregator(lookback_periods=1)
    returns = [Decimal("0.001")]  # 0.1% daily
    apy_simple = aggregator.calculate_rolling_apy(returns, compound=False)
    apy_compound = aggregator.calculate_rolling_apy(returns, compound=True)
    # Compound APY should be strictly greater than simple APR
    assert apy_compound > apy_simple


def test_compute_summary_stats() -> None:
    aggregator = ApyAggregator(lookback_periods=5)
    returns = [Decimal("0.001"), Decimal("0.002"), Decimal("0.0015")]
    apy, stddev, anomaly = aggregator.compute_summary_stats(returns)
    assert apy > Decimal("0")
    assert stddev > Decimal("0")
    assert anomaly is False
