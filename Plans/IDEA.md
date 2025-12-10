# Rainfall Prediction Project Plan

## 1. Overview

**Single-sentence overview**

Use IMC aggregated to daily as the target and daily-aggregated WDP, UTH, LST, OLR, CMP, HEM (and time/lag features) as predictors; build and validate the pipeline & model in four incremental frames (2 days, 7 days, 15 days, 60–90 days).

**Dataset reference**

- Reference for dataset availability: see MOSDAC product list (IMC, WDP, LST, CMP, UTH, OLR, HEM) from your uploaded file.

---

## 2. Global Decisions (Apply to All Frames)

### 2.1 Target (Y)

- **IMC (3RIMG_L2B_IMC)**, half-hourly → daily
- Aggregation:
  - `daily_total_mm = sum(rate_mm_per_hr × interval_hours)` per grid cell per day

### 2.2 Predictors (X)

All on daily scale:

- **WDP**: wind / shear / vorticity
- **UTH**: humidity
- **LST**: surface temperature
- **OLR**: convective indicator
- **CMP**: cloud microphysics (optional)
- **HEM**: daily rainfall product

### 2.3 Spatial & Grid Setup

- Spatial domain:
  - India bounding box: **Lat 6°N–38°N**, **Lon 68°E–98°E**
- Grid:
  - **0.25° × 0.25°** cells
  - All processing & predictions are on these grid cells
  - User latitude/longitude snapped to nearest grid cell for predictions

### 2.4 Storage & Tools

- **Storage format**
  - Keep raw **HDF5 (.h5)** as downloaded
  - Intermediate & final tabular data: **Parquet** (columnar, compressed)
  - Avoid huge CSVs

- **Suggested stack (flexible)**
  - Data:
    - `xarray` + `dask` for HDF5
    - `pandas` for tabular
  - Modeling:
    - `scikit-learn` for multiple regression / Ridge / RandomForest
  - Backend:
    - `FastAPI` or `Flask`
  - Frontend:
    - Any simple React/Tailwind stack

### 2.5 Evaluation & Splits

- **Metrics**
  - MAE, RMSE, R²
  - Bias (mean error)
  - Scatter plot, residual distribution
  - Optional: compare **IMC vs model** and **IMC vs HEM**

- **Train/test split**
  - **Time-based split**: train on earliest days, test on later days
  - For spatial experiments: spatial hold-out (reserve some grid cells as test)

### 2.6 Logging & Manifests

- Maintain a small **manifest** (CSV/Parquet) containing:
  - File paths
  - Date range
  - Product name
  - Grid cell IDs processed
- Purpose: make incremental reruns and debugging easier

---

## 3. Folder Layout (Exact)

```text
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
```

---

## 4. Preparation (Shared One-Time Tasks)

### 4.1 Grid Definition

- Create `data_processed/grid_definition.parquet` with all **0.25° grid cell centers** that intersect an **India land mask**.
- Columns:
  - `grid_id`
  - `lat_center`, `lon_center`
  - `lat_min`, `lat_max`
  - `lon_min`, `lon_max`

### 4.2 File Manifest

- Create a **file manifest** listing all downloaded `.h5` files per dataset and their timestamps:
  - Columns: product, file_path, start_time, end_time, etc.
  - Allows incremental processing and audit trails.

### 4.3 Aggregation Rules

Decide & fix in advance:

- **IMC**
  - `daily_total_mm = sum(rate_mm_per_hr × interval_hours)` per grid cell per day
- **WDP** (for each desired variable)
  - `daily_mean`
  - `daily_max`
  - `daily_90th_percentile`
- **LST**
  - `daily_mean`
  - `daily_max`
- **CMP**
  - Chosen daily summary stats (e.g., `cloud_optical_depth_mean`, etc.)
- **UTH, OLR, HEM**
  - Use daily values as provided (if already daily)

### 4.4 Lag & Time Features

Decide lag features and document:

- Possible examples:
  - `Y(t-1)` (previous day rainfall)
  - `Y(t-3_avg)` (3-day rolling mean)
  - `X(t-1)` lags for key predictors
- Time features:
  - Day-of-year
  - Month
  - Monsoon flag (e.g., Jun–Sep = monsoon)

---

## 5. Four Frames — Step-by-Step

Each frame is an incremental experiment with increasing data and complexity.

- **Frame A** — Base pipeline + model using 2 days (proof-of-concept)
- **Frame B** — Extend to 7 days (small experiment)
- **Frame C** — Extend to 15 days (mid-stage)
- **Frame D** — Final model with 2–3 months (60–90 days)

---

## 5.1 Frame A — 2-Day Proof of Concept

**Goal:**  
Verify full end-to-end pipeline and model run; sanity check features & outputs.

### 5.1.1 Inputs

- 2 consecutive days of **all products**.
- For half-hourly products: grab all files that cover those 2 days.
- Products:
  - IMC / WDP / LST / CMP / UTH / OLR / HEM (where available)

### 5.1.2 Steps (Detailed)

1. **Download & organize**
   - Place `.h5` files for the 2 days into the corresponding `data_raw/` subfolders.

2. **Inspect sample files**
   - For each product, inspect one sample `.h5` file:
     - Variable names
     - Time coordinate conventions (UTC)
   - Log variable names & meanings in a short `README`.

3. **Spatial subset**
   - Restrict each dataset to India bbox:
     - `lat ∈ [6, 38]`, `lon ∈ [68, 98]`
   - Discard everything outside.

4. **Grid snapping prep**
   - Load `grid_definition.parquet`.
   - Map data grid to `grid_id` cells that overlap the India domain.

5. **Temporal aggregation to daily**
   - **IMC**:
     - Convert half-hourly rates to mm per timestep
     - Sum over each day per grid cell → `IMC_daily_total_mm`
   - **WDP / LST / CMP**:
     - From per-timestep values, compute:
       - `daily_mean`
       - `daily_max`
       - `daily_pct90` (90th percentile)
   - **UTH / OLR / HEM**:
     - Extract per-day values and map to grid cells (if already daily gridded).

6. **Spatial aggregation per grid cell**
   - For each grid cell and day, compute aggregated features:
     - Mean or sum as appropriate per variable.
   - Result: one row per **(date, grid_id)**.

7. **Merged dataframe**
   - Columns:
     - `date`
     - `grid_id`
     - X-features (WDP, UTH, LST, OLR, CMP, HEM, etc.)
     - Y: `IMC_daily_total_mm`
   - Save as Parquet under:
     - `data_processed/frame_2d/`

8. **Basic EDA & sanity checks**
   - Histograms
   - Null counts
   - Min/max checks
   - Confirm plausible ranges per feature; flag anomalies.

9. **Train/test split (tiny)**
   - Train: first day
   - Test: second day
   - This is for pipeline validation only, not real generalization.

10. **Model training**
    - Fit a simple multiple linear regression:
      - OLS or Ridge with large alpha.
    - Compute metrics:
      - MAE, RMSE, R².
    - Save model:
      - `models/model_frame_2d.pkl`

11. **Diagnostics**
    - Plots:
      - Observed vs predicted scatter
      - Residual histogram
    - Coefficients table.
    - Save under:
      - `reports/frame_2d/`

### 5.1.3 Acceptance Criteria (Frame A)

- Pipeline runs end-to-end without crashes.
- Merged Parquet exists in `data_processed/frame_2d/`.
- Model trains and predicts.
- Diagnostics (metrics + plots) are generated.
- Optional: simple UI demo for predictions of one grid cell.

### 5.1.4 Deliverables (Frame A)

- `data_processed/frame_2d/*.parquet`
- `models/model_frame_2d.pkl`
- EDA notebook & short report with plots
- README: variables and units mapping

---

## 5.2 Frame B — 7-Day Small Experiment

**Goal:**  
Test stability of the pipeline and preliminary model behavior with more days and spatial sampling.

### 5.2.1 Inputs

- 7 consecutive days of all products (IMC, WDP, LST, CMP, UTH, OLR, HEM).

### 5.2.2 Steps (Differences vs Frame A)

Repeat Frame A process with these differences:

1. **Process full 7-day batch**
   - Same spatial subset and aggregation rules.
   - Save outputs to:
     - `data_processed/frame_7d/`

2. **Spatial sampling**
   - Avoid only national aggregates (too few rows).
   - Create per-grid-cell rows:
     - Many grid cells × 7 days
   - Optionally sub-sample grid cells if dataset is too large.

3. **Feature engineering**
   - Add lag and time features:
     - `Y_tminus1` (previous-day IMC)
     - Rolling 3-day mean if feasible
     - Time features:
       - `day_of_year`, `month`, `monsoon_flag`
   - For early frames, one-day lag is sufficient.

4. **Train/test split**
   - Options:
     - Time-split:
       - First 5 days train, last 2 days test, or
     - Train on first 70% of rows (by time) and test on last 30%.

   - Spatial hold-out variant also possible:
     - Hold out some `grid_id`s.

5. **Modeling**
   - Multiple linear regression + Ridge for stability.
   - Capture coefficients & signs; check physical plausibility:
     - Example: humidity coefficient should usually be non-negative.

6. **Diagnostics**
   - Compute:
     - MAE, RMSE, R²
     - Residual plots
     - Coefficient table
   - Compute model bias:
     - `mean(pred - obs)`

7. **Optional experiment**
   - Compare model performance:
     - With **HEM included** vs **HEM excluded** as a feature.

### 5.2.3 Acceptance Criteria (Frame B)

- Model coefficients are stable:
  - No extreme or NaN values.
- Residuals are reasonable.
- Pipeline can be rerun reliably.

### 5.2.4 Deliverables (Frame B)

- `data_processed/frame_7d/*.parquet`
- `models/model_frame_7d.pkl`
- Comparison report:
  - Model with/without HEM
  - EDA
  - Coefficient table

---

## 5.3 Frame C — 15-Day Mid-Stage

**Goal:**  
Get better statistics; test more advanced features and stronger validation.

### 5.3.1 Inputs

- 15 consecutive days (or a convenient two-week range) of all products.

### 5.3.2 Steps

1. **Process 15-day batch**
   - Same pipeline as before.
   - Store in:
     - `data_processed/frame_15d/`

2. **Increase spatial sampling**
   - Include more grid cells:
     - Aim for **a few thousand grid cells × 15 days**.
   - Exclude ocean-dominant cells using a **land mask**.

3. **Feature engineering upgrades**
   - Lags:
     - `Y(t-1)`, `Y(t-3)`
     - 3-day rolling mean of Y
   - WDP/LST:
     - Include both **mean** & **max** statistics
   - Derived features:
     - `shear_200_850 = value_200mb − value_850mb`
     - `vorticity_850` or similar
   - Continue UTH, OLR, CMP, HEM features as in previous frames.

4. **Modeling**
   - Try multiple approaches:
     - Multiple Linear Regression (OLS)
     - Ridge (tune `alpha` using simple cross-validation over time folds)
     - Non-linear baseline:
       - Random Forest (to detect nonlinearity)
   - Avoid heavy overfitting; keep models interpretable.

5. **Cross-validation**
   - Time-series CV:
     - Expanding-window folds (e.g., train on first 5 days, test on next few, etc.)
   - Spatial hold-out:
     - Hold out some `grid_id`s and evaluate on those unseen locations.

6. **Metrics & analysis**
   - Compute:
     - MAE, RMSE, R² across folds
   - Analyze:
     - Feature importance / coefficient stability across folds
     - Compare linear vs non-linear models

### 5.3.3 Acceptance Criteria (Frame C)

- Metrics:
  - Improve or stabilize relative to 7-day frame.
- Generalization:
  - Reasonable performance on:
    - Held-out grid cells (spatial)
    - Later days (temporal)

### 5.3.4 Deliverables (Frame C)

- `data_processed/frame_15d/*.parquet`
- `models/model_frame_15d.pkl`
- Cross-validation report:
  - Folds
  - Metrics
  - Spatial hold-out results

---

## 5.4 Frame D — Final 60–90 Day Model

**Goal:**  
Full model training and evaluation; produce deployable artifact (model + API + demo).

### 5.4.1 Inputs

- 60–90 days of all datasets over a continuous time period.

### 5.4.2 Steps

1. **Full-period processing**
   - Process entire 60–90-day dataset using same aggregation pipeline.
   - Store in:
     - `data_processed/frame_final/`
   - Consider batch processing:
     - e.g., per-week Parquet shards then concatenate.

2. **Full spatial sampling**
   - Keep all land grid cells or a carefully chosen subset.
   - Approximate dataset size:
     - Example: 10k cells × 90 days ≈ 900k rows.
   - Use Parquet partitioning:
     - By `grid_id` or `date` (or both) for efficient IO.

3. **Advanced feature engineering**
   - Same as Frame C, plus:
     - Interaction terms (e.g., `humidity × vorticity`)
     - Seasonal categorical flags
     - Normalized/scaled features
   - Consider area weighting if computing region totals.

4. **Train/test splitting**

   - **Primary (temporal):**
     - Train on earliest 70% of days
     - Test on latest 30% of days

   - **Secondary (spatial):**
     - Hold out 10–20% of grid cells entirely for testing.
     - Report performance on these held-out locations.

5. **Modeling**

   - Main models:
     - Multiple Linear Regression (OLS) — interpretability
     - Ridge Regression (alpha tuned) — stability
   - Stronger nonlinear baseline (if resources allow):
     - Random Forest or XGBoost
   - Choose final “primary” model based on:
     - Performance vs complexity
     - Interpretability requirements

6. **Calibration & bias correction**

   - If systematic bias exists (e.g., underprediction of heavy rain):
     - Fit a simple bias correction model on validation:
       - `IMC_true ~ a * pred + b`
     - Apply bias correction to predictions.
   - Report:
     - Metrics before and after bias correction.

7. **Uncertainty estimates**

   - At minimum:
     - Compute variance of residuals.
     - Provide prediction intervals using residual standard deviation.
   - Or:
     - Use ensemble models (e.g., RF/XGBoost) for uncertainty via spread.

8. **Final evaluation report**

   - Include:
     - Full metrics (MAE, RMSE, R²)
     - Spatial error maps (e.g., spatial RMSE)
     - Per-month or seasonal performance
     - Performance on heavy-rain events (tail behavior)

9. **Final artifacts**

   - Save final model:
     - `models/model_final.pkl`
   - Attach metadata JSON:
     - Feature list
     - Training date range
     - Grid specification
     - Preprocessing steps (needed for inference)

   - Deployable components:
     - Inference script
     - Mapping: `grid_id → model features`
     - API wrapper (FastAPI/Flask)
     - Basic frontend for querying and visualization

### 5.4.3 Deliverables (Frame D)

- `data_processed/frame_final/` shards + consolidated table
- `models/model_final.pkl` + metadata JSON
- Full evaluation report and figures
- Deployment-ready API skeleton + small demo (frontend showing place → prediction)

---

## 6. Team Task Breakdown (4 Members)

Roles are per frame but can be rotated.

### 6.1 Member A — Data Engineer (Ingestion & Storage)

- Download `.h5` files from MOSDAC.
- Maintain file manifest.
- Implement spatial subset to India bbox.
- Generate and maintain `grid_definition.parquet`.

**Output:**

- Processed per-product Parquet shards for each frame.

### 6.2 Member B — Preprocessing & Feature Engineer

- Aggregate half-hourly → daily per grid cell.
- Compute derived features:
  - Lags
  - Rolling stats
  - Shear, vorticity, etc.
- Merge into final feature table per frame.

**Output:**

- `data_processed/frame_*/*.parquet`

### 6.3 Member C — Modeling & Evaluation

- Build and run regression models per frame:
  - OLS, Ridge, basic RF.
- Run time-based and spatial cross-validation.
- Collect metrics and create diagnostic plots.

**Output:**

- Model files (`models/…pkl`)
- Evaluation notebooks and figures

### 6.4 Member D — Backend, Frontend & Reporting

- Backend:
  - Simple predict API: input (lat, lon, date) → prediction
  - Handles grid snapping and model inference.
- Frontend:
  - Minimal interface:
    - User types location (geocode)
    - Calls backend and displays prediction.
- Reporting:
  - Write report sections
  - Slides and demo prep

**Output:**

- Backend project
- Frontend demo
- Final written report

### 6.5 Coordination

- Use:
  - Shared `README.md`
  - Internal sprint board (Trello / GitHub Projects)
  - Shared storage (Google Drive/OneDrive or network drive) for large HDF5 files.

---

## 7. Checks & Quality Assurance (Per Frame)

### 7.1 Data QA

- Ensure:
  - No NAs after merge for required features.
  - Units are correct (especially rainfall in mm/day).
  - Timezone handling is consistent (UTC, local, etc.).

### 7.2 Sanity Checks

- Confirm plausible ranges:
  - Humidity: 0–100
  - OLR: within typical physical range
  - LST, winds, etc. within expected bounds.

### 7.3 Reproducibility

- Re-run pipeline for a previous frame and ensure identical outputs.
- Tag important milestones in git (e.g., per frame).

### 7.4 Model Sanity

- Coefficients:
  - Physically plausible signs (e.g., higher humidity → non-negative effect on rainfall).
- If not:
  - Investigate multicollinearity, data issues, or feature scaling problems.

### 7.5 Performance Checks

- Run simple baselines:
  - Mean predictor, climatology, persistence.
- Ensure model meaningfully outperforms baselines.

---

## 8. Reporting & Viva Preparation

Include at least the following in your final documentation/presentation:

1. **Project objective & scope**
   - Explain daily aggregation choice and modeling goals.
2. **Datasets listing & justification**
   - Cite MOSDAC product list and why each variable is useful.
3. **Grid design & snapping**
   - 0.25° grid justification and snapping method.
4. **Preprocessing pipeline diagram**
   - Flowchart: raw → subset → aggregate → features → model.
5. **Feature list & transformations**
   - Explicit table: name, source, aggregation, units.
6. **Modeling methods & hyperparameters**
   - Which models, how hyperparameters were chosen.
7. **Results per frame**
   - Tables & plots:
     - Metrics per frame
     - Coefficients, p-values (where applicable)
8. **Limitations**
   - Data sparsity, spatial smoothing, sensor issues, etc.
9. **Future work**
   - IMC half-hourly modeling
   - Higher-resolution grid
   - More advanced models.
10. **Demo screenshots & API endpoints**
    - Example requests/responses.

---

## 9. Optional Bonus Elements

For extra credit / higher grade:

- Bias-correct IMC using HEM or auxiliary gauge data (if available).
- Produce spatial error maps:
  - Show locations where model underperforms.
- Implement **bilinear interpolation** for smoother location predictions instead of nearest-grid.
- Add simple **uncertainty estimates** per prediction:
  - Prediction intervals, ensembles, or residual-based intervals.

---

## 10. Final Notes & Acceptance Criteria (Course Submission)

### 10.1 Minimum Deliverables (40–50 Marks)

- Functioning data pipeline.
- Merged daily dataset for final frame (60–90 days).
- Final trained regression model with evaluation:
  - RMSE, MAE, R².
- Basic backend that serves predictions for given location and date.
- Minimal visualization or printout of results.

### 10.2 Extra Polish (Higher Grade)

- Clear EDA and visualizations.
- Comparisons:
  - HEM vs IMC rainfall.
- Bias correction step.
- Spatial test results (spatial hold-out performance).
- Polished frontend demo and well-structured report.
