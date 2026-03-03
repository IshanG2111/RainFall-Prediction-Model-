import pickle
import logging
import pandas as pd
from typing import Any, Dict
from backend.utils.cache import TTLCache
from backend.core.config import settings

# Logging
logger = logging.getLogger(__name__)

# Cache Singleton
cache_instance = TTLCache(ttl_seconds=settings.CACHE_TTL_SECONDS)

def get_cache() -> TTLCache:
    return cache_instance

# App Resources Container
class AppResources:
    model = None
    scaler = None
    feature_columns = None
    metrics = None
    grid_df = None
    master_df = None

# Load Model
def load_model_resources():
    logger.info("Loading ML model...")

    if not settings.MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found at {settings.MODEL_PATH}")

    with open(settings.MODEL_PATH, "rb") as f:
        model_data = pickle.load(f)

    # Support multi-model structure
    if "models" in model_data:
        AppResources.model = model_data["models"]["main"]
    else:
        AppResources.model = model_data.get("model")

    AppResources.scaler = model_data.get("scaler")
    AppResources.feature_columns = model_data.get("feature_columns")
    AppResources.metrics = model_data.get("metrics", {})

    # Validate critical components
    if AppResources.model is None:
        raise ValueError("Model missing in model file")

    if AppResources.feature_columns is None:
        raise ValueError("Feature columns missing in model file")

    logger.info("Model loaded successfully.")

# Load Grid
def load_grid():
    logger.info("Loading grid data...")

    if not settings.GRID_PATH.exists():
        raise FileNotFoundError(f"Grid file not found at {settings.GRID_PATH}")

    AppResources.grid_df = pd.read_parquet(settings.GRID_PATH)

    if AppResources.grid_df.empty:
        raise ValueError("Grid dataset is empty")

    logger.info("Grid loaded successfully.")

# Load Master Dataset
def load_master_dataset():
    logger.info("Loading master dataset...")

    if settings.MASTER_DATA_PATH.exists():
        AppResources.master_df = pd.read_parquet(settings.MASTER_DATA_PATH)
        logger.info("Master dataset loaded.")
    else:
        AppResources.master_df = None
        logger.warning("Master dataset not found. Using fallback feature sampling.")

# Initialize All Resources
def initialize_resources():
    load_model_resources()
    load_grid()
    load_master_dataset()
    logger.info("All backend resources initialized successfully.")

# Getter Functions
def get_model():
    return AppResources.model

def get_scaler():
    return AppResources.scaler

def get_feature_columns():
    return AppResources.feature_columns

def get_metrics() -> Dict[str, Any]:
    return AppResources.metrics

def get_grid_df():
    return AppResources.grid_df

def get_master_df():
    return AppResources.master_df