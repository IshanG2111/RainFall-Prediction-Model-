# Changelog

All notable changes to the Rainfall Prediction Model are documented here.

---

## v2.1.0 — Feature Engineering & Accuracy Improvements

### Fixed
- **Deterministic Predictions**: Resolved inconsistent results on reload by implementing a deterministic random seed based on `grid_id` and `date_target` in `get_realistic_features()`. Identical queries now return identical forecasts.

### Added
- **Meteorological Interaction Features**: Two new engineered features improve heavy-rainfall prediction:
  - `olr_uth_interaction` — Combines deep convection signal (OLR) with upper-level moisture (UTH).
  - `temp_moisture` — Links surface temperature (LST) with humidity availability.
- **Sample Weighting**: Rainfall days are now up-weighted during training to counteract the zero-inflation bias inherent in the dataset.
- **Automated Hyperparameter Tuning**: Replaced hardcoded parameters with `RandomizedSearchCV` to automatically find the optimal `learning_rate`, `max_depth`, `l2_regularization`, and `max_iter`.

### Changed
- **Retrained Model**: Updated `models/model_frame_1.pkl` with the improved pipeline trained on 1.3M data points.

---

## v2.0.0 — Backend Modernisation

### Changed
- Migrated backend from monolithic `app.py` to modular **FastAPI v2.0** architecture with `core/`, `routes/`, `schemas/`, `services/`, and `utils/` packages.
- All API endpoints versioned under `/api/v1/` prefix.
- Added `slowapi` rate limiting (15 req/min for locations, 5 req/min for forecast).
- Implemented Pydantic v2 request/response validation.

### Added
- React + Vite + Tailwind CSS frontend with interactive 7-day forecast dashboard.
- Geoapify-powered location autocomplete with debounced search.
- Physics-constrained post-processing to prevent meteorologically impossible predictions.
