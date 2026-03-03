from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
from backend.routes.locations import router as location_router
from backend.routes.forecast import router as forecast_router
from backend.routes.health import router as health_router
from backend.routes.frontend import router as frontend_router
from backend.core.dependencies import initialize_resources

_BASE_DIR = Path(__file__).resolve().parent.parent
_STATIC_DIR = _BASE_DIR / "static"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Logic
    try:
        initialize_resources()
    except Exception as e:
        print(f"Resource initialization failed: {e}")
        raise e  # Stop app from starting if critical resources fail
    yield  # Application runs here


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
        allow_origins=["*"],  # TODO: Restrict this in production to specific domains
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Serve static files (CSS, JS, assets)
    if _STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

    # Register Routers
    app.include_router(frontend_router)                           # GET /  → index.html
    app.include_router(location_router, prefix="/api", tags=["Locations"])
    app.include_router(forecast_router, prefix="/api", tags=["Forecast"])
    app.include_router(health_router, prefix="/api", tags=["Health"])

    return app

app = create_app()