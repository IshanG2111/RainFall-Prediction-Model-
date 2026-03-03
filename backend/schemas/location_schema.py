from pydantic import BaseModel

class LocationSuggestion(BaseModel): # This is the schema for the location suggestions returned by the API
    place: str
    lat: float
    lon: float