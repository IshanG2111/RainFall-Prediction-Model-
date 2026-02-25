from backend.utils.cache import TTLCache
from backend.core.config import settings

# Singleton cache instance
cache_instance = TTLCache(ttl_seconds=settings.CACHE_TTL_SECONDS)

def get_cache() -> TTLCache:
    return cache_instance