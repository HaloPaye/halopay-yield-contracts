from typing import Dict


class MetricsCollector:
    def __init__(self) -> None:
        self.counters: Dict[str, int] = {}
        self.gauges: Dict[str, float] = {}

    def inc_counter(self, name: str, amount: int = 1) -> int:
        if amount < 0:
            raise ValueError("Counter increments must be non-negative")
        self.counters[name] = self.counters.get(name, 0) + amount
        return self.counters[name]

    def set_gauge(self, name: str, value: float) -> None:
        self.gauges[name] = float(value)

    def get_counter(self, name: str) -> int:
        return self.counters.get(name, 0)

    def get_gauge(self, name: str) -> float:
        return self.gauges.get(name, 0.0)
