from decimal import Decimal
import pytest
from src.domain.amm_calculator import AmmCalculator


def test_amm_calculator_init_validation() -> None:
    with pytest.raises(ValueError, match="fee_fraction must be in"):
        AmmCalculator(fee_fraction=Decimal("-0.01"))

    with pytest.raises(ValueError, match="fee_fraction must be in"):
        AmmCalculator(fee_fraction=Decimal("1.0"))


def test_amm_calculator_get_amount_in_edge_cases() -> None:
    calc = AmmCalculator(fee_fraction=Decimal("0.003"))
    reserve_in = Decimal("10000")
    reserve_out = Decimal("20000")

    # Impossible swap: requesting more than reserves
    assert calc.get_amount_in(
        Decimal("25000"), reserve_in, reserve_out
    ) == Decimal("0")
    assert calc.get_amount_in(
        Decimal("20000"), reserve_in, reserve_out
    ) == Decimal("0")

    # Zero or negative inputs
    assert calc.get_amount_in(
        Decimal("0"), reserve_in, reserve_out
    ) == Decimal("0")
    assert calc.get_amount_in(
        Decimal("-100"), reserve_in, reserve_out
    ) == Decimal("0")

    # Valid exact output calculation
    amount_in = calc.get_amount_in(Decimal("1000"), reserve_in, reserve_out)
    assert amount_in > Decimal("0")
    # Verify symmetry with get_amount_out
    amount_out = calc.get_amount_out(amount_in, reserve_in, reserve_out)
    assert abs(amount_out - Decimal("1000")) < Decimal("0.01")


def test_amm_calculator_lp_mint_and_burn() -> None:
    calc = AmmCalculator()

    # Initial deposit minting
    shares = calc.calculate_lp_mint(
        deposit_a=Decimal("10000"),
        deposit_b=Decimal("10000"),
        reserve_a=Decimal("0"),
        reserve_b=Decimal("0"),
        total_shares=Decimal("0"),
    )
    # sqrt(10000 * 10000) - 1000 = 10000 - 1000 = 9000
    assert shares == Decimal("9000.0000000")

    # Subsequent deposit
    subsequent_shares = calc.calculate_lp_mint(
        deposit_a=Decimal("1000"),
        deposit_b=Decimal("1000"),
        reserve_a=Decimal("10000"),
        reserve_b=Decimal("10000"),
        total_shares=Decimal("9000"),
    )
    # min(1000*9000/10000, 1000*9000/10000) = 900
    assert subsequent_shares == Decimal("900.0000000")

    # Burning shares
    burned_a, burned_b = calc.calculate_lp_burn(
        shares_to_burn=Decimal("900"),
        total_shares=Decimal("9900"),
        reserve_a=Decimal("11000"),
        reserve_b=Decimal("11000"),
    )
    assert burned_a == Decimal("1000.0000000")
    assert burned_b == Decimal("1000.0000000")
