from decimal import Decimal


class SlippageGuard:
    def __init__(
        self,
        max_allowed_slippage: Decimal = Decimal("0.05"),
        base_slippage: Decimal = Decimal("0.005"),
    ) -> None:
        self.max_allowed_slippage = max_allowed_slippage
        self.base_slippage = base_slippage

    def evaluate_order_slippage(
        self,
        expected_price: Decimal,
        executed_price: Decimal,
    ) -> bool:
        if expected_price <= Decimal("0") or executed_price <= Decimal("0"):
            return False

        slippage = abs(expected_price - executed_price) / expected_price
        return slippage <= self.max_allowed_slippage
