from decimal import Decimal
from typing import List


class ApyAggregator:
    def __init__(self, lookback_periods: int = 7) -> None:
        self.lookback_periods = lookback_periods

    def calculate_rolling_apy(self, daily_returns: List[Decimal]) -> Decimal:
        if not daily_returns:
            return Decimal("0")

        start_idx = -self.lookback_periods
        recent = daily_returns[start_idx:]
        avg_daily = sum(recent) / Decimal(len(recent))
        annualized = avg_daily * Decimal("365")
        return max(Decimal("0"), annualized.quantize(Decimal("0.0001")))
