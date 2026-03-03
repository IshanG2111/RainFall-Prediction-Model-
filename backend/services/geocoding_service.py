import requests
import logging
from typing import List, Dict
from backend.core.config import settings
from backend.utils.cache import TTLCache

logger = logging.getLogger(__name__)

class GeocodingService:
    BASE_URL = "https://api.geoapify.com/v1/geocode/autocomplete"

    def __init__(self, cache: TTLCache):
        self.cache = cache

    def search_locations(self, query: str) -> List[Dict]:
        query = query.strip().lower()

        # Check cache
        cached = self.cache.get(query)
        if cached:
            return cached

        # Validate API key
        if not settings.GEOAPIFY_API_KEY:
            raise ValueError("Geocoding API key not configured")

        params = {
            "text": query,
            "limit": settings.DEFAULT_LIMIT,
            "filter": f"countrycode:{settings.COUNTRY_CODE}",
            "lang": "en",
            "apiKey": settings.GEOAPIFY_API_KEY,
        }

        response = requests.get(
            self.BASE_URL,
            params=params,
            timeout=settings.REQUEST_TIMEOUT,
        )
        response.raise_for_status()

        data = response.json()
        features = data.get("features", [])

        formatted_results = []

        for feature in features:
            properties = feature.get("properties", {})

            if properties.get("formatted") and properties.get("lat") is not None and properties.get("lon") is not None:
                formatted_results.append({
                    "place": properties.get("formatted"),
                    "lat": properties.get("lat"),
                    "lon": properties.get("lon"),
                })

        self.cache.set(query, formatted_results)

        return formatted_results