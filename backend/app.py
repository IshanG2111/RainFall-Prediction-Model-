import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from backend.routes.locations import router as location_router
from backend.routes.forecast import router as forecast_router
from backend.routes.health import router as health_router
from backend.routes.frontend import router as frontend_router
from backend.core.dependencies import initialize_resources
from backend.core.config import settings
from backend.core.rate_limiter import limiter

import mimetypes

# Fix Windows registry MIME type issues for JS modules
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")

# Project root directory (parent of backend/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

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

    # Static assets for React frontend must be mounted BEFORE the catch-all router
    frontend_assets = PROJECT_ROOT / "frontend" / "dist" / "assets"
    if frontend_assets.exists():
        app.mount("/assets", StaticFiles(directory=str(frontend_assets)), name="frontend_assets")

    # Old Static files (CSS, JS, images) - kept for compatibility if needed
    static_assets = PROJECT_ROOT / "static"
    if static_assets.exists():
        app.mount("/static", StaticFiles(directory=str(static_assets)), name="static")

    # Frontend route (serves index.html at / and handles client-side routing)
    app.include_router(frontend_router)

    return app

app = create_app()