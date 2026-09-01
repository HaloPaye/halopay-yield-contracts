# Optimized Transaction Retry Queue with Exponential Backoff
import time

class TransactionRetryQueue:
    def __init__(self, max_retries: int = 5, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay

    def get_backoff_delay(self, attempt: int) -> float:
        return min(30.0, self.base_delay * (2 ** attempt))
