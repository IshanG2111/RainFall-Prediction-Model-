from typing import List, Dict
from opencage.geocoder import OpenCageGeocode
from opencage.geocoder import RateLimitExceededError, NotAuthorizedError
from backend.core.config import settings
from backend.utils.cache import TTLCache

class GeocodingService:
    def __init__(self, geocoder: OpenCageGeocode, cache: TTLCache):
        self.geocoder = geocoder
        self.cache = cache

    def search_locations(self, query: str) -> List[Dict]:
        query = query.strip()

        # Check cache first
        cached = self.cache.get(query.lower())
        if cached:
            return cached

        try:
            results = self.geocoder.geocode(
                query,
                limit=settings.DEFAULT_LIMIT,
                countrycode=settings.COUNTRY_CODE,
                no_annotations=1,
                language="en",
            )
        except RateLimitExceededError:
            raise Exception("OpenCage rate limit exceeded.")
        except NotAuthorizedError:
            raise Exception("Invalid OpenCage API key.")
        except Exception as e:
            raise Exception(f"Geocoding error: {str(e)}")

        formatted_results = []

        for result in results:
            if "geometry" not in result:
                continue

            formatted_results.append(
                {
                    "place": result.get("formatted"),
                    "lat": result["geometry"]["lat"],
                    "lon": result["geometry"]["lng"],
                }
            )

        # Store in cache
        self.cache.set(query.lower(), formatted_results)

        return formatted_results