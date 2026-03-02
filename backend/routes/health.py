from fastapi import APIRouter
from backend.core.dependencies import (get_model,get_grid_df,)

router = APIRouter()

@router.get("/health")
def health_check():
    model_loaded = get_model() is not None
    grid_loaded = get_grid_df() is not None

    return {
        "status": "ok",
        "model_loaded": model_loaded,
        "grid_loaded": grid_loaded,
    }