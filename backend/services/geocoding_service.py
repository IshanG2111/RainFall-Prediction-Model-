import requests
from typing import List, Dict
from backend.core.config import settings
from backend.utils.cache import TTLCache

class GeocodingService:
    BASE_URL = "https://api.geoapify.com/v1/geocode/autocomplete"

    def __init__(self, cache: TTLCache):
        self.cache = cache #Initialize the cache for geocoding results

    def search_locations(self, query: str) -> List[Dict]: #Search for locations based on the query string
        query = query.strip()

        cached = self.cache.get(query.lower()) #Check if the query result is already cached, if so return the cached result
        if cached:
            return cached

        params = {
            "text": query,
            "limit": settings.DEFAULT_LIMIT,
            "filter": f"countrycode:{settings.COUNTRY_CODE}",
            "lang": "en",
            "apiKey": settings.GEOAPIFY_API_KEY,
        } #Prepare the parameters for the API request.

        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status() #Check if the API request was successful, if not raise an exception.

        data = response.json()

        features = data.get("features", []) #Extract the relevant information from the API response and format it for the frontend.

        formatted_results = []

        for feature in features:
            properties = feature.get("properties", {}) #Extract the properties of each feature.

            formatted_results.append({
                "place": properties.get("formatted"),
                "lat": properties.get("lat"),
                "lon": properties.get("lon"),
            })

        self.cache.set(query.lower(), formatted_results) #Cache the results for future queries to improve performance.

        return formatted_results