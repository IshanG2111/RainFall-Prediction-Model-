from fastapi import Depends
from opencage.geocoder import OpenCageGeocode
from backend.core.config import settings
from backend.utils.cache import TTLCache

def get_geocoder() -> OpenCageGeocode:
    if not settings.OPENCAGE_API_KEY:
        raise RuntimeError("OpenCage API key not configured.")
    return OpenCageGeocode(settings.OPENCAGE_API_KEY)

# Singleton cache instance
cache_instance = TTLCache(ttl_seconds=settings.CACHE_TTL_SECONDS)

def get_cache() -> TTLCache:
    return cache_instance