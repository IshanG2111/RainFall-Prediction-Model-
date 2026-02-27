import time
from typing import Any, Dict

class TTLCache:
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl = ttl_seconds #Time to live in seconds
        self.store: Dict[str, Dict[str, Any]] = {} #Dictionary to store cache entries, where each entry contains the value and expiry time

    def get(self, key: str):
        entry = self.store.get(key) #Retrieve the cache entry for the given key

        if not entry:
            return None

        if time.time() > entry["expiry"]: #Check if the current time has exceeded the expiry time of the cache entry
            del self.store[key]
            return None

        return entry["value"]

    def set(self, key: str, value: Any): #Set a cache entry and calculate its expiry time
        self.store[key] = {
            "value": value,
            "expiry": time.time() + self.ttl,
        }

    def clear(self):
        self.store.clear() #Clear all cache entries