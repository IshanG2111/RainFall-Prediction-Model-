<div align="center">

# Backend — Rainfall AI

![FastAPI](https://img.shields.io/badge/FastAPI-v2.0-009688?style=flat-square&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square&logo=pydantic&logoColor=white)

</div>

> FastAPI-based REST backend for the Rainfall AI geocoding and ML-based 7-day forecast system.

---

## Architecture

The backend follows a **layered, modular architecture** separating routing, business logic, data access, and configuration:

```
backend/
├── app.py                        # FastAPI app factory (create_app, lifespan, CORS, rate-limiting)
├── core/
│   ├── config.py                 # Centralised settings and environment variable loading
│   ├── dependencies.py           # Singleton resource loader (model, scaler, grid, master dataset)
│   └── rate_limiter.py           # Shared slowapi limiter instance
├── routes/
│   ├── frontend.py               # GET /  → serves React index.html (catch-all)
│   ├── health.py                 # GET /api/v1/health
│   ├── locations.py              # GET /api/v1/locations?q=<query>
│   └── forecast.py               # POST /api/v1/forecast
├── schemas/
│   ├── request_schema.py         # ForecastRequest (Pydantic v2 input model)
│   ├── forecast_schema.py        # ForecastResponse (Pydantic v2 output model)
│   └── location_schema.py        # LocationSuggestion (Pydantic v2 output model)
├── services/
│   ├── forecast_service.py       # Orchestration layer (date → grid → model → response)
│   ├── model_service.py          # Feature engineering + ML inference + physics constraints
│   ├── geocoding_service.py      # Geoapify API wrapper with TTL cache
│   ├── grid_service.py           # Maps lat/lon → nearest historical grid cell
│   └── date_service.py           # Generates 7-day forecast date array
└── utils/
    └── cache.py                  # Thread-safe TTL cache implementation
```

---

## API Endpoints (v1)

All endpoints are versioned under `/api/v1`. Rate limiting is enforced per IP via `slowapi`.

| Method | Endpoint                      | Rate Limit | Description                            |
|--------|-------------------------------|------------|----------------------------------------|
| `GET`  | `/api/v1/health`              | —          | Server + model readiness check         |
| `GET`  | `/api/v1/locations?q=<query>` | 15/min     | Location autocomplete (≥ 3 chars)      |
| `POST` | `/api/v1/forecast`            | 5/min      | 7-day rainfall forecast for a location |

### `GET /api/v1/locations`

Returns up to 5 matching Indian locations via Geoapify geocoding.
```json
[
  { "place": "New Delhi, India", "lat": 28.6139, "lon": 77.2090 },
  { "place": "New Town, WB, India", "lat": 22.5883, "lon": 88.4734 }
]
```

### `POST /api/v1/forecast`

Runs a 7-day ML rainfall prediction for a selected location and start date.

**Request:**
```json
{
  "location": "New Delhi, India",
  "lat": 28.6139,
  "lon": 77.2090,
  "date": "2026-03-15"
}
```

**Response:**
```json
{
  "location": "New Delhi, India",
  "coordinates": { "lat": 28.6139, "lon": 77.2090 },
  "forecast": [
    { "date": "2026-03-15", "rainfall_mm": 0.33, "status": "Light Rain" },
    { "date": "2026-03-16", "rainfall_mm": 0.0, "status": "No Rain" },
    { "date": "2026-03-17", "rainfall_mm": 5.08, "status": "Moderate Rain" }
  ]
}
```

### `GET /api/v1/health`

```json
{ "status": "ok", "model_loaded": true, "grid_loaded": true }
```

---

## Quick Start

**Prerequisites:** Python 3.9+, a virtual environment, and a [Geoapify API key](https://www.geoapify.com/).

```bash
# 1. Install dependencies (from project root)
pip install -r requirements.txt

# 2. Create .env at the project root
echo "GEOAPIFY_API_KEY=your_key_here" > .env

# 3. Train the model (first time only)
python src/model.py

# 4. Start the server
python src/app.py
# — or —
uvicorn backend.app:app --host 0.0.0.0 --port 5000 --reload
```

| Resource             | URL                                  |
|----------------------|--------------------------------------|
| Web App              | `http://localhost:5000/`             |
| Interactive API Docs | `http://localhost:5000/docs`         |
| OpenAPI JSON         | `http://localhost:5000/openapi.json` |

---

## Environment Variables

Defined in `.env` at the project root. Loaded by `backend/core/config.py`.

| Variable           | Description                   | Default                                       |
|--------------------|-------------------------------|-----------------------------------------------|
| `GEOAPIFY_API_KEY` | Geoapify autocomplete API key | *(required)*                                  |
| `ALLOWED_ORIGINS`  | Comma-separated CORS origins  | `http://localhost:5173,http://localhost:3000` |
| `REQUEST_TIMEOUT`  | HTTP client timeout (seconds) | `5`                                           |

---

> For full API reference with request/response schemas, error codes, and frontend integration patterns see [`docs/backend_architecture.md`](../docs/backend_architecture.md).