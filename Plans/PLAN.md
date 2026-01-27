# 🚀 MASTER ROADMAP — 4 PHASES (Top-Level Overview)

This acts as your global structure.
Each phase below will become its own dedicated chat.

---

## 🟦 PHASE 1 — 2-DAY PIPELINE (Trial Run + Pipeline Validation)

### 🎯 Goal
Build the entire data pipeline end-to-end using only 2 days of data to ensure everything works without scaling problems.

### 🧩 Key Tasks

1. **Data Acquisition**
   - Order and download 2 days of all required datasets (IMC, WDP, LST, UTH, OLR, HEM, CMP).

2. **Data Processing**
   - Convert all raw data to daily format.
   - Apply India bounding box filtering.
   - Map all data into 0.25° × 0.25° grid cells.
   - Merge into a single daily table.
   - Perform basic cleaning and preprocessing.

3. **Data Export**
   - Export the processed dataset as `daily_dataset_2d.parquet`.

### 📤 Output (for teammate)
A fully functional but small dataset so Teammate 1 can test feature engineering.

### 🎯 Success Criteria
The entire system runs without breaking:
1. Downloads work
2. HDF5 reading works
3. Daily aggregation works
4. Grid mapping works
5. Merging works

This phase is about **pipeline correctness**, not accuracy.

---

## 🟩 PHASE 2 — 8-DAY PIPELINE (Small Dataset, Early Modeling)

### 🎯 Goal
Process 8 different days of data using your validated pipeline, and prepare a dataset large enough for basic model training.

### 🧩 Key Tasks

1. **Data Acquisition**
   - Download 8 days of all required datasets.

2. **Data Processing**
   - Run the already-tested daily conversion & grid mapping.
   - Clean + preprocess.
   - Add basic features:
     - `lag_1`
     - `day_of_year`
     - `month`

3. **Data Export**
   - Export dataset: `daily_dataset_7d.parquet`.

### 📤 Output (for teammates)
Enough samples for:
1. Linear regression
2. Ridge regression
3. Early diagnostic plots

### 🎯 Success Criteria
1. Dataset stable
2. No missing values
3. Feature engineering starts producing patterns
4. Model begins learning something non-random

---

## 🟧 PHASE 3 — 90-DAY PIPELINE (Advanced Features)

### 🎯 Goal
Work with a large-sized dataset to improve the data quality and add meaningful physical features.

### 🧩 Key Tasks

1. **Data Acquisition**
   - Download 90 days of all required datasets.

2. **Data Processing**
   - Run the full pipeline (now stable from Phases 1 & 2).
   - Add advanced features:
     - `rolling_3_day_mean`
     - `lag_3`
     - `wind_shear`
     - `vorticity components`
     - `divergence`
     - `seasonality flags`

3. **Data Export**
   - Export dataset: `daily_dataset_90d.parquet`.

### 📤 Output (for teammates)
Enough size for:
1. Model stability testing
2. Cross-validation with time splits
3. Spatial validation

### 🎯 Success Criteria
1. Features behave physically correctly
2. Model accuracy improves from Phase 2
3. No bottlenecks in preprocessing

---
Each phase will stay clean and isolated.