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


## Step 3 — Daily Aggregation of Half-Hourly Data
### **3.1 IMC Daily Processing**
Processes INSAT-3DR IMC rainfall (mm/hr) by reconstructing geolocation from satellite metadata, converting half-hourly rain rates into daily rainfall totals, clipping to the India domain, mapping to the 0.25° India grid, and generating a complete daily rainfall field with 15,360 grid cells.

### **3.2 WDP Daily Processing**
Processes INSAT-3DR WDP wind data (U/V components). Extracts surface-level winds, computes wind speed magnitude, reprojects the WDP grid to the 0.25° India grid, and produces a daily-mean wind speed dataset.

### **3.3 LST Daily Processing**
Processes INSAT-3DR Land Surface Temperature (LST in Kelvin). Reconstructs full-disk geolocation from satellite attributes, clips to India, performs daily averaging of temperature, and maps the dataset onto the unified 0.25° India grid.

### **3.4 CMP Daily Processing**
Processes INSAT-3DR Cloud Microphysics fields. Extracts both Cloud Effective Radius (CER) and Cloud Optical Thickness (COT), applies scale factors, reconstructs geolocation, aligns to the 0.25° grid, and generates daily-mean CER and COT grids.

### **3.5 UTH Daily Processing**
Processes daily Upper Tropospheric Humidity (already binned daily by IMD). Reprojects the satellite grid using metadata, clips to India, maps values onto the 0.25° India grid, and outputs a complete daily UTH field.

### **3.6 OLR Daily Processing**
Processes daily Outgoing Longwave Radiation (OLR). Utilizes INSAT-3DR's daily binned radiative flux product, reconstructs lat/lon grids, maps to the 0.25° India grid, and generates a daily OLR dataset used as a key convective indicator.

### **3.7 HEM Daily Processing**
Processes INSAT-3DR HEM daily precipitation (mm/day). Uses the already-binned daily rainfall total, reconstructs geolocation, maps to the 0.25° grid, and outputs a complete daily rainfall field complementary to IMC.

### **3.8 Merging all datasets**
This step merges all the processed daily satellite products (IMC, WDP, LST, CMP, UTH, OLR, HEM) into a single unified daily dataset. The merge is performed on grid_id and date, producing a complete feature table with 15,360 grid cells per day. No ML-specific preprocessing is done at this stage; the output serves as the raw feature layer for Step 4.

---