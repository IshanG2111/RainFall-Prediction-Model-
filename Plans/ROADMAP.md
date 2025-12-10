# 🌧️ Rainfall Prediction Project — PROFESSIONAL LAB ROADMAP

This roadmap outlines a robust, phase-wise approach for a 40–50 mark, 2-credit lab project on rainfall prediction using multi-satellite datasets. 

**Key features:**
- 📦 Individual phases for each dataset
- 📅 Cycle-based project (2 days → 7 days → 15 days → 60–90 days)
- ✅ Detailed point-to-point steps (no code)
- 🧑‍💻 Realistic workflow (industry-style)
- ℹ️ What to do, *why* to do it, and *what output* to expect at each step

---

## 🚀 MASTER ROADMAP  
**Title:** Rainfall Prediction Using INSAT-3DR Datasets (IMC, HEM, WDP, UTH, OLR, LST, CMP)  
**Goal:** Build a daily multiple regression model of rainfall for the India region

---

### 1. 📑 DATASETS USED

| Product | Name              | Freq.       | Role                                   |
|---------|-------------------|-------------|----------------------------------------|
| IMC     | 3RIMG_L2B_IMC     | Half-hourly | 🎯 Target Y (Rainfall, daily total)    |
| HEM     | 3RIMG_L3B_HEM_DLY | Daily       | Optional feature/benchmark target      |
| WDP     | 3RIMG_L2G_WDP     | Half-hourly | Wind, shear, vorticity, divergence (X) |
| UTH     | 3RIMG_L2B_UTH     | Daily       | Humidity (X)                           |
| OLR     | 3RIMG_L2B_OLR     | Daily       | Convection indicator (X)               |
| LST     | 3RIMG_L2B_LST     | Half-hourly | Land surface temperature (X)           |
| CMP     | 3RIMG_L2C_CMP     | Half-hourly | Cloud microphysics (optional X)        |

**Spatial Region:**  
- India: Lat 6°N – 38°N, Lon 68°E – 98°E  
- Grid size: 0.25° × 0.25° (all data daily, per grid cell)

---

## 🟦 PHASE 0 — PROJECT FOUNDATION (One-time Setup)
**0.1. Folder Structure**
```plaintext
project/
  ├── data_raw/
  ├── data_processed/
  ├── models/
  ├── notebooks/
  ├── reports/
  ├── frontend/
  └── backend/
```
**0.2. Grid Definition**  
- List all 0.25° grid cells covering India  
- Each cell stores: `grid_id`, `lat_min`, `lat_max`, `lon_min`, `lon_max`, `lat_center`, `lon_center`

**0.3. Feature Summary Rules**  
- IMC: daily total rainfall  
- WDP: daily mean/max/percentile  
- LST: daily mean/max  
- CMP: daily mean  
- UTH, OLR, HEM: daily values as provided

**0.4. ML Target**  
- IMC_daily (Rainfall, Y)

---

## 🟦 PHASE 1 — DATA PREP BY PRODUCT

*Handle each dataset individually before merging.*

### 🔵 1A. IMC (Half-hourly → Daily, *Target Y*)  
- Download .h5 files  
- Subset to India  
- For each timestamp:  
    `rainfall_rate_mm_per_hr × 0.5 hr = rainfall_per_step`  
- Sum all steps in a day → `IMC_daily_total (mm/day)`
- Aggregate per grid cell  
- Store as `IMC_daily` table

### 🔵 1B. HEM (Daily)
- Download daily HEM 
- Subset spatially  
- Assign to grids  
- Store as `HEM_daily`

### 🔵 1C. WDP (Half-hourly → Daily)
- Download WDP  
- Subset spatially  
- For each grid cell per day, compute:  
    - mean/max wind  
    - vorticity (200, 500, 850 mb)  
    - wind shear (200mb–850mb)  
    - divergence/convergence  
- Store as `WDP_daily`

### 🔵 1D. UTH (Daily)
- Download UTH  
- Spatial subset  
- Assign to grids  
- Store as `UTH_daily`

### 🔵 1E. OLR (Daily)
- Download OLR  
- Spatial subset  
- Store per grid cell  
- (Low OLR → strong convection)

### 🔵 1F. LST (Half-hourly → Daily)
- Download LST  
- Subset spatially  
- For each grid/day:  
    - daily mean temperature  
    - daily max temperature  
- Store as `LST_daily`

### 🔵 1G. CMP (Half-hourly → Daily, *Optional*)
- Download CMP  
- Spatial subset  
- Compute daily mean cloud parameter(s)  
- Store as `CMP_daily`

---

## 🟦 PHASE 2 — MERGE ALL PRODUCTS INTO DAILY MASTER DATASET

**Steps:**  
- Pick date range (2d, 7d, 15d, 60–90d as required)  
- For each date & grid cell, assemble:  
    - Date, grid_id
    - `IMC_daily (Y)`
    - `WDP_daily`
    - `LST_daily`
    - `UTH_daily`
    - `OLR_daily`
    - `CMP_daily` (optional)
    - `HEM_daily` (optional)
    - Time features (day, month, DOY, monsoon)
- Remove missing/corrupted rows
- Store as **Parquet** under frame-specific folder

---

## 🟥 PHASE 3 — MODEL TRAINING (Four Frames)

Train/test model in four stages with increasing dataset size.

### 🟠 FRAME 1 — 2 Days Data Model
- Validate entire pipeline (not accuracy)
- Download/process 2 days of all datasets
- Merge into master table
- Fit multiple linear regression
- Test on day 2
- **Output:**  
    - Model runs without errors  
    - Values reasonable  
    - Pipeline validated

### 🟢 FRAME 2 — 7 Days Data Model
- Process 7 days of datasets
- Add lag features: IMC(t–1)
- Add time features: DOY, month, monsoon flag
- Fit regression, evaluate train/test split
- **Check:**  
    - Coefficients have sensible signs (e.g., humidity ↑ → rain ↑)
    - Model better than naïve baseline
    - Reduced residuals

### 🔵 FRAME 3 — 15 Days Data Model
- Process 15 days
- Add features:
    - wind_shear
    - 3-day rolling rainfall avg
    - vorticity components
- Fit multiple regression & ridge regression
- Test on last 4–5 days, spatial hold-out
- **Output:**  
    - Stable coefficients  
    - Realistic accuracy  
    - Diagnostic plots (scatter, residuals, importance)

### 🟣 FRAME 4 — FINAL MODEL (60–90 Days)
- Download/process 2–3 months’ data
- As above, with lag/rolling features (t–1, t–3, rolling mean)
- Fit final regression model
- Test on last 20–30% of days
- **Evaluate:**  
    - MAE, RMSE, R² metrics  
    - Compare predictions vs IMC  
    - (Optional: IMC vs HEM)  
    - Save as `model_final.pkl`
- **Submission Output:**  
    - Final model & accuracy  
    - Plots  
    - Clean merged dataset  
    - API-ready logic

---

## 🟧 PHASE 4 — BACKEND (Prediction Engine)

**Steps:**  
1. User inputs place name (e.g., “Patia, Bhubaneswar”)
2. Frontend calls Nominatim API → gets lat/lon  
3. Backend snaps lat/lon to nearest 0.25° grid cell  
4. Backend loads final model  
5. Backend fetches features for cell and predicts:
    - `Daily rainfall (mm)`
    - (Optional: atmospheric conditions)
6. Backend returns JSON to frontend

---

## 🟦 PHASE 5 — FRONTEND (User Interface)

**Features:**  
- User inputs city/area
- Show lat/lon (from geocoding)
- Display predicted rainfall
- Show supporting parameters (humidity, wind, convection)
- Display trend graph for last 7 days
- Visual rain/no-rain indicator

---

## 🟩 PHASE 6 — REPORT & VIVA PREPARATION

**Report Must Include:**  
- Introduction, dataset list (from MOSDAC) + their roles
- Why IMC as target; why 0.25° grid; why daily aggregation
- Detailed preprocessing pipeline  
- Daily feature table description  
- Model evolution (all 4 frames)  
- Final performance  
- Backend/frontend architecture  
- Screenshots/outputs  
- Conclusion + future work

**Viva Must Cover:**  
- What each dataset measures
- Why daily? Why not half-hourly?
- Why multiple regression?
- What coefficients mean
- How grid snapping works
- How the pipeline (place → lat/lon → grid → prediction) works

---

## ✅ FINAL DELIVERABLES CHECKLIST

**DATA**
- Raw H5 files (2d, 7d, 15d, final)
- Processed daily grid tables

**MODELS**
- `model_frame_2d.pkl`
- `model_frame_7d.pkl`
- `model_frame_15d.pkl`
- `model_final.pkl`

**REPORTS & PLOTS**
- Accuracy graphs
- Feature importance
- Pred vs actual scatter

**BACKEND**
- Prediction API (with grid snapping)

**FRONTEND**
- Location search + rainfall prediction display

---
