from decimal import Decimal
from typing import Union


def calculate_slippage(volume: float) -> float:
    """Legacy function to calculate slippage based on volume."""
    return max(0.01, 100 / volume if volume > 0 else 0.05)


class DynamicSlippageCalculator:
    """Calculates dynamic slippage bounds and tolerance based on pool volume,
    trade size, and market volatility.
    """

    def __init__(
        self,
        min_slippage: Decimal = Decimal("0.001"),
        max_slippage: Decimal = Decimal("0.05"),
        base_impact_factor: Decimal = Decimal("100"),
    ) -> None:
        if min_slippage < Decimal("0") or max_slippage < min_slippage:
            raise ValueError("Invalid slippage bounds")
        self.min_slippage = min_slippage
        self.max_slippage = max_slippage
        self.base_impact_factor = base_impact_factor

    def compute_slippage(
        self,
        trade_amount: Union[Decimal, float, int],
        pool_liquidity: Union[Decimal, float, int],
        volatility_multiplier: Union[Decimal, float, int] = Decimal("1.0"),
    ) -> Decimal:
        trade_dec = Decimal(str(trade_amount))
        pool_dec = Decimal(str(pool_liquidity))
        vol_dec = Decimal(str(volatility_multiplier))

        if (
            trade_dec <= Decimal("0")
            or pool_dec <= Decimal("0")
            or vol_dec <= Decimal("0")
        ):
            return self.max_slippage

        # Price impact is proportional to trade size relative to pool liquidity
        impact = (trade_dec / pool_dec) * vol_dec
        clamped_impact = min(self.max_slippage, impact)
        return max(self.min_slippage, clamped_impact)

    def is_slippage_acceptable(
        self,
        expected_price: Union[Decimal, float, int],
        executed_price: Union[Decimal, float, int],
        allowed_slippage: Union[Decimal, float, int],
    ) -> bool:
        exp_p = Decimal(str(expected_price))
        exec_p = Decimal(str(executed_price))
        allow_s = Decimal(str(allowed_slippage))

        if (
            exp_p <= Decimal("0")
            or exec_p <= Decimal("0")
            or allow_s < Decimal("0")
        ):
            return False

        slippage = abs(exp_p - exec_p) / exp_p
        return slippage <= allow_s
