import requests
from typing import List, Dict
from backend.core.config import settings
from backend.utils.cache import TTLCache

class GeocodingService:
    BASE_URL = "https://api.geoapify.com/v1/geocode/autocomplete"

    def __init__(self, cache: TTLCache):
        self.cache = cache

    def search_locations(self, query: str) -> List[Dict]:
        query = query.strip()

        cached = self.cache.get(query.lower())
        if cached:
            return cached

        params = {
            "text": query,
            "limit": settings.DEFAULT_LIMIT,
            "filter": f"countrycode:{settings.COUNTRY_CODE}",
            "lang": "en",
            "apiKey": settings.GEOAPIFY_API_KEY,
        }

        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()

        data = response.json()

        features = data.get("features", [])

        formatted_results = []

        for feature in features:
            properties = feature.get("properties", {})

            formatted_results.append({
                "place": properties.get("formatted"),
                "lat": properties.get("lat"),
                "lon": properties.get("lon"),
            })

        self.cache.set(query.lower(), formatted_results)

        return formatted_results