import math
from typing import List


class VolatilityTracker:
    def __init__(self, window_size: int = 10, volatility_threshold: float = 0.05):
        self.window_size = window_size
        self.volatility_threshold = volatility_threshold
        self.price_history: List[float] = []

    def record_price(self, price: float) -> None:
        if price > 0:
            self.price_history.append(price)
            if len(self.price_history) > self.window_size:
                self.price_history.pop(0)

    def calculate_volatility(self) -> float:
        if len(self.price_history) < 2:
            return 0.0
        mean = sum(self.price_history) / len(self.price_history)
        variance = sum((p - mean) ** 2 for p in self.price_history) / len(
            self.price_history
        )
        return math.sqrt(variance) / mean

    def should_trigger_rebalance(self) -> bool:
        return self.calculate_volatility() >= self.volatility_threshold
