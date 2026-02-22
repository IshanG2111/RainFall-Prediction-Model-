from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.locations import router as location_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="Rainfall AI Backend",
        version="1.0.0",
        description="FastAPI backend for Rainfall AI geocoding and forecast system",
    )

    # CORS (important for frontend later)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  #TODO: change to frontend URL in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(location_router)

    return app

app = create_app()