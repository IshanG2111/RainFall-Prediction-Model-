# 🌧️ Rainfall Prediction Using INSAT-3DR Satellite Products  
Daily Rainfall Modeling · Multi-Phase Pipeline · Regression-Based Prediction

---

## 📌 Project Overview

This project builds a complete rainfall prediction pipeline using **INSAT-3DR satellite products** from MOSDAC.

All satellite data is converted into **daily features** on a **0.25° × 0.25° India grid**, and then used to train regression models across multiple incremental phases.

The pipeline grows gradually from:

**2 days → 7 days → 15 days → 60–90 days**

ensuring correctness, stability, and accuracy at each step.

---

# 🧭 Project Phases

## 🟦 Phase 0 — Project Foundation
- Create folder structure  
- Set up 0.25° spatial grid plan  
- Decide aggregation rules for each dataset  
- Choose IMC as the target variable  
- Prepare evaluation strategy

## 🟦 Phase 1 — 2-Day Pipeline (Pilot Run)
- Download & organize 2 days of all INSAT datasets  
- Validate raw data  
- Build manifest for all files  
- Build spatial grid (Step 2)  
- Convert half-hourly → daily  
- Merge datasets  
- Train a small regression model  

## 🟩 Phase 2 — 7-Day Pipeline (Early Modeling)
- Process 7 days end-to-end  
- Add lag features & time features  
- Train linear & ridge regressions  
- Generate early diagnostic plots  

## 🟧 Phase 3 — 15-Day Pipeline (Advanced Features)
- Add rolling stats, wind shear, vorticity, divergence  
- Time-based cross-validation  
- Spatial hold-out validation  
- Improve model stability  

## 🟥 Phase 4 — 60–90 Day Final Dataset (Production Model)
- Build the full dataset  
- Train final regression model  
- Deploy backend prediction API  
- Build frontend UI  
- Final reports & evaluation

---

# Phase 1 — 2-Day Pipeline

Phase 1 validates the entire workflow using **two days of data**:  
**15 July 2025 → 16 July 2025**

This ensures everything works perfectly before scaling.


## Step 1 — Data Acquisition & Verification

### **1.1 Selected Dates**
- **15 July 2025 → 16 July 2025**  
- Chosen during monsoon season for strong rainfall variation.

### **1.2 Downloaded Datasets**
All required datasets were downloaded and stored under:
```
data_raw/
├── imc/
├── wdp/
├── lst/
├── cmp/
├── uth/
├── olr/
└── hem/
```

### **Datasets Used**

| Dataset | Product Code      | Frequency   | Role                        |
|---------|-------------------|-------------|-----------------------------|
| IMC     | 3RIMG_L2B_IMC     | Half-hourly | Target rainfall (Y)         |
| WDP     | 3RIMG_L2G_WDP     | Half-hourly | Wind, vorticity, divergence |
| LST     | 3RIMG_L2B_LST     | Half-hourly | Land surface temperature    |
| CMP     | 3RIMG_L2C_CMP     | Half-hourly | Cloud microphysics          |
| UTH     | 3RIMG_L3B_UTH_DLY | Daily       | Upper-tropospheric humidity |
| OLR     | 3RIMG_L3B_OLR_DLY | Daily       | Convection indicator        |
| HEM     | 3RIMG_L3B_HEM_DLY | Daily       | Daily rainfall (auxiliary)  |

Total files downloaded: **336 files**

### **1.3 Verified All 7 Sample Files**
Verified HDF5 structure for:

- IMC  
- WDP  
- LST  
- CMP  
- UTH  
- OLR  
- HEM  

Checked:
- Variables  
- Time stamps  
- Coordinates  
- Spatial dimensions  
- Product consistency  

All files are valid and match MOSDAC standards.

### **1.4 Generated manifest_2d.csv**
Created a complete file manifest containing:

- `product`
- `filename`
- `timestamp`
- `resolution`
- `variables`
- `size_MB`

Saved as:
```
data_processed/manifest_2d.csv
```

This manifest serves as the **master index** for Phase 1 and future phases.


## Step 2 — Spatial Grid & Bounding Box Setup 

### **2.1 Bounding Box Specification (India Region)**
This bounding box is used to generate grid_definition.parquet.
All satellite data is clipped to this region before aggregation.

- Latitude: 6°N → 38°N
- Longitude: 68°E → 98°E

### **2.2 Grid Resolution**
This project uses a uniform spatial grid to aggregate all INSAT-3DR satellite datasets into a consistent reference frame.
- Resolution: 0.25° × 0.25°
- Approx. 25 km × 25 km per cell (varies slightly with latitude)

### **2.3 Generate Latitude & Longitude Sequences**
Used to build the 0.25° × 0.25° India grid.
- Latitude edges: 6.0 → 38.0, step 0.25
- Longitude edges: 68.0 → 98.0, step 0.25

### **2.4 Grid Cell Boundaries**
Grid IDs are assigned row-wise (south → north, west → east).
Each grid cell is defined by 4 boundaries And two midpoints:
- `lat_min`, `lat_max`
- `lon_min`, `lon_max`
- `lat_center`, `lon_center`

### **2.5 Save grid_definition.parquet**
All grid cell boundaries and centers are compiled into
a single Parquet file:
```
data_processed/grid_definition.parquet
```
This file contains:

- grid_id
- lat_min, lat_max
- lon_min, lon_max
- lat_center, lon_center

Total grid cells: 15,360

This file is used by all subsequent stages of the pipeline,
including data aggregation (IMC, WDP, LST, CMP, UTH, OLR, HEM),
model training, and backend prediction services.
---