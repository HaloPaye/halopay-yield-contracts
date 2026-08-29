def calculate_slippage(volume: float) -> float:
    return max(0.01, 100 / volume if volume > 0 else 0.05)
