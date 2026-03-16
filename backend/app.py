import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from backend.routes.locations import router as location_router
from backend.routes.forecast import router as forecast_router
from backend.routes.health import router as health_router
from backend.core.config import settings
from backend.core.rate_limiter import limiter

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)

# Application Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Initializing backend resources...")
        initialize_resources()
        logger.info("Backend resources initialized successfully.")
    except Exception:
        logger.exception("Resource initialization failed.")
        raise
    yield
    logger.info("Application shutdown complete.")

# App Factory
def create_app() -> FastAPI:
    app = FastAPI(
        title="Rainfall AI Backend",
        version="2.0.0",
        description="FastAPI backend for Rainfall AI geocoding and ML-based forecast system",
        lifespan=lifespan,
    )

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Attach limiter
    app.state.limiter = limiter
    app.add_exception_handler(
        RateLimitExceeded,
        lambda request, exc: JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Please try again later."},
        ),
    )
    app.add_middleware(SlowAPIMiddleware)

    # Versioned API prefix
    API_PREFIX = "/api/v1"

    app.include_router(location_router, prefix=API_PREFIX)
    app.include_router(forecast_router, prefix=API_PREFIX)
    app.include_router(health_router, prefix=API_PREFIX)

    return app

app = create_app()