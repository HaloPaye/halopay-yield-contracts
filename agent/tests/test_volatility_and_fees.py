import pytest
from src.domain.volatility_tracker import VolatilityTracker
from src.domain.fee_estimator import FeeEstimator


def test_volatility_tracker_flat_prices():
    tracker = VolatilityTracker(window_size=5, volatility_threshold=0.05)
    for _ in range(5):
        tracker.record_price(1.0)
    assert tracker.calculate_volatility() == pytest.approx(0.0)
    assert not tracker.should_trigger_rebalance()


def test_volatility_tracker_spike():
    tracker = VolatilityTracker(window_size=5, volatility_threshold=0.05)
    for p in [1.0, 1.0, 1.0, 1.5, 2.0]:
        tracker.record_price(p)
    assert tracker.calculate_volatility() > 0.05
    assert tracker.should_trigger_rebalance()


def test_fee_estimator_ema():
    estimator = FeeEstimator(alpha=0.5, base_fee=100)
    res = estimator.update_fee(200)
    assert res == pytest.approx(150.0)
    assert estimator.get_recommended_fee() == 150
