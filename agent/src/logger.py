import json
from datetime import datetime, timezone
import os

def log_event(mode: str, level: str, event: str, **kwargs):
    # Ensure mode format
    if not mode.startswith("["):
        mode = f"[{mode.upper()}]"
        
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "level": level,
        "event": event,
    }
    payload.update(kwargs)
    print(json.dumps(payload), flush=True)
