import logging
import requests
from fastapi import APIRouter, Query, Depends, HTTPException, Request
from typing import List
from backend.schemas.location_schema import LocationSuggestion
from backend.core.dependencies import get_cache
from backend.services.geocoding_service import GeocodingService
from backend.core.config import settings
from backend.core.rate_limiter import limiter

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Locations"])

@router.get("/locations", response_model=List[LocationSuggestion])
@limiter.limit("15/minute")
def get_location_suggestions(
    request: Request,
    q: str = Query(..., description="Search query for location"),
    cache=Depends(get_cache),
):
    q = q.strip()

    if len(q) < settings.MIN_QUERY_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Query must be at least {settings.MIN_QUERY_LENGTH} characters.",
        )

    normalized_query = q.lower()
    service = GeocodingService(cache)

    try:
        return service.search_locations(normalized_query)

    except requests.RequestException:
        logger.exception("Geocoding service failed")
        raise HTTPException(
            status_code=502,
            detail="Geocoding service unavailable",
        )