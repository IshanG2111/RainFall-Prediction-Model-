from pydantic import BaseModel, Field, field_validator
from datetime import date as DateType

class ForecastRequest(BaseModel):
    location: str = Field(...,min_length=3,max_length=200,description="Full formatted location name selected from autocomplete")

    lat: float = Field(...,ge=-90,le=90,description="Latitude of selected location")

    lon: float = Field(...,ge=-180,le=180,description="Longitude of selected location")

    date: DateType = Field(...,description="Selected start date in YYYY-MM-DD format")

    @field_validator("location")
    @classmethod
    def validate_location(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Location cannot be empty")
        return value.strip()