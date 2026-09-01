# Flash Loan and Pool Manipulation Detector
class FlashLoanDetector:
    def __init__(self, volume_spike_threshold: float = 3.0):
        self.volume_spike_threshold = volume_spike_threshold

    def is_anomalous_pool_state(self, current_reserves: float, average_reserves: float) -> bool:
        if average_reserves <= 0:
            return False
        ratio = current_reserves / average_reserves
        return ratio > self.volume_spike_threshold or ratio < (1.0 / self.volume_spike_threshold)
