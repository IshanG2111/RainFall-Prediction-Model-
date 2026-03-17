# Evaluation Criteria Documentation

## Purpose
This document explains the complete evaluation rubric for the Rainfall Prediction Model project and maps each criterion to implementation evidence available in this repository.

## Marks Distribution

| Criteria | Maximum Marks |
|---|---:|
| Data Collection | 10 |
| Data Engineering | 10 |
| Database Setup | 10 |
| Model Training | 10 |
| Model Validation | 10 |
| Result Analysis | 10 |
| Front End | 20 |
| Report | 15 |
| Innovation | 5 |
| **Total** | **100** |

---

## 1) Data Collection (10)

### What this criterion evaluates
Quality, relevance, and scale of data collection for rainfall forecasting.

### What was implemented
- Multi-source weather feature extraction from INSAT-3DR derived parameters.
- Consolidated data preparation pipeline under the scripts workflow.
- Historical records were prepared at scale to support robust model training.

### Evidence in this project
- Source and processed datasets are maintained in the data directory.
- Feature sources are documented in features documentation and model documentation.
- Training size references are documented in project summary materials.

---

## 2) Data Engineering (10)

### What this criterion evaluates
How raw weather data was cleaned, transformed, and engineered into model-ready inputs.

### What was implemented
- Cyclic encodings for temporal continuity (`day_sin`, `day_cos`, `week_sin`, `week_cos`).
- Domain interaction features for meteorological behavior:
  - `olr_uth_interaction`
  - `temp_moisture`
- Target log transform (`log1p`) and inverse transform (`expm1`).
- Standard scaling for stable training dynamics.
- Data clipping to realistic meteorological ranges.

### Evidence in this project
- Full rationale and formulas are documented in feature engineering documentation.
- Changelog confirms addition of interaction features and improved pipeline.

---

## 3) Database Setup (10)

### What this criterion evaluates
Data organization, storage structure, and operational access pattern for training and inference.

### What was implemented
- Structured data layout separating raw, intermediate, and final datasets.
- Grid-based indexing strategy to map geographic coordinates to nearest historical cells.
- Centralized resource initialization for loading model artifacts and master data.
- Supporting cache utilities for efficient repeated operations.

### Evidence in this project
- Data folder hierarchy includes raw, grid, and processed assets.
- Backend dependency/resource initialization and grid services are documented in backend architecture.

---

## 4) Model Training (10)

### What this criterion evaluates
Model selection quality, training strategy, and handling of rainfall prediction challenges.

### What was implemented
- Primary algorithm: `HistGradientBoostingRegressor`.
- Zero-inflated rainfall handling through log-target transformation.
- Sample weighting added to improve non-zero rainfall learning.
- Hyperparameter tuning with `RandomizedSearchCV`.
- Retrained model artifacts integrated into production workflow.

### Evidence in this project
- Model architecture documentation explains algorithm and training pipeline.
- Changelog records training upgrades and retraining updates.

---

## 5) Model Validation (10)

### What this criterion evaluates
Whether validation strategy is realistic, leakage-safe, and performance-focused.

### What was implemented
- Time-aware validation strategy using time-series split methodology.
- Performance tracked with standard regression metrics:
  - RMSE
  - MAE
  - R2 score
- Validation reported against large-scale historical data.

### Evidence in this project
- Evaluation approach and metric reporting are documented in project readme and model notes.
- Method emphasizes honest future-style testing rather than random split shortcuts.

---

## 6) Result Analysis (10)

### What this criterion evaluates
Interpretation quality of model outputs and practical usability of forecast results.

### What was implemented
- Seven-day rainfall output with category interpretation:
  - No Rain
  - Light Rain
  - Moderate Rain
  - Heavy Rain
- Physics-constrained post-processing to reject implausible predictions.
- Trend visualizations and day-wise forecast cards for clearer interpretation.

### Evidence in this project
- Backend and model docs describe post-processing and categorization logic.
- Frontend includes forecast cards, trend view, and map-based context.

---

## 7) System Implementation (Frontend + Backend) (20)

This section intentionally explains frontend and backend together in one integrated flow, as required.

### Full-stack flow
1. User searches a location in the frontend dashboard.
2. Frontend calls location autocomplete API (`GET /api/v1/locations`).
3. User selects a location and date, then submits forecast request.
4. Frontend sends prediction request (`POST /api/v1/forecast`).
5. Backend validates request using Pydantic schemas.
6. Service pipeline resolves grid, prepares dates, performs model inference, and applies physics rules.
7. Backend returns structured seven-day response.
8. Frontend renders outlook cards, trend chart, and map context.

### Frontend implementation highlights
- React + Vite + TypeScript user interface.
- Debounced location search and loading/error state handling.
- Forecast visualization components (cards, chart, map).
- API abstraction layer for clean request handling.

### Backend implementation highlights
- FastAPI modular architecture: routes, services, schemas, core dependencies, utilities.
- Versioned APIs under `/api/v1`.
- Health checks, request validation, and rate limiting.
- Forecast orchestration across geocoding, grid mapping, date generation, and model service.

### Why this earns high weight
- Demonstrates end-to-end engineering, not only model experimentation.
- Shows production-style integration between data science output and user-facing application.

---

## 8) Report (15)

### What this criterion evaluates
Completeness, clarity, and technical communication quality of documentation and reporting.

### What was implemented
- Dedicated documentation for architecture, feature engineering, physics basis, roadmap, and research context.
- Structured readme with setup, run instructions, endpoints, and model summary.
- Changelog tracking improvements and versioned technical updates.

### Evidence in this project
- Docs directory contains focused documents for each major technical area.
- Reporting style supports both academic review and implementation handover.

---

## 9) Innovation (5)

### What this criterion evaluates
Novel engineering choices and meaningful improvements beyond baseline implementation.

### What was implemented
- Deterministic prediction seeding tied to location/date for reproducibility.
- Physics-aware constraints on ML outputs.
- Heavy-rain-oriented interaction features.
- Automated hyperparameter tuning replacing fixed manual parameters.
- Quantile and uncertainty-aware thinking reflected in design direction.

### Evidence in this project
- Changelog and architecture docs capture iterative innovations and reliability upgrades.

---

## Evidence Mapping Table

| Criteria | Marks | Primary Evidence Sources |
|---|---:|---|
| Data Collection | 10 | `README.md`, `docs/features.md`, `data/` |
| Data Engineering | 10 | `docs/feature_engineering.md`, `changes.md` |
| Database Setup | 10 | `backend/core/dependencies.py`, `backend/services/grid_service.py`, `data/` |
| Model Training | 10 | `docs/model_architecture.md`, `src/model.py`, `changes.md` |
| Model Validation | 10 | `README.md`, `docs/model_architecture.md` |
| Result Analysis | 10 | `docs/model_architecture.md`, `docs/frontend.md` |
| System Implementation (Frontend + Backend) | 20 | `docs/frontend.md`, `docs/backend_architecture.md`, `frontend/src/`, `backend/` |
| Report | 15 | `README.md`, `docs/`, `changes.md` |
| Innovation | 5 | `changes.md`, `docs/feature_engineering.md`, `docs/backend_architecture.md` |

---

## Conclusion
The project aligns with all rubric criteria and provides traceable implementation evidence for each mark category. The frontend and backend are documented together in one integrated system section to clearly demonstrate complete full-stack delivery.