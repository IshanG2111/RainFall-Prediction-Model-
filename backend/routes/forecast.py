from fastapi import APIRouter, HTTPException
from backend.schemas.request_schema import ForecastRequest
from backend.schemas.forecast_schema import ForecastResponse
from backend.services.forecast_service import generate_forecast

router = APIRouter()

@router.post("/forecast", response_model=ForecastResponse)
def forecast(request: ForecastRequest):
    try:
        result = generate_forecast(request)
        return result

    except ValueError as ve:
        # Controlled validation / business logic errors
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception as e:
        # Unexpected internal errors
        raise HTTPException(status_code=500,detail="Internal server error during forecast generation.",)