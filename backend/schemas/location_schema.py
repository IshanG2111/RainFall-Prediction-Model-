from pydantic import BaseModel

class LocationSuggestion(BaseModel):
    place: str
    lat: float
    lon: float