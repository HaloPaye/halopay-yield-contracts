from decimal import Decimal


class AmmCalculator:
    """Constant product (x * y = k) AMM swap calculator with fee modeling."""

    def __init__(self, fee_fraction: Decimal = Decimal("0.003")) -> None:
        self.fee_fraction = fee_fraction

    def get_amount_out(
        self,
        amount_in: Decimal,
        reserve_in: Decimal,
        reserve_out: Decimal,
    ) -> Decimal:
        if (
            amount_in <= Decimal("0")
            or reserve_in <= Decimal("0")
            or reserve_out <= Decimal("0")
        ):
            return Decimal("0")

        amount_in_with_fee = amount_in * (Decimal("1") - self.fee_fraction)
        numerator = amount_in_with_fee * reserve_out
        denominator = reserve_in + amount_in_with_fee
        if denominator <= Decimal("0"):
            return Decimal("0")
        return (numerator / denominator).quantize(Decimal("0.0000001"))

    def calculate_price_impact(
        self,
        amount_in: Decimal,
        reserve_in: Decimal,
    ) -> Decimal:
        """Calculates expected price impact fraction."""
        if reserve_in <= Decimal("0") or amount_in <= Decimal("0"):
            return Decimal("1.0")
        return (amount_in / (reserve_in + amount_in)).quantize(Decimal("0.0000001"))
