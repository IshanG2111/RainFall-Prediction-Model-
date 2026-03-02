from datetime import datetime
from backend.services.date_service import generate_7_day_forecast
from backend.services.grid_service import get_nearest_grid
from backend.services.model_service import predict_single_day

def _categorize_rainfall(rainfall: float) -> str:
    if rainfall < 0.1:
        return "No Rain"
    elif rainfall < 2.5:
        return "Light Rain"
    elif rainfall < 15:
        return "Moderate Rain"
    else:
        return "Heavy Rain"

def generate_forecast(request):
    # Grid mapping
    grid_info = get_nearest_grid(request.lat, request.lon)

    grid_id = grid_info["grid_id"]
    center_lat = grid_info["center_lat"]
    center_lon = grid_info["center_lon"]

    # Generate 7-day dates
    date_array = generate_7_day_forecast(request.date)

    forecast_list = []

    for date_obj in date_array:
        rainfall = predict_single_day(
            grid_id=grid_id,
            center_lat=center_lat,
            center_lon=center_lon,
            date_target=date_obj,
        )

        forecast_list.append({
            "date": date_obj.strftime("%Y-%m-%d"),
            "rainfall_mm": rainfall,
            "status": _categorize_rainfall(rainfall),
        })

    return {
        "location": request.location,
        "coordinates": {"lat": request.lat,"lon": request.lon},
        "forecast": forecast_list,
    }