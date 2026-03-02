import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

class Settings:
    # API Keys
    GEOAPIFY_API_KEY: str = os.getenv("GEOAPIFY_API_KEY", "")

    # Geocoding Settings
    COUNTRY_CODE: str = "in"
    DEFAULT_LIMIT: int = 5

    CACHE_TTL_SECONDS: int = 60 * 60  # 1 hour

    # Validation
    MIN_QUERY_LENGTH: int = 3

    # Model & Data Paths
    MODEL_PATH: Path = BASE_DIR / "models" / "model_frame_1.pkl"
    GRID_PATH: Path = BASE_DIR / "grid" / "grid_definition.parquet"
    MASTER_DATA_PATH: Path = BASE_DIR / "data_processed" / "3_months" / "final_dataset" / "final_dataset.parquet"

settings = Settings()