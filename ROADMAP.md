Perfect — here is THE FINAL, CLEAN, PROFESSIONAL, PHASE-WISE ROADMAP exactly how a 40–50 mark 2-credit lab project should be structured.
This version includes:

✔ Separate phases for each dataset
✔ Separate working cycles for 2 days → 7 days → 15 days → 60–90 days
✔ Detailed, point-to-point steps with NO code
✔ Industry-style workflow your professor will love
✔ What to do, why to do it, and what output each step must produce

This is your authoritative project plan.

🚀 MASTER ROADMAP: Rainfall Prediction Using INSAT-3DR IMC, HEM, WDP, UTH, OLR, LST, CMP (Daily Multiple Regression Model)

We use the following datasets from MOSDAC (as per Satellite Data Order.pdf).

DATASETS USED:
Dataset	Product Name	Frequency	Role
IMC	3RIMG_L2B_IMC	Half-hourly	Target Y (Rainfall) → convert to daily total
HEM	3RIMG_L3B_HEM_DLY	Daily	Optional feature OR comparison target
WDP	3RIMG_L2G_WDP	Half-hourly	Wind, shear, vorticity, divergence (X)
UTH	3RIMG_L2B_UTH	Daily	Humidity (X)
OLR	3RIMG_L2B_OLR	Daily	Convection indicator (X)
LST	3RIMG_L2B_LST	Half-hourly	Land surface temperature (X)
CMP	3RIMG_L2C_CMP	Half-hourly	Cloud microphysics (optional X)
🗺️ SPATIAL RESOLUTION

India Region: Lat 6°N → 38°N, Lon 68°E → 98°E

Grid size: 0.25° × 0.25°

All data is aggregated daily per grid cell

📅 TIME RESOLUTION

Daily
(half-hourly products → daily summary; daily products → used as-is)

=========================================================
🟦 PHASE 0 — PROJECT FOUNDATION (ONE-TIME SETUP)
=========================================================
0.1 Create Folder Structure
project/
  data_raw/
  data_processed/
  models/
  notebooks/
  reports/
  frontend/
  backend/

0.2 Create Grid Definition

Create a list of all 0.25° grid cells covering India

Each cell stores:

grid_id

lat_min, lat_max

lon_min, lon_max

lat_center, lon_center

0.3 Decide Feature Summary Rules

IMC → daily total rainfall

WDP → daily mean, max, percentile

LST → daily mean, max

CMP → daily mean

UTH, OLR, HEM → daily values as provided

0.4 Decide ML Target

IMC_daily (primary target Y)

=========================================================
🟦 PHASE 1 — DATA PREP BY PRODUCT (DONE ONCE)
=========================================================

Each dataset is handled separately before merging.

🔵 PHASE 1A — IMC (Half-hourly → Daily)

Role: Target rainfall (Y)

Steps:

Download IMC .h5 files

Spatial subset to India

Convert each timestamp

rainfall_rate_mm_per_hr × 0.5 hr = rainfall_per_step

Sum all steps in a day → IMC_daily_total (mm/day)

Aggregate values per grid cell

Store IMC_daily table

🔵 PHASE 1B — HEM (Daily)

Role: optional feature; benchmark rainfall

Steps:

Download daily HEM

Spatial subset

Assign to grid cells

Store HEM_daily per grid

🔵 PHASE 1C — WDP (Half-hourly → Daily)

Role: Wind dynamics

Steps:

Download half-hourly WDP

Spatial subset

For each grid cell per day, compute:

mean wind

max wind

vorticity_200, vorticity_500, vorticity_850

wind_shear (200mb − 850mb)

divergence/convergence

Store daily WDP feature table

🔵 PHASE 1D — UTH (Daily)

Role: Humidity

Steps:

Download UTH

Spatial subset

Assign to grid cells

Store UTH_daily table

🔵 PHASE 1E — OLR (Daily)

Role: Convection

Steps:

Download OLR

Spatial subset

Store OLR_daily per grid cell
(Strong convection = low OLR)

🔵 PHASE 1F — LST (Half-hourly → Daily)

Role: Temperature

Steps:

Download LST

Spatial subset

For each grid/day:

daily_mean_temperature

daily_max_temperature

Store LST_daily table

🔵 PHASE 1G — CMP (Half-hourly → Daily) — OPTIONAL

Role: Cloud microphysics

Steps:

Download CMP

Spatial subset

Compute daily mean cloud parameter(s)

Store CMP_daily

=========================================================
🟦 PHASE 2 — MERGE ALL PRODUCTS INTO DAILY MASTER DATASET
=========================================================
Steps:

Pick a date range (2 days, 7 days, 15 days, 60–90 days depending on frame)

For each date & grid cell → assemble:

Date | grid_id |
IMC_daily (Y) |
WDP_daily |
LST_daily |
UTH_daily |
OLR_daily |
CMP_daily (optional) |
HEM_daily (optional) |
Time features (day, month, DOY, monsoon)


Remove missing or corrupted rows

Store final dataset as Parquet under folder matching current frame

=========================================================
🟥 PHASE 3 — MODEL TRAINING (FOUR FRAMES)
=========================================================

We build & test model 4 times — gradually increasing data size.

FRAME 1 — 2 DAYS DATA MODEL
🎯 Objective: Validate ENTIRE PIPELINE (not accuracy)
Steps:

Download 2 days IMC/WDP/LST/CMP/UTH/OLR/HEM

Process each dataset to daily

Merge into master table

Fit Multiple Linear Regression

Test on day 2

Output expected:

Model runs without errors

Values reasonable

Pipeline validated

FRAME 2 — 7 DAYS DATA MODEL
🎯 Objective: Early modeling with enough data to check coefficients & signs
Steps:

Process 7 days of all datasets

Add lag features: IMC(t−1)

Add time features: DOY, month, monsoon flag

Fit regression

Evaluate train/test split

Check:

Coefficients sensible (humidity ↑ → rain ↑)

Model improves over naïve baseline

Residuals reduce

FRAME 3 — 15 DAYS DATA MODEL
🎯 Objective: Mid-scale dataset for stable regression & validation
Steps:

Process 15 days

Add richer features:

wind_shear

3-day rolling rainfall avg

vorticity components

Fit multiple regression + ridge regression

Test on last 4–5 days

Validate with spatial hold-out

Output:

Stable coefficients

Realistic accuracy trends

Strong diagnostic plots (scatter, residuals, feature importance)

FRAME 4 — FINAL MODEL (60–90 DAYS)
🎯 Objective: Complete, production-ready model for your lab project
Steps:

Download 2–3 months of all datasets

Repeat all processing

Lag features: t−1, t−3, rolling mean

Fit final regression model

Test on last 20–30% of days

Evaluate:

MAE, RMSE, R²

Compare predicted rainfall vs IMC

Optional: Compare IMC vs HEM

Save final model (model_final.pkl)

Output needed for submission:

Final model

Accuracy metrics

Plots

Clean merged dataset

API-ready prediction logic

=========================================================
🟧 PHASE 4 — BACKEND (Prediction Engine)
=========================================================
Steps:

User inputs place name (e.g., “Patia, Bhubaneswar”)

Frontend calls Nominatim API → returns lat/lon

Backend snaps lat/lon to nearest 0.25° grid cell

Backend loads final model

Backend inserts the grid cell’s daily features into model

Model predicts:

Daily rainfall (mm)

(Optional) predicted atmospheric conditions

Return JSON to frontend

=========================================================
🟦 PHASE 5 — FRONTEND (User Interface)
=========================================================
Steps:

User inputs city/area name

Show coordinates returned from geocoding

Display predicted rainfall

Show supporting parameters (humidity, wind, convection strength)

Display trend graph for last 7 days

Visual indicator (rain–no rain)

=========================================================
🟩 PHASE 6 — REPORT & VIVA PREPARATION
=========================================================
Report must include:

Introduction

Dataset list (as per MOSDAC PDF) with role of each dataset

Why IMC as target

Why 0.25° grid

Why daily aggregation

Detailed preprocessing pipeline

Daily feature table description

Model evolution over 4 frames

Final model performance

Backend–frontend architecture

Screenshots & outputs

Conclusion + future work

Viva must include:

What each dataset measures

Why daily? Why not half-hourly?

Why multiple regression?

What do coefficients mean?

How grid snapping works?

How place → lat/lon → grid → prediction pipeline works

✅ FINAL DELIVERABLES CHECKLIST
✔ Data

Raw H5 files (2d, 7d, 15d, final)

Processed daily grid tables

✔ Models

model_frame_2d.pkl

model_frame_7d.pkl

model_frame_15d.pkl

model_final.pkl

✔ Reports & Plots

Accuracy graphs

Feature importance

Pred vs actual scatter

✔ Backend

Prediction API with grid snapping

✔ Frontend

Location search + rainfall prediction display