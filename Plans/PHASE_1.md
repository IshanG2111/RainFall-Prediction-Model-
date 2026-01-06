# Phase 1 — 2-Day Pipeline

Phase 1 validates the entire workflow using **two days of data**:  
**15 July 2025 → 16 July 2025**

This ensures everything works perfectly before scaling.

---

## Step 1 — Data Acquisition & Verification

### **1.1 Selected Dates**
- **15 July 2025 → 16 July 2025**  
- Chosen during monsoon season for strong rainfall variation.

### **1.2 Downloaded Datasets**
All required datasets were downloaded and stored under:

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


### **1.3 Verified All Sample Files**
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

---

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

## Step 4 — MERGE ALL DAILY PRODUCTS INTO ONE DATASET

### **4.1 Load Master Daily Files**
Load all master daily Parquet files and verify their structure and ensure each contains exactly:
- grid_id
- lat_center
- lon_center
- date
- daily aggregated feature (e.g., rain_mm, lst_k, wind_speed, etc.)
This establishes the base input for building the final merged dataset.

### **4.2 Combine All Days into One Continuous Dataset**
Each daily file contains 15,360 grid cells for that date.
This step merges all files vertically into one consolidated dataframe. This combined table becomes the core dataset on which all subsequent preprocessing is performed.

### **4.3 Add Temporal / Seasonal Metadata**
To help machine learning models understand seasonal patterns, several temporal features are added:

| Column       | Meaning                                  |
|--------------|------------------------------------------|
| day          | Day of month                             |
| month        | Month number                             |
| year         | Year (useful for multi-year datasets)    |
| day_of_year  | Numerical day 1–365                      |
| week_of_year | ISO week index                           |
| monsoon_flag | Binary flag (1 for Jun–Sep, 0 otherwise) |
These metadata fields help capture seasonality, monsoon patterns, and weekly cycles.

### **4.4 Validate Target Column (IMC Rainfall)**
IMC rainfall (rain_mm) is the target variable for prediction.
This step verifies:
- No negative rainfall values
- No extreme outliers beyond known physical limits
- All rows contain valid values (IMC grids with missing rainfall were already dropped earlier).

This ensures that the target column is clean and suitable for supervised learning.

### **4.5 Identify Missing Feature Columns**
Even after daily aggregation, certain satellite products naturally contain missing values:
- LST missing under deep clouds
- CMP (CER/COT) missing for retrieval failure
- WDP (wind) missing at edge of domain
- UTH/OLR occasionally missing due to sector gaps

This stage:
- Scans all feature columns
- Flags missing or invalid entries
- Prepares the dataset for structured imputation in Step 4.6

### **4.6 Handle Missing Feature Values (Feature Engineering Logic)**
Each variable has different physical properties, so a custom imputation strategy is used.
#### IMC Rainfall (Target)
- IMC is the target → never imputed
- If IMC rainfall is missing → the entire row is removed

#### Variables Derived from Half-Hourly Data (WDP, LST, CMP)
Missing values arise from cloud obstruction, retrieval failure, or edge-of-domain issues.

A 3-level hierarchical imputation strategy is applied:
1. Spatial Neighbor Median
    - Use nearby 4–8 grid cells on the same day
    - Captures local continuity
   
2. Latitude-Band Median
   - Use values from all cells within the same latitude strip
   - Useful when entire region is cloudy

3. Monthly Climatology
   - Fallback using long-term typical values for that month

4. Physical Range Clipping
   - Ensures all imputed values lie within known valid bounds
   - Example:
      - lst_k in 200–330 K
      - cer in 0–60 µm
      - cot in 0–200

#### Daily Products (UTH, OLR, HEM)
These are already stable daily stats from IMD.
- Missing values replaced using same-day column mean
- Ensures smoothness without distorting physical ranges

This results in a fully filled, physically consistent dataset suitable for ML.

### **4.7 Save Final Merged Dataset**
After all merging, engineering, and imputation:
The final dataframe is saved to

This final dataset has:
- All grid cells for each date 
- Zero missing values 
- Clean, calibrated satellite features 
- Temporal metadata 
- Rainfall target column

Shape of final dataset:
```
(30718 rows, 18 columns)
```
---
## File Structure For Phase 1
```
data_processed/
└── 2_days/
    └── cmp_daily/
        ├── cmp_2025-07-15.parquet
        └── cmp_2025-07-16.parquet
    └── finaldata/
        ├── final_dataset.parquet
    └── hem_daily/
        ├── hem_2025-07-15.parquet
        └── hem_2025-07-16.parquet
    └── imc_daily/
        ├── imc_2025-07-15.parquet
        └── imc_2025-07-16.parquet
    └── lst_daily/
        ├── lst_2025-07-15.parquet
        └── lst_2025-07-16.parquet
    └── master_daily/
        ├── master_raw_2025-07-15.parquet
        └── master_raw_2025-07-16.parquet
    └── olr_daily/
        ├── olr_2025-07-15.parquet
        └── olr_2025-07-16.parquet
    └── uth_daily/
        ├── uth_2025-07-15.parquet
        └── uth_2025-07-16.parquet
    └── wdp_daily/
        ├── wdp_2025-07-15.parquet
        └── wdp_2025-07-16.parquet
└── grid/
    ├── grid_definition.parquet
```