from enum import Enum
import time
from typing import Any, Dict, Optional


class CircuitState(str, Enum):
    CLOSED = "closed"        # Normal operations
    HALF_OPEN = "half_open"  # Testing recovery
    OPEN = "open"            # Tripped: Emergency withdrawal active


class EmergencyCircuitBreaker:
    """High-performance, low-latency Emergency Withdrawal Circuit Breaker.

    Operates in O(1) time with zero external I/O on the critical path
    to guard DeFi vault assets against rapid drawdowns and oracle failures.
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout_seconds: float = 60.0,
        half_open_success_threshold: int = 2,
    ) -> None:
        if failure_threshold <= 0:
            raise ValueError("failure_threshold must be positive")
        if recovery_timeout_seconds <= 0:
            raise ValueError("recovery_timeout_seconds must be positive")
        if half_open_success_threshold <= 0:
            raise ValueError("half_open_success_threshold must be positive")

        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        self.half_open_success_threshold = half_open_success_threshold

        self.state: CircuitState = CircuitState.CLOSED
        self.failure_count: int = 0
        self.success_count: int = 0
        self.last_failure_time: Optional[float] = None
        self.emergency_override: bool = False

    def is_operational(self, current_time: Optional[float] = None) -> bool:
        """Evaluates whether normal vault execution is permitted in O(1) time.

        Returns:
            True if operations are allowed (CLOSED or recovery in HALF_OPEN),
            False if circuit is OPEN (emergency withdrawal required).
        """
        if self.emergency_override:
            return False

        if self.state == CircuitState.CLOSED:
            return True

        now = current_time if current_time is not None else time.time()

        if self.state == CircuitState.OPEN:
            if self.last_failure_time is not None:
                elapsed = now - self.last_failure_time
                if elapsed >= self.recovery_timeout_seconds:
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                    return True
            return False

        # HALF_OPEN state allows probationary execution
        return True

    def record_success(self) -> None:
        """Records a successful operation and handles recovery transition."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.half_open_success_threshold:
                self.reset()
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    def record_failure(
        self, current_time: Optional[float] = None
    ) -> CircuitState:
        """Records a failure event and trips the circuit if threshold met."""
        now = current_time if current_time is not None else time.time()
        self.last_failure_time = now

        if self.state == CircuitState.HALF_OPEN:
            # Immediate trip on probationary failure
            self.state = CircuitState.OPEN
        else:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN

        return self.state

    def trip_emergency(self) -> None:
        """Manually forces the circuit breaker into emergency open state."""
        self.emergency_override = True
        self.state = CircuitState.OPEN

    def reset(self) -> None:
        """Resets the circuit breaker to closed baseline."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.emergency_override = False

    def get_telemetry(self) -> Dict[str, Any]:
        """Returns structured diagnostic status dictionary."""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "emergency_override": self.emergency_override,
            "last_failure_time": self.last_failure_time,
        }
