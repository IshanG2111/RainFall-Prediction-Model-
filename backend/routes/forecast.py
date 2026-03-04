import logging
from fastapi import APIRouter, HTTPException, Request
from backend.schemas.request_schema import ForecastRequest
from backend.schemas.forecast_schema import ForecastResponse
from backend.services.forecast_service import generate_forecast
from backend.core.rate_limiter import limiter

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Forecast"])

@router.post("/forecast", response_model=ForecastResponse)
@limiter.limit("5/minute")
def forecast(request: Request, body: ForecastRequest):
    try:
        result = generate_forecast(body)
        return result

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception:
        logger.exception("Forecast error")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during forecast generation.",
        )
