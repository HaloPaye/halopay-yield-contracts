from typing import Optional, Any, Dict


class HorizonStreamWatcher:
    """Manages Horizon Server-Sent Events (SSE) streaming with exponential backoff."""

    def __init__(
        self,
        endpoint: str,
        initial_backoff_sec: float = 1.0,
        max_backoff_sec: float = 30.0,
        backoff_multiplier: float = 2.0,
    ) -> None:
        self.endpoint = endpoint
        self.initial_backoff_sec = initial_backoff_sec
        self.max_backoff_sec = max_backoff_sec
        self.backoff_multiplier = backoff_multiplier
        self.current_backoff = initial_backoff_sec
        self.retry_count = 0
        self.is_connected = False

    def on_connect(self) -> None:
        self.is_connected = True
        self.retry_count = 0
        self.current_backoff = self.initial_backoff_sec

    def on_disconnect(self) -> float:
        self.is_connected = False
        self.retry_count += 1
        delay = self.current_backoff
        self.current_backoff = min(
            self.max_backoff_sec, self.current_backoff * self.backoff_multiplier
        )
        return delay

    def parse_event(self, raw_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not isinstance(raw_data, dict):
            return None
        return {
            "id": raw_data.get("id"),
            "paging_token": raw_data.get("paging_token"),
            "type": raw_data.get("type", "payment"),
            "successful": raw_data.get("successful", True),
        }
