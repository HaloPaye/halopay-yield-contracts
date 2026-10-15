from decimal import Decimal, InvalidOperation
from typing import Tuple


class AmmCalculator:
    """Constant product (x * y = k) AMM swap & liquidity calculator.

    Models Soroban constant-product liquidity pools with exact rounding,
    fee deduction, LP share minting/burning, and slippage calculations.
    """

    def __init__(self, fee_fraction: Decimal = Decimal("0.003")) -> None:
        if fee_fraction < Decimal("0") or fee_fraction >= Decimal("1"):
            raise ValueError("fee_fraction must be in [0.0, 1.0)")
        self.fee_fraction = fee_fraction

    def get_amount_out(
        self,
        amount_in: Decimal,
        reserve_in: Decimal,
        reserve_out: Decimal,
    ) -> Decimal:
        """Calculates token output given input and pool reserves."""
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

    def get_amount_in(
        self,
        amount_out: Decimal,
        reserve_in: Decimal,
        reserve_out: Decimal,
    ) -> Decimal:
        """Calculates required input amount for exact output."""
        if (
            amount_out <= Decimal("0")
            or reserve_in <= Decimal("0")
            or reserve_out <= Decimal("0")
            or amount_out >= reserve_out
        ):
            return Decimal("0")

        numerator = reserve_in * amount_out
        denominator = (reserve_out - amount_out) * (
            Decimal("1") - self.fee_fraction
        )
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
        return (amount_in / (reserve_in + amount_in)).quantize(
            Decimal("0.0000001")
        )

    def calculate_lp_mint(
        self,
        deposit_a: Decimal,
        deposit_b: Decimal,
        reserve_a: Decimal,
        reserve_b: Decimal,
        total_shares: Decimal,
    ) -> Decimal:
        """Calculates minted LP shares with initial deposit geometric mean."""
        if deposit_a <= Decimal("0") or deposit_b <= Decimal("0"):
            return Decimal("0")

        if total_shares <= Decimal("0"):
            # Initial deposit: sqrt(A * B) - minimum liquidity lock
            try:
                product = float(deposit_a * deposit_b)
                shares = Decimal(str(product ** 0.5)) - Decimal("1000")
                return max(Decimal("0"), shares.quantize(Decimal("0.0000001")))
            except (OverflowError, InvalidOperation):
                return Decimal("0")

        if reserve_a <= Decimal("0") or reserve_b <= Decimal("0"):
            return Decimal("0")

        share_a = (deposit_a * total_shares) / reserve_a
        share_b = (deposit_b * total_shares) / reserve_b
        return min(share_a, share_b).quantize(Decimal("0.0000001"))

    def calculate_lp_burn(
        self,
        shares_to_burn: Decimal,
        total_shares: Decimal,
        reserve_a: Decimal,
        reserve_b: Decimal,
    ) -> Tuple[Decimal, Decimal]:
        """Calculates reserve amounts returned upon burning LP shares."""
        if (
            shares_to_burn <= Decimal("0")
            or total_shares <= Decimal("0")
            or shares_to_burn > total_shares
        ):
            return Decimal("0"), Decimal("0")

        amount_a = (shares_to_burn * reserve_a) / total_shares
        amount_b = (shares_to_burn * reserve_b) / total_shares
        return (
            amount_a.quantize(Decimal("0.0000001")),
            amount_b.quantize(Decimal("0.0000001")),
        )
