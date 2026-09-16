from decimal import Decimal
from typing import Dict, Any


class FlashLoanDetector:
    """Detects suspicious sudden pool volume spikes and rapid price swings indicating flash loan attacks."""

    def __init__(
        self,
        max_volume_ratio: Decimal = Decimal("3.0"),
        max_price_deviation: Decimal = Decimal("0.08"),
    ) -> None:
        self.max_volume_ratio = max_volume_ratio
        self.max_price_deviation = max_price_deviation

    def inspect_swap(
        self,
        historical_mean_volume: Decimal,
        tx_volume: Decimal,
        pre_price: Decimal,
        post_price: Decimal,
    ) -> Dict[str, Any]:
        if historical_mean_volume <= Decimal("0") or pre_price <= Decimal("0"):
            return {"flagged": False, "reason": None}

        volume_ratio = tx_volume / historical_mean_volume
        price_dev = abs(post_price - pre_price) / pre_price

        is_volume_anomaly = volume_ratio >= self.max_volume_ratio
        is_price_anomaly = price_dev >= self.max_price_deviation

        flagged = is_volume_anomaly and is_price_anomaly
        reason = None
        if flagged:
            reason = f"Flash loan anomaly detected: volume ratio {volume_ratio:.2f}x, price dev {price_dev * 100:.1f}%"

        return {
            "flagged": flagged,
            "volume_ratio": volume_ratio.quantize(Decimal("0.01")),
            "price_deviation": price_dev.quantize(Decimal("0.0001")),
            "reason": reason,
        }
