import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

class Settings:
    GEOAPIFY_API_KEY: str = os.getenv("GEOAPIFY_API_KEY", "")
    COUNTRY_CODE: str = "in"
    DEFAULT_LIMIT: int = 10

    # Cache
    CACHE_TTL_SECONDS: int = 60 * 60  # 1 hour

    # Validation
    MIN_QUERY_LENGTH: int = 3


settings = Settings()