from pydantic import BaseModel, Field
from typing import List

class Coordinates(BaseModel):
    lat: float = Field(..., description="Latitude of selected location")
    lon: float = Field(..., description="Longitude of selected location")


class ForecastDay(BaseModel):
    date: str = Field(..., description="Forecast date (YYYY-MM-DD)")
    rainfall_mm: float = Field(..., description="Predicted rainfall in millimeters")
    status: str = Field(..., description="Rainfall category")


class ForecastResponse(BaseModel):
    location: str = Field(..., description="Selected location name")
    coordinates: Coordinates
    forecast: List[ForecastDay]