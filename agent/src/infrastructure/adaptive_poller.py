class AdaptivePoller:
    def __init__(
        self,
        min_interval_sec: float = 2.0,
        max_interval_sec: float = 60.0,
        backoff_factor: float = 1.5,
    ):
        self.min_interval_sec = min_interval_sec
        self.max_interval_sec = max_interval_sec
        self.backoff_factor = backoff_factor
        self.current_interval = min_interval_sec

    def on_activity(self) -> float:
        self.current_interval = self.min_interval_sec
        return self.current_interval

    def on_idle(self) -> float:
        self.current_interval = min(
            self.max_interval_sec, self.current_interval * self.backoff_factor
        )
        return self.current_interval
