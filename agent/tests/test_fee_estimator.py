import pytest
from src.domain.fee_estimator import FeeEstimator, PriorityLevel


def test_fee_estimator_init_validation() -> None:
    with pytest.raises(ValueError, match="alpha must be within"):
        FeeEstimator(alpha=0.0)

    with pytest.raises(ValueError, match="alpha must be within"):
        FeeEstimator(alpha=1.5)

    with pytest.raises(ValueError, match="Invalid min_fee or max_fee"):
        FeeEstimator(min_fee=1000, max_fee=500)

    with pytest.raises(ValueError, match="base_fee must be within"):
        FeeEstimator(base_fee=50, min_fee=100, max_fee=1000)


def test_fee_estimator_negative_fee_rejected() -> None:
    estimator = FeeEstimator()
    with pytest.raises(ValueError, match="observed_fee cannot be negative"):
        estimator.update_fee(-10)


def test_fee_estimator_surge_clamping() -> None:
    # Base fee 100, max surge ratio 3.0 -> effective surge cap = 300
    estimator = FeeEstimator(alpha=0.5, base_fee=100, max_surge_ratio=3.0)
    # Observed fee 5000 is clamped to 300
    res = estimator.update_fee(5000)
    assert estimator.spike_detected is True
    # EMA: 0.5 * 300 + 0.5 * 100 = 200
    assert res == pytest.approx(200.0)


def test_fee_estimator_min_fee_clamping() -> None:
    estimator = FeeEstimator(alpha=0.5, base_fee=100, min_fee=100)
    # If observed fee is below min_fee (e.g. 50), it is clamped to min_fee 100
    res = estimator.update_fee(50)
    assert res == pytest.approx(100.0)


def test_fee_estimator_priority_levels() -> None:
    estimator = FeeEstimator(base_fee=100)
    assert estimator.get_recommended_fee(PriorityLevel.LOW) == 100
    assert estimator.get_recommended_fee(PriorityLevel.NORMAL) == 110
    assert estimator.get_recommended_fee(PriorityLevel.HIGH) == 150
    assert estimator.get_recommended_fee(PriorityLevel.CRITICAL) == 200


def test_fee_estimator_reset() -> None:
    estimator = FeeEstimator(base_fee=100)
    estimator.update_fee(200)
    assert estimator.get_recommended_fee() > 100
    estimator.reset(150)
    assert estimator.get_recommended_fee() == 150
    assert len(estimator.history) == 0
    assert estimator.spike_detected is False


def test_fee_estimator_reset_out_of_bounds() -> None:
    estimator = FeeEstimator(min_fee=100, max_fee=1000)
    with pytest.raises(ValueError, match="Reset fee out of bounds"):
        estimator.reset(50)
