import time
from typing import Any, Dict

class TTLCache:
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl = ttl_seconds
        self.store: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str):
        entry = self.store.get(key)

        if not entry:
            return None

        if time.time() > entry["expiry"]:
            del self.store[key]
            return None

        return entry["value"]

    def set(self, key: str, value: Any):
        self.store[key] = {
            "value": value,
            "expiry": time.time() + self.ttl,
        }

    def clear(self):
        self.store.clear()