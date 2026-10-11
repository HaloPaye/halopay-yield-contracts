from decimal import Decimal
import pytest
from src.domain.slippage import DynamicSlippageCalculator, calculate_slippage


def test_legacy_calculate_slippage_positive() -> None:
    # 100 / 2000 = 0.05
    assert calculate_slippage(2000.0) == pytest.approx(0.05)
    # 100 / 10000 = 0.01
    assert calculate_slippage(10000.0) == pytest.approx(0.01)
    # 100 / 20000 = 0.005, clamped to min 0.01
    assert calculate_slippage(20000.0) == pytest.approx(0.01)


def test_legacy_calculate_slippage_zero_and_negative() -> None:
    assert calculate_slippage(0.0) == 0.05
    assert calculate_slippage(-50.0) == 0.05


def test_calculator_initialization_valid() -> None:
    calc = DynamicSlippageCalculator(
        min_slippage=Decimal("0.002"),
        max_slippage=Decimal("0.08"),
    )
    assert calc.min_slippage == Decimal("0.002")
    assert calc.max_slippage == Decimal("0.08")


def test_calculator_initialization_invalid_bounds() -> None:
    with pytest.raises(ValueError, match="Invalid slippage bounds"):
        DynamicSlippageCalculator(min_slippage=Decimal("-0.01"))

    with pytest.raises(ValueError, match="Invalid slippage bounds"):
        DynamicSlippageCalculator(
            min_slippage=Decimal("0.05"),
            max_slippage=Decimal("0.01"),
        )


def test_compute_slippage_normal_conditions() -> None:
    calc = DynamicSlippageCalculator(
        min_slippage=Decimal("0.005"),
        max_slippage=Decimal("0.10"),
    )
    # 500 / 50000 = 0.01
    slippage = calc.compute_slippage(trade_amount=500, pool_liquidity=50000)
    assert slippage == Decimal("0.01")


def test_compute_slippage_clamped_to_min() -> None:
    calc = DynamicSlippageCalculator(
        min_slippage=Decimal("0.005"),
        max_slippage=Decimal("0.10"),
    )
    # 10 / 100000 = 0.0001 < min_slippage
    slippage = calc.compute_slippage(trade_amount=10, pool_liquidity=100000)
    assert slippage == Decimal("0.005")


def test_compute_slippage_clamped_to_max() -> None:
    calc = DynamicSlippageCalculator(
        min_slippage=Decimal("0.005"),
        max_slippage=Decimal("0.05"),
    )
    # 20000 / 100000 = 0.20 > max_slippage
    slippage = calc.compute_slippage(trade_amount=20000, pool_liquidity=100000)
    assert slippage == Decimal("0.05")


def test_compute_slippage_with_volatility() -> None:
    calc = DynamicSlippageCalculator(
        min_slippage=Decimal("0.005"),
        max_slippage=Decimal("0.10"),
    )
    # (1000 / 100000) * 1.5 = 0.015
    slippage = calc.compute_slippage(
        trade_amount=1000,
        pool_liquidity=100000,
        volatility_multiplier=Decimal("1.5"),
    )
    assert slippage == Decimal("0.015")


def test_compute_slippage_invalid_inputs_fallback() -> None:
    calc = DynamicSlippageCalculator(
        min_slippage=Decimal("0.005"),
        max_slippage=Decimal("0.05"),
    )
    assert calc.compute_slippage(0, 1000) == Decimal("0.05")
    assert calc.compute_slippage(100, 0) == Decimal("0.05")
    assert calc.compute_slippage(-10, 1000) == Decimal("0.05")
    assert calc.compute_slippage(100, -1000) == Decimal("0.05")
    assert (
        calc.compute_slippage(100, 1000, volatility_multiplier=0)
        == Decimal("0.05")
    )


def test_is_slippage_acceptable() -> None:
    calc = DynamicSlippageCalculator()
    # 1% slippage with 2% tolerance -> True
    assert calc.is_slippage_acceptable(
        expected_price=Decimal("100"),
        executed_price=Decimal("99"),
        allowed_slippage=Decimal("0.02"),
    )
    # 3% slippage with 2% tolerance -> False
    assert not calc.is_slippage_acceptable(
        expected_price=Decimal("100"),
        executed_price=Decimal("97"),
        allowed_slippage=Decimal("0.02"),
    )
    # Exact boundary -> True
    assert calc.is_slippage_acceptable(
        expected_price=Decimal("100"),
        executed_price=Decimal("98"),
        allowed_slippage=Decimal("0.02"),
    )


def test_is_slippage_acceptable_invalid_prices() -> None:
    calc = DynamicSlippageCalculator()
    assert not calc.is_slippage_acceptable(0, 100, Decimal("0.05"))
    assert not calc.is_slippage_acceptable(100, 0, Decimal("0.05"))
    assert not calc.is_slippage_acceptable(-50, 100, Decimal("0.05"))
    assert not calc.is_slippage_acceptable(100, -50, Decimal("0.05"))
    assert not calc.is_slippage_acceptable(100, 100, Decimal("-0.01"))
