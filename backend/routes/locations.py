from fastapi import APIRouter, Query, Depends, HTTPException
from typing import List
from backend.schemas.location_schema import LocationSuggestion
from backend.core.dependencies import get_cache
from backend.services.geocoding_service import GeocodingService
from backend.core.config import settings

router = APIRouter(prefix="/api", tags=["Locations"])


@router.get("/locations", response_model=List[LocationSuggestion])
def get_location_suggestions(
    q: str = Query(..., description="Search query for location"),
    cache=Depends(get_cache),
):
    # Validate minimum query length
    if len(q.strip()) < settings.MIN_QUERY_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Query must be at least {settings.MIN_QUERY_LENGTH} characters.",
        )

    service = GeocodingService(cache)

    return service.search_locations(q)