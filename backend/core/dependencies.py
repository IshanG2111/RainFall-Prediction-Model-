import pickle
import pandas as pd
from typing import Any, Dict
from backend.utils.cache import TTLCache
from backend.core.config import settings

# Cache Singleton
cache_instance = TTLCache(ttl_seconds=settings.CACHE_TTL_SECONDS)


def get_cache() -> TTLCache:
    return cache_instance

# Global Resources
_model = None
_scaler = None
_feature_columns = None
_metrics = None
_grid_df = None
_master_df = None

# Load Model
def load_model_resources():
    global _model, _scaler, _feature_columns, _metrics

    if not settings.MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found at {settings.MODEL_PATH}")

    with open(settings.MODEL_PATH, "rb") as f:
        model_data = pickle.load(f)

    # Support multi-model structure
    if "models" in model_data:
        _model = model_data["models"]["main"]
    else:
        _model = model_data.get("model")

    _scaler = model_data.get("scaler")
    _feature_columns = model_data.get("feature_columns")
    _metrics = model_data.get("metrics", {})

# Load Grid
def load_grid():
    global _grid_df
    if not settings.GRID_PATH.exists():
        raise FileNotFoundError(f"Grid file not found at {settings.GRID_PATH}")
    _grid_df = pd.read_parquet(settings.GRID_PATH)

# Load Master Dataset
def load_master_dataset():
    global _master_df
    if settings.MASTER_DATA_PATH.exists():
        _master_df = pd.read_parquet(settings.MASTER_DATA_PATH)
    else:
        _master_df = None

# Initialize All Resources
def initialize_resources():
    load_model_resources()
    load_grid()
    load_master_dataset()
    print("All backend resources initialized successfully.")

# Getter Functions
def get_model():
    return _model


def get_scaler():
    return _scaler


def get_feature_columns():
    return _feature_columns


def get_metrics() -> Dict[str, Any]:
    return _metrics


def get_grid_df():
    return _grid_df


def get_master_df():
    return _master_df