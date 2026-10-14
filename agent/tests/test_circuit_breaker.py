import pytest
from src.domain.circuit_breaker import CircuitState, EmergencyCircuitBreaker


def test_circuit_breaker_init_validation() -> None:
    with pytest.raises(ValueError, match="failure_threshold must be positive"):
        EmergencyCircuitBreaker(failure_threshold=0)

    with pytest.raises(
        ValueError, match="recovery_timeout_seconds must be positive"
    ):
        EmergencyCircuitBreaker(recovery_timeout_seconds=-5.0)

    with pytest.raises(
        ValueError, match="half_open_success_threshold must be positive"
    ):
        EmergencyCircuitBreaker(half_open_success_threshold=0)


def test_circuit_breaker_normal_lifecycle() -> None:
    breaker = EmergencyCircuitBreaker(
        failure_threshold=2,
        recovery_timeout_seconds=10.0,
        half_open_success_threshold=2,
    )
    # Starts closed
    assert breaker.is_operational()
    assert breaker.state == CircuitState.CLOSED

    # Single failure does not trip
    breaker.record_failure(current_time=100.0)
    assert breaker.is_operational()
    assert breaker.state == CircuitState.CLOSED

    # Second failure trips
    breaker.record_failure(current_time=101.0)
    assert not breaker.is_operational(current_time=105.0)
    assert breaker.state == CircuitState.OPEN

    # Recovery timeout expires (10s elapsed) -> becomes HALF_OPEN
    assert breaker.is_operational(current_time=112.0)
    assert breaker.state == CircuitState.HALF_OPEN

    # Two consecutive successes in HALF_OPEN close the circuit
    breaker.record_success()
    assert breaker.state == CircuitState.HALF_OPEN
    breaker.record_success()
    assert breaker.state == CircuitState.CLOSED
    assert breaker.is_operational()


def test_circuit_breaker_half_open_failure_immediate_trip() -> None:
    breaker = EmergencyCircuitBreaker(
        failure_threshold=2, recovery_timeout_seconds=5.0
    )
    breaker.record_failure(current_time=100.0)
    breaker.record_failure(current_time=101.0)
    assert breaker.state == CircuitState.OPEN

    # Transition to half open
    assert breaker.is_operational(current_time=107.0)
    assert breaker.state == CircuitState.HALF_OPEN

    # Any failure during half open trips immediately
    breaker.record_failure(current_time=108.0)
    assert breaker.state == CircuitState.OPEN
    assert not breaker.is_operational(current_time=109.0)


def test_circuit_breaker_manual_emergency_override() -> None:
    breaker = EmergencyCircuitBreaker()
    assert breaker.is_operational()

    breaker.trip_emergency()
    assert not breaker.is_operational()
    assert breaker.state == CircuitState.OPEN

    breaker.reset()
    assert breaker.is_operational()
    assert breaker.state == CircuitState.CLOSED


def test_circuit_breaker_telemetry() -> None:
    breaker = EmergencyCircuitBreaker(failure_threshold=3)
    breaker.record_failure(current_time=100.0)
    telemetry = breaker.get_telemetry()
    assert telemetry["state"] == "closed"
    assert telemetry["failure_count"] == 1
    assert telemetry["emergency_override"] is False
    assert telemetry["last_failure_time"] == 100.0
