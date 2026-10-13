from decimal import Decimal, InvalidOperation
from typing import List, Optional, Tuple, Union


class ApyAggregator:
    """Hardened APY and Yield Scraping Aggregator.

    Provides statistical sanitization, winsorization, flash-loan outlier
    clamping, and compound APY calculations for DeFi yield monitoring.
    """

    def __init__(
        self,
        lookback_periods: int = 7,
        max_allowed_apy: Decimal = Decimal("5.0"),  # 500% APY ceiling
        max_daily_return: Decimal = Decimal("0.10"),  # 10% return ceiling
        min_daily_return: Decimal = Decimal("-0.50"),  # -50% loss floor
    ) -> None:
        if lookback_periods <= 0:
            raise ValueError("lookback_periods must be greater than 0")
        if max_allowed_apy <= Decimal("0"):
            raise ValueError("max_allowed_apy must be positive")
        if min_daily_return >= max_daily_return:
            raise ValueError(
                "min_daily_return must be less than max_daily_return"
            )

        self.lookback_periods = lookback_periods
        self.max_allowed_apy = max_allowed_apy
        self.max_daily_return = max_daily_return
        self.min_daily_return = min_daily_return
        self.anomaly_detected: bool = False

    def sanitize_return(
        self, raw_return: Union[Decimal, float, int, str]
    ) -> Optional[Decimal]:
        """Validates and parses return value, filtering out invalid values."""
        try:
            val = Decimal(str(raw_return))
            if val.is_nan() or val.is_infinite():
                return None
            return val
        except (InvalidOperation, TypeError, ValueError):
            return None

    def calculate_rolling_apy(
        self,
        daily_returns: List[Union[Decimal, float, int, str]],
        compound: bool = False,
    ) -> Decimal:
        """Calculates rolling annualized yield with outlier rejection.

        Args:
            daily_returns: List of daily returns over time.
            compound: If True, uses compound interest formula (1 + r)^365 - 1.

        Returns:
            Sanitized APY as Decimal quantized to 4 decimal places.
        """
        if not daily_returns:
            return Decimal("0")

        sanitized: List[Decimal] = []
        self.anomaly_detected = False

        for r in daily_returns:
            parsed = self.sanitize_return(r)
            if parsed is None:
                continue

            # Check for extreme manipulation spikes (e.g. flash loan attacks)
            if parsed > self.max_daily_return:
                self.anomaly_detected = True
                parsed = self.max_daily_return
            elif parsed < self.min_daily_return:
                self.anomaly_detected = True
                parsed = self.min_daily_return

            sanitized.append(parsed)

        if not sanitized:
            return Decimal("0")

        recent = sanitized[-self.lookback_periods:]
        count = Decimal(len(recent))
        avg_daily = sum(recent) / count

        if avg_daily <= Decimal("0"):
            return Decimal("0.0000")

        if compound:
            # (1 + avg_daily)^365 - 1 with overflow protection
            try:
                base = Decimal("1") + avg_daily
                annualized = (base ** 365) - Decimal("1")
            except (OverflowError, InvalidOperation):
                annualized = self.max_allowed_apy
        else:
            annualized = avg_daily * Decimal("365")

        clamped = min(self.max_allowed_apy, max(Decimal("0"), annualized))
        return clamped.quantize(Decimal("0.0001"))

    def compute_summary_stats(
        self, daily_returns: List[Union[Decimal, float, int, str]]
    ) -> Tuple[Decimal, Decimal, bool]:
        """Returns tuple of (rolling_apy, volatility_stddev, is_anomaly)."""
        apy = self.calculate_rolling_apy(daily_returns)
        sanitized = [
            self.sanitize_return(r)
            for r in daily_returns
            if self.sanitize_return(r) is not None
        ]
        if len(sanitized) < 2:
            return apy, Decimal("0.0000"), self.anomaly_detected

        mean = sum(sanitized) / Decimal(len(sanitized))
        variance = sum((x - mean) ** 2 for x in sanitized) / Decimal(
            len(sanitized) - 1
        )
        stddev_val = float(variance) ** 0.5
        stddev = Decimal(str(stddev_val)).quantize(Decimal("0.0001"))
        return apy, stddev, self.anomaly_detected
