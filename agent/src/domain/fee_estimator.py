class FeeEstimator:
    def __init__(self, alpha: float = 0.2, base_fee: int = 100):
        self.alpha = alpha
        self.current_ema = float(base_fee)

    def update_fee(self, observed_fee: int) -> float:
        self.current_ema = (self.alpha * observed_fee) + (
            (1.0 - self.alpha) * self.current_ema
        )
        return self.current_ema

    def get_recommended_fee(self) -> int:
        return int(round(self.current_ema))
