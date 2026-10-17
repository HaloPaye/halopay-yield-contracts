from src.domain import (
    AmmCalculator,
    ApyAggregator,
    CircuitState,
    EmergencyCircuitBreaker,
    FeeEstimator,
    MultiSigCoordinator,
    PoolRebalancer,
)
from src.infrastructure import (
    HorizonClient,
    HorizonStreamWatcher,
    MetricsCollector,
)


def test_domain_exports() -> None:
    assert AmmCalculator is not None
    assert ApyAggregator is not None
    assert CircuitState is not None
    assert EmergencyCircuitBreaker is not None
    assert FeeEstimator is not None
    assert MultiSigCoordinator is not None
    assert PoolRebalancer is not None


def test_infrastructure_exports() -> None:
    assert HorizonClient is not None
    assert HorizonStreamWatcher is not None
    assert MetricsCollector is not None
