import time
from typing import Any, Dict
from threading import Lock

class TTLCache:
    def __init__(self, ttl_seconds: int = 3600, max_size: int = 1000):
        self.ttl = ttl_seconds
        self.max_size = max_size
        self.store: Dict[str, Dict[str, Any]] = {}
        self.lock = Lock()

    def get(self, key: str):
        with self.lock:
            entry = self.store.get(key)

            if not entry:
                return None

            # Check expiration
            if time.time() > entry["expiry"]:
                del self.store[key]
                return None

            return entry["value"]

    def set(self, key: str, value: Any):
        with self.lock:
            # Evict oldest if max size exceeded
            if len(self.store) >= self.max_size:
                oldest_key = next(iter(self.store))
                del self.store[oldest_key]

            self.store[key] = {
                "value": value,
                "expiry": time.time() + self.ttl,
            }

    def clear(self):
        with self.lock:
            self.store.clear()

    def size(self) -> int:
        with self.lock:
            return len(self.store)