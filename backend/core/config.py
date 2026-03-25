import os
from pathlib import Path
from dotenv import load_dotenv

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

class Settings:
    def __init__(self):
        # Environment
        self.ENV: str = os.getenv("ENV", "development").lower()

        # Logging
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

        # API Keys
        self.GEOAPIFY_API_KEY: str = os.getenv("GEOAPIFY_API_KEY", "")

        # Fail fast only in production
        if self.ENV == "production" and not self.GEOAPIFY_API_KEY:
            raise ValueError("Missing GEOAPIFY_API_KEY in production environment")

        # CORS / Networking
        self.ALLOWED_ORIGINS: list = os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:5173"
        ).split(",")

        self.REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", 5))

        # Geocoding Settings
        self.COUNTRY_CODE: str = "in"
        self.DEFAULT_LIMIT: int = 5
        self.CACHE_TTL_SECONDS: int = 60 * 60  # 1 hour

        # Validation
        self.MIN_QUERY_LENGTH: int = 3

        # Rain Categorization Thresholds
        self.RAIN_THRESHOLDS = {
            "light": 2.5,
            "moderate": 15,
        }

        # Model & Data Paths
        self.MODEL_PATH: Path = BASE_DIR / "models" / "model_frame_1.pkl"
        self.GRID_PATH: Path = BASE_DIR / "grid" / "grid_definition.parquet"
        self.MASTER_DATA_PATH: Path = (BASE_DIR/ "data_processed"/ "3_months"/ "final_dataset"/ "final_dataset.parquet")

# Singleton instance
settings = Settings()