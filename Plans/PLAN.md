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

## 🟩 PHASE 2 — 7-DAY PIPELINE (Small Dataset, Early Modeling)

### 🎯 Goal
Process 7 consecutive days of data using your validated pipeline, and prepare a dataset large enough for basic model training.

### 🧩 Key Tasks

1. **Data Acquisition**
   - Download 7 days of all required datasets.

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

## 🟧 PHASE 3 — 15-DAY PIPELINE (Intermediate Scale + Advanced Features)

### 🎯 Goal
Work with a medium-sized dataset to improve the data quality and add meaningful physical features.

### 🧩 Key Tasks

1. **Data Acquisition**
   - Download 15 days of all required datasets.

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
   - Export dataset: `daily_dataset_15d.parquet`.

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

## 🟥 PHASE 4 — FINAL 60–90 DAY PIPELINE (Production Dataset + Deployment)

### 🎯 Goal
Produce the full dataset for final model training + backend integration.

### 🧩 Key Tasks

1. **Data Acquisition**
   - Download 60–90 days of all required datasets.

2. **Data Processing**
   - Run the full, validated pipeline.
   - Add all engineered features from previous phases.

3. **Data Export**
   - Export dataset: `daily_dataset_final.parquet`.

### 📤 Output (for teammates)
1. Final dataset for model training
2. Backend API for predictions
3. Frontend UI for user interaction

### 🎯 Success Criteria
1. Final dataset complete & clean
2. Final model trained
3. API + UI working
4. Project report ready

---

## 🧭 HOW YOU WILL USE THIS MASTER ROADMAP

You will now create 4 new chats, named like:
- ✔ Phase 1: 2-Day Pipeline
- ✔ Phase 2: 7-Day Pipeline
- ✔ Phase 3: 15-Day Pipeline
- ✔ Phase 4: Final Dataset & Deployment

Inside each new chat, say:

> "Give me the detailed roadmap for this phase."

And I'll generate the full detailed per-phase roadmap, including:
- Step-by-step tasks
- Subtasks
- Deliverables
- QC checklists
- Folder structure
- Outputs for teammates

Each phase will stay clean and isolated.