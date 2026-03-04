from fastapi import APIRouter
from backend.core.dependencies import (get_model,get_scaler,get_feature_columns,get_grid_df)

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    model_loaded = get_model() is not None
    scaler_loaded = get_scaler() is not None
    features_loaded = get_feature_columns() is not None
    grid_loaded = get_grid_df() is not None

    return {
        "status": "ok",
        "model_loaded": model_loaded,
        "scaler_loaded": scaler_loaded,
        "features_loaded": features_loaded,
        "grid_loaded": grid_loaded,
    }
