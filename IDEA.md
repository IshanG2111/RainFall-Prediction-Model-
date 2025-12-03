OVERVIEW (single sentence)

Use IMC aggregated to daily as the target and daily-aggregated WDP, UTH, LST, OLR, CMP, HEM (and time/lag features) as predictors; build and validate the pipeline & model in four incremental frames (2 → 7 → 15 → 60–90 days) on a 0.25° × 0.25° India grid.

Reference for dataset availability: MOSDAC product list (IMC, WDP, LST, CMP, UTH, OLR, HEM) from your uploaded file.

GLOBAL DECISIONS (apply to all frames)

Target (Y): IMC (3RIMG_L2B_IMC), convert half-hourly → daily total (mm/day).

Predictors (X): WDP (wind/shear/vorticity), UTH (humidity), LST (surface temp), OLR (convective indicator), CMP (cloud microphysics; optional), HEM (daily) — all daily.

Spatial domain: India bbox Lat 6°N–38°N, Lon 68°E–98°E.

Grid: 0.25° × 0.25° cells; snap user coordinates to nearest cell for predictions.

Storage format: keep raw HDF5 (.h5) as download; write intermediate and final tabular datasets as Parquet (columnar, compressed). Don’t write huge CSVs.

Tools (suggested stack): xarray + dask for HDF5, pandas for tabular, scikit-learn for multiple regression/Ridge; FastAPI/Flask for backend; any simple React/Tailwind frontend. (You may use these tools but this roadmap contains no code.)

Evaluation metrics: MAE, RMSE, R², bias (mean error), scatter plot, residual distribution; also compare IMC vs model and (optional) IMC vs HEM.

Train/test split: time-based split (train on earliest days, test on later days). For spatial experiments include spatial hold-out (reserve some grid cells as test).

Logging & manifests: maintain a small manifest CSV/Parquet containing file paths, date range, product name, grid cell ids processed — makes reruns easy.

FOLDER LAYOUT (exact)
project_root/
 ├─ data_raw/
 │   ├─ imc/
 │   ├─ wdp/
 │   ├─ lst/
 │   ├─ cmp/
 │   ├─ uth/
 │   ├─ olr/
 │   └─ hem/
 ├─ data_processed/
 │   ├─ grid_definition.parquet    # grid cell centers, ids, lat/lon ranges
 │   ├─ frame_2d/                  # processed per-frame parquet shards
 │   ├─ frame_7d/
 │   ├─ frame_15d/
 │   └─ frame_final/               # 60-90 day final dataset
 ├─ models/
 │   ├─ model_frame_2d.pkl
 │   ├─ model_frame_7d.pkl
 │   └─ model_final.pkl
 ├─ notebooks/                      # EDA + diagnostic notebooks (one per frame)
 ├─ reports/
 ├─ backend/
 └─ frontend/

PREPARATION: shared one-time tasks

Create grid_definition.parquet with all 0.25° grid cell centers that intersect India land mask (store grid_id, lat_center, lon_center, lat_min, lat_max, lon_min, lon_max).

Create file manifest listing all downloaded .h5 files per dataset and their timestamps (so you can process incrementally).

Decide aggregation rules up front:

IMC: daily_total_mm = sum(rate_mm_per_hr × interval_hours)

WDP (for each desired variable): daily mean, daily max, 90th percentile

LST: daily mean, daily max

CMP: daily mean stats you decide (e.g., cloud optical depth mean)

UTH, OLR, HEM: use daily values as provided

Decide lag features to create: e.g., Y(t-1), Y(t-3 avg), X(t-1) as needed (document in feature spec).

FOUR FRAMES — DETAILED STEP-BY-STEP (for each frame we will repeat steps; below are the exact actions and success criteria)
FRAME A — Base pipeline + model using 2 days (proof-of-concept)

Goal: verify full end-to-end pipeline and model run; sanity check features & outputs.

Inputs

2 consecutive days of all products (for those that are half-hourly grab all files that cover those 2 days). Use IMC/WDP/LST/CMP/UTH/OLR/HEM where available.

Steps (minute-by-minute checklist)

Download & organize those 2 days’ .h5 files into data_raw folders.

Inspect one sample file from each product to learn variable names & time coordinate conventions (UTC). Log variable names in a short README.

Spatial subset: restrict each dataset to India bbox (6–38N, 68–98E). Discard everything outside.

Grid snapping prep: load grid_definition.parquet and map grid cells that overlap the India bbox.

Temporal aggregation to daily for each product:

IMC: convert half-hourly rate → mm per timestep then sum across day to get daily_total per grid cell.

WDP/LST/CMP: compute per-timestep values → then daily_mean, daily_max, daily_pct90 per grid cell.

UTH/OLR/HEM: extract per-day values and map to grid cells (if product is already gridded daily).

Spatial aggregation per grid cell: for each grid cell compute aggregated daily features (mean or sum depending on variable); store per-cell per-day row.

Build merged dataframe (Date | grid_id | X-features | Y: IMC_daily). Save as Parquet under data_processed/frame_2d/.

Basic EDA & sanity checks: histograms, null counts, min/max, plausible ranges per feature. Flag any strange values.

Create a very small train/test split (train first day, test second day) — note: this won’t produce meaningful generalization, it’s a pipeline test.

Fit a simple multiple linear regression (unregularized or Ridge with large alpha) and compute metrics (MAE, RMSE, R²). Log model file to models/model_frame_2d.pkl.

Produce diagnostic plots: observed vs predicted scatter, residual histogram, coefficients table. Save to reports/frame_2d/.

Acceptance criteria for this frame: pipeline runs without crashes, merged Parquet exists, model trains and predicts, diagnostics generated. You can show UI demo using predictions for one grid cell.

Deliverables (Frame A)

data_processed/frame_2d/*.parquet

models/model_frame_2d.pkl

EDA notebook & short report with plots

Readme: variables/units mapping

FRAME B — Extend to 7 days (small experiment)

Goal: test stability of the pipeline and preliminary model behavior with more days and spatial sampling.

Inputs

7 consecutive days of all products.

Steps

(Repeat FRAME A steps with these differences)

Process full 7-day batch: same spatial subset + aggregation rules. Save to data_processed/frame_7d/.

Spatial sampling (if needed): if you’re keeping only national aggregates, you’ll have only 7 rows — that’s too small. Instead create per-grid-cell rows (i.e., many grid cells × 7 days). Use all land grid cells or a selected subset (e.g., 500–2000 cells) to obtain enough samples.

Feature engineering: add lag features (Y_tminus1), rolling 3-day mean if possible (for early frames, one-day lag is sufficient). Add time features (day_of_year, month, monsoon flag).

Train/Test split: use time-split (first 5 days train, last 2 days test) OR train on first 70% of rows by time and test on last 30% (with spatial hold-out variant also possible).

Modeling: Multiple linear regression + Ridge for stability. Capture coefficients & signs — check if they are physically plausible (e.g., positive humidity coefficient).

Diagnostics: MAE/RMSE/R², residual plots, coefficient table. Also compute model bias (mean(pred − obs)).

Optional: compare performance when including HEM as feature vs excluding HEM.

Acceptance criteria: model coefficients stable (no extreme or NaN), residuals reasonable, pipeline repeatable.

Deliverables (Frame B)

data_processed/frame_7d/*.parquet

models/model_frame_7d.pkl

Comparison report: model with/without HEM, EDA, coefficient table

FRAME C — Extend to 15 days (mid-stage)

Goal: get better statistics, test more advanced features and stronger validation.

Inputs

15 consecutive days (or convenient two-week range).

Steps

Process the 15-day batch same as before; store in data_processed/frame_15d/.

Increase spatial sampling: include more grid cells (aim for a few thousand spatial cells × 15 days to achieve good sample count). You can exclude ocean-dominant grid cells by applying a land mask.

Feature engineering upgrades: add Y(t-1), Y(t-3), 3-day rolling mean, and both mean & max for WDP/LST; create derived features like shear_200_850 = value_200mb − value_850mb, and vorticity_850 as a separate feature.

Modeling: try multiple approaches: Multiple Linear Regression, Ridge (tune alpha with simple CV across time folds), and a non-linear baseline (Random Forest) to check for nonlinearity. Don’t overfit.

Cross-validation: use time-series CV (expanding window) and also run a spatial hold-out test (hold out a subset of grid cells and evaluate model on those cells).

Metrics & analysis: report MAE, RMSE, R² across folds; show feature importance / coefficient stability across folds.

Acceptance criteria: metrics improve or stabilize relative to 7-day frame; model generalizes reasonably across held-out grids and later days.

Deliverables (Frame C)

data_processed/frame_15d/*.parquet

models/model_frame_15d.pkl

Cross-validation report with folds, metrics, and spatial hold-out results

FRAME D — Final model with 2–3 months (60–90 days) (final)

Goal: full model training, evaluation, and prepare deployable artifact.

Inputs

60–90 days of all datasets (download selected continuous period).

Steps

Process the entire 60–90 day dataset using the same aggregation pipeline; store in data_processed/frame_final/. Consider processing in batches (e.g., per-week parquet shards) and then concatenating for speed.

Full spatial sampling: keep all land grid cells or a well-chosen subset. Expect dataset size = grid_cells × days (e.g., 10k cells × 90 days = 900k rows). Use Parquet partitioning by grid_id or date to speed queries.

Advanced feature engineering: as above plus interaction terms (humidity × vorticity), categorical seasonal flags, and normalized features. Consider area weighting if you compute region totals.

Train/Test splitting strategy:

Primary: train on earliest 70% days, test on latest 30% days (temporal split).

Secondary: spatial generalization test — hold out 10–20% of grid cells entirely for testing.

Report both results.

Modeling: Multiple Linear Regression (OLS) for interpretability and Ridge (alpha tuned) for stability; include Random Forest or XGBoost as a stronger nonlinear baseline if compute/time permits. Choose the final model balancing accuracy + interpretability.

Calibration & bias correction: if systematic bias exists (e.g., model underpredicts heavy rain), do a simple bias correction (fit IMC_true ~ a*pred + b on validation). Report pre/post correction.

Uncertainty estimates: compute prediction intervals (e.g., using residual std) or use ensemble of trees if RF/XGBoost. At least report variance of residuals and confidence bounds.

Final evaluation report: full metrics, maps of errors (spatial RMSE), per-month performance, large-event performance (how model performs on days with large rain).

Save final model to models/model_final.pkl with metadata (features list, training dates, grid spec).

Deployable artifacts: model file, inference script, mapping from grid_id → model features, API wrapper.

Deliverables (Frame D)

data_processed/frame_final/ shards + consolidated table

models/model_final.pkl + metadata json

Full evaluation report and figures

Deployment-ready API skeleton + small demo (frontend showing place → prediction)

TEAM TASK BREAKDOWN (4 members) — repeatable per frame

Assign roles and keep handoffs clean. Rotate or keep same roles across frames.

Member A — Data Engineer (Ingestion & Storage)

Download .h5 files from MOSDAC and maintain manifest.

Implement spatial subset to India bbox.

Generate and maintain grid_definition.parquet.

Output: processed per-product Parquet shards for each frame.

Member B — Preprocessing & Feature Engineer

Aggregate half-hourly → daily per grid cell.

Compute derived features (lags, rolling stats, shear, vorticity fields).

Merge into final feature table per frame.

Output: data_processed/frame_*/*.parquet.

Member C — Modeling & Evaluation

Build and run regression models for each frame (OLS, Ridge, basic RF).

Run time and spatial CV, collect metrics and create diagnostic plots.

Save models and metrics.

Output: model files, evaluation notebooks and figures.

Member D — Backend + Frontend + Report

Expose a simple predict API that takes lat/lon/date and returns predictions (snapping to grid).

Build a minimal frontend where user types place (geocode + call backend) and displays results.

Write report sections, slides, and prepare demo.

Output: backend repo, frontend demo, final report.

Coordination: use one shared README.md and an internal sprint board (Trello/GitHub Projects). Use shared storage (Google Drive/OneDrive) for large HDF5 or a network drive.

CHECKS & QA (applies at each frame)

Data QA: confirm no NA after merge for required features, units correct (mm/day), consistent timezone.

Sanity checks: min/max plausible ranges (e.g., humidity 0–100, OLR within typical physical range).

Repro checks: run pipeline for previous frame and ensure identical outputs. Keep a git tag for each frame.

Model sanity: coefficients should have physically plausible signs (e.g., higher humidity → non-negative effect on rainfall). If not, investigate multicollinearity or data errors.

Performance checks: run simple baseline (mean predictor) and ensure model beats baseline.

REPORTING & VIVA PREP (what to include)

Project objective & scope (explain daily aggregation decision)

Dataset listing & justification (cite MOSDAC product list).

Grid design & snapping logic (0.25° justification)

Preprocessing pipeline diagram (flowchart)

Feature list & transformations (explicit table)

Modeling methods & hyperparameters

Results per frame (tables & plots) — include small P-value / coefficient discussion for regression

Limitations (data sparsity, spatial smoothing) & future work (IMC half-hourly model, higher-res grid)

Demo screenshots + API endpoints

OPTIONAL BONUS ELEMENTS (if you want extra credit)

Bias-correct IMC using HEM or auxiliary gauge data (if available).

Produce spatial error maps to show where the model underperforms.

Implement bilinear interpolation for smoother location predictions (instead of nearest-grid).

Add a simple uncertainty estimate per prediction (prediction interval).

FINAL NOTES / Acceptance Criteria for course submission

Minimum deliverables for 40–50 marks: functioning data pipeline, merged daily dataset for final frame, final trained regression model with evaluation (RMSE/MAE/R²), a basic backend that serves predictions by place name, and a concise report describing steps & results.

Extra polish for higher grade: clear EDA, comparisons (HEM vs IMC), bias-correction, spatial test results, and a polished frontend demo.