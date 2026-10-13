from enum import Enum
from typing import Dict, List, Optional


class PriorityLevel(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class FeeEstimator:
    """Hardened Gas and Fee Estimation Engine for Stellar transactions.

    Protects against fee manipulation, artificial surge spikes, and bounded
    resource consumption.
    """

    def __init__(
        self,
        alpha: float = 0.2,
        base_fee: int = 100,
        min_fee: int = 100,
        max_fee: int = 50_000,
        max_surge_ratio: float = 3.0,
    ) -> None:
        if not (0.0 < alpha <= 1.0):
            raise ValueError("alpha must be within (0.0, 1.0]")
        if min_fee < 0 or max_fee < min_fee:
            raise ValueError("Invalid min_fee or max_fee bounds")
        if base_fee < min_fee or base_fee > max_fee:
            raise ValueError("base_fee must be within [min_fee, max_fee]")

        self.alpha = float(alpha)
        self.base_fee = int(base_fee)
        self.min_fee = int(min_fee)
        self.max_fee = int(max_fee)
        self.max_surge_ratio = float(max_surge_ratio)
        self.current_ema = float(base_fee)
        self.history: List[int] = []
        self.spike_detected: bool = False

    def update_fee(self, observed_fee: int) -> float:
        """Updates exponential moving average with strict outlier clamping.

        Args:
            observed_fee: Raw observed fee from ledger or network telemetry.

        Returns:
            Updated float EMA fee.
        """
        if observed_fee < 0:
            raise ValueError("observed_fee cannot be negative")

        # Cap observed fee against ceiling and surge factor
        surge_limit = self.current_ema * self.max_surge_ratio
        effective_cap = min(
            float(self.max_fee), max(surge_limit, float(self.min_fee))
        )

        if observed_fee > effective_cap:
            self.spike_detected = True
            clamped_fee = effective_cap
        else:
            self.spike_detected = False
            clamped_fee = max(float(self.min_fee), float(observed_fee))

        self.current_ema = (self.alpha * clamped_fee) + (
            (1.0 - self.alpha) * self.current_ema
        )

        self.history.append(int(clamped_fee))
        if len(self.history) > 100:
            self.history.pop(0)

        return self.current_ema

    def get_recommended_fee(
        self, priority: PriorityLevel = PriorityLevel.LOW
    ) -> int:
        """Calculates recommended fee scaled by transaction urgency level.

        Args:
            priority: PriorityLevel determining safety headroom.

        Returns:
            Integer fee recommendation clamped between min_fee and max_fee.
        """
        multipliers: Dict[PriorityLevel, float] = {
            PriorityLevel.LOW: 1.0,
            PriorityLevel.NORMAL: 1.1,
            PriorityLevel.HIGH: 1.5,
            PriorityLevel.CRITICAL: 2.0,
        }
        mult = multipliers.get(priority, 1.0)
        fee = int(round(self.current_ema * mult))
        return max(self.min_fee, min(self.max_fee, fee))

    def reset(self, new_base_fee: Optional[int] = None) -> None:
        """Resets the state to the base fee or provided value."""
        target = new_base_fee if new_base_fee is not None else self.base_fee
        if target < self.min_fee or target > self.max_fee:
            raise ValueError("Reset fee out of bounds")
        self.current_ema = float(target)
        self.history.clear()
        self.spike_detected = False
