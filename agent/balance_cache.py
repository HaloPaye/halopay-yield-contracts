# High Performance User Balance Cache
import time

class BalanceCache:
    def __init__(self, ttl_seconds: int = 15):
        self.ttl = ttl_seconds
        self.store = {}

    def set_balance(self, user_address: str, balance: float):
        self.store[user_address] = (balance, time.time())

    def get_balance(self, user_address: str) -> float | None:
        if user_address in self.store:
            val, ts = self.store[user_address]
            if time.time() - ts < self.ttl:
                return val
        return None
