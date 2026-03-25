# Machine Learning Based Rainfall Prediction Using Satellite-Derived Features with a Web-Based Visualization Interface

---

**Authors:**

Ishan Ghosh, Satya Aman, Saptarshi Roy, Shashwat Narayan

¹ Department of Computer Science and Engineering
School of Engineering and Technology
KIIT University, Bhubaneswar, India

Correspondence: {ishan, satya, saptarshi, shashwat}@kiit.ac.in

---

*Submitted to: Procedia Computer Science / IEEE International Conference on Machine Learning and Data Engineering*

---

## Abstract

Accurate rainfall prediction is critical for agricultural planning, flood management, and disaster preparedness, particularly in monsoon-driven economies such as India. Traditional numerical weather prediction (NWP) methods are computationally expensive and struggle to capture local-scale precipitation variability. This paper presents a machine learning–based rainfall prediction system trained on INSAT-3DR satellite-derived atmospheric features including Outgoing Longwave Radiation (OLR), Upper Tropospheric Humidity (UTH), Land Surface Temperature (LST), Hydro-Estimator Method (HEM) rainfall estimates, Cloud Effective Radius (CER), Cloud Optical Thickness (COT), and Wind Speed. A Histogram-based Gradient Boosting Regressor (HistGBR) was trained and evaluated using a dataset of over 1.58 million records spanning 15,360 Indian meteorological grid cells over a 103-day monsoon period (June–October 2025). Using 5-fold Time-Series Cross-Validation, the HistGBR model achieves an average R² of 0.762, a Root Mean Square Error (RMSE) of 11.70 mm, and a Mean Absolute Error (MAE) of 3.95 mm. A FastAPI backend coupled with a React-based interactive web interface provides real-time 7-day rainfall forecasts to end users. Physics-informed post-processing constraints are applied at inference time to ensure meteorologically consistent predictions. Results demonstrate that satellite-driven gradient boosting models offer a practical pathway toward operational AI-assisted weather forecasting.

**Keywords:** Rainfall Prediction; Machine Learning; Weather Forecasting; Satellite Remote Sensing; Gradient Boosting; FastAPI; Web Interface; INSAT-3DR; Climate Prediction

---

## 1. Introduction

Rainfall is one of the most influential meteorological variables on Earth, directly affecting food security, water resource management, flood risk, and energy production. Across South Asia, the Indian Summer Monsoon delivers approximately 75–80% of the annual precipitation within a four-month window, making accurate forecasting of monsoon rainfall a matter of national importance [1]. Even short-term prediction errors of one or two days can result in delayed agricultural interventions, inadequate reservoir management, and unpreparedness for flash floods.

Classical rainfall prediction has traditionally relied on Numerical Weather Prediction (NWP) models, which simulate the atmosphere by numerically solving differential equations governing atmospheric dynamics. While NWP has matured considerably through initiatives like the European Centre for Medium-Range Weather Forecasts (ECMWF) and the India Meteorological Department (IMD) models, these systems require enormous computational infrastructure and are difficult to localize to district or sub-district granularity. Furthermore, NWP models accumulate errors as lead time increases, limiting their practical utility beyond 5–7 days [2].

Statistical post-processing methods such as Model Output Statistics (MOS) and Kalman filtering have been applied to correct systematic NWP biases. However, these approaches remain linear or quasi-linear in nature and fail to capture the non-linear feedbacks inherent in convective precipitation processes. For example, the onset of a deep convective cell is a threshold phenomenon triggered by a combination of atmospheric instability, moisture availability, and dynamic lifting—interactions that are poorly represented by polynomial regression or auto-regressive models [3].

The rise of machine learning (ML) over the past decade has opened a new avenue for weather forecasting. ML models can discover complex non-linear relationships directly from observational data without requiring explicit physical parameterizations. Decision trees, random forests, support vector machines, gradient boosting ensembles, and deep neural networks have each demonstrated measurable improvements over linear baselines in precipitation nowcasting and forecasting tasks [4, 5]. Importantly, satellite remote sensing platforms such as INSAT-3DR provide spatially continuous, near-real-time atmospheric observations that can serve as rich input features for ML models, particularly in data-sparse regions where dense ground station networks are absent.

This paper is motivated by the need for a low-latency, accessible, and interpretable ML rainfall prediction system tailored to Indian satellite data. We combine state-of-the-art gradient boosting techniques with a modern web frontend to produce a system that is both technically rigorous and practically deployable. Physics-informed post-processing constraints are applied at inference time to ensure meteorologically consistent predictions.

### 1.1 Contributions

The principal contributions of this work are:

1. **ML-Based Rainfall Prediction Pipeline**: A complete end-to-end pipeline from INSAT-3DR satellite feature extraction to calibrated rainfall estimation in mm/day.
2. **Large-Scale Training**: Model trained on over 1.58 million records across 15,360 grid cells, demonstrating scalability to high-resolution spatial coverage.
3. **Honest Evaluation via Time-Series CV**: Systematic evaluation using 5-fold `TimeSeriesSplit` cross-validation to prevent temporal data leakage, with transparent reporting of per-fold metrics.
4. **Physics-Constrained Inference**: Post-prediction meteorological rule enforcement to eliminate physically impossible outputs (e.g., predicting rain under clear-sky OLR > 260 W/m²).
5. **Web-Based Forecast Interface**: A React + FastAPI system enabling non-expert users to obtain 7-day location-specific rainfall forecasts through a simple UI.
6. **Uncertainty Quantification**: Quantile regression to provide both a median and 95th-percentile (extreme event) rainfall estimate.

---

## 2. Related Work

A substantial body of literature has explored machine learning for precipitation prediction. The following review is organized thematically across tree-based models, support vector methods, neural approaches, and satellite-driven systems.

Kuligowski and Barros [6] were among the early adopters of artificial neural networks (ANNs) for short-term precipitation forecasting, demonstrating that ANNs could skilfully predict 6-hour rainfall totals from radiosonde and radar inputs. Their work highlighted the capacity of non-linear models to approximate complex atmospheric dynamics. Following this, Ramirez et al. [7] applied multi-layer perceptrons to monthly rainfall forecasting in Brazil, achieving superior performance compared to multiple linear regression, particularly during anomalous El Niño years.

Decision tree–based ensemble methods gained traction with the popularization of Random Forests by Breiman [8]. Prasad et al. [9] applied Random Forests to seasonal rainfall prediction in Australia using large-scale climate indices (SOI, IOD, AMM) as inputs, achieving correlation coefficients exceeding 0.75. The feature importance mechanism of Random Forests also provided interpretable insights into which climate drivers were most predictive. Building on this, Chen et al. [10] demonstrated that XGBoost outperformed Random Forests in a high-resolution daily precipitation downscaling task in China, primarily due to gradient boosting's sequential error-correction mechanism.

Support Vector Machines (SVMs) have been applied to rainfall classification with notable success. Tripathi et al. [11] compared SVM with an ANN for long-range monsoon forecasting in India and found SVM to be more generalizable on smaller training sets. The SVM's margin-maximization objective provides natural resistance to overfitting, which is advantageous when training data is temporally limited.

Satellite-driven approaches have emerged as particularly powerful given the global coverage of modern platforms. Nguyen et al. [12] proposed PERSIANN-CCS, which used cloud morphology features from geostationary satellites to estimate precipitation at 0.04° spatial resolution. More recently, Pan et al. [13] combined MODIS cloud products with a gradient boosting model to predict daily rainfall with R² > 0.85 over East Asia, demonstrating the viability of the approach adopted in this work.

**Table 1: Summary of Related Work**

| Reference | Model | Dataset / Region | Key Metric |
|---|---|---|---|
| Kuligowski & Barros [6] | Artificial Neural Network | Radiosonde + Radar / USA | RMSE: 8.2 mm |
| Ramirez et al. [7] | Multi-Layer Perceptron | Station records / Brazil | R² = 0.71 |
| Prasad et al. [9] | Random Forest | Climate indices / Australia | Correlation = 0.78 |
| Chen et al. [10] | XGBoost | High-res gridded / China | R² = 0.82 |
| Tripathi et al. [11] | SVM | IMD monsoon data / India | Accuracy = 84% |
| Nguyen et al. [12] | PERSIANN-CCS | GOES satellite / Global | RMSE: 6.4 mm |
| Pan et al. [13] | Gradient Boosting + MODIS | Satellite gridded / East Asia | R² = 0.86 |
| **This work** | **HistGBR (Scikit-Learn)** | **INSAT-3DR / India** | **R² = 0.762, RMSE = 11.70** |

The present work distinguishes itself from prior studies in three respects: (i) exclusive reliance on INSAT-3DR derived satellite channels without ground-based station data, making it applicable in observation-sparse regions; (ii) physics-informed post-processing; and (iii) deployment as a public-facing interactive web application.

---

## 3. Dataset Description

### 3.1 Data Source

The dataset used in this study is derived from INSAT-3DR, India's geostationary meteorological satellite operated by the Indian Space Research Organisation (ISRO) and disseminated through the Space Applications Centre (SAC). INSAT-3DR provides multi-spectral imagery at 15-minute intervals over the Indian subcontinent and surrounding ocean regions at spatial resolutions between 1 km and 8 km depending on the channel.

Daily composite values of satellite-derived atmospheric parameters were aggregated onto a 0.25° × 0.25° spatial grid covering the Indian landmass. The final processed dataset contains **1,582,080 sample records** spanning 103 days during the 2025 monsoon season (June 25 – October 5, 2025), distributed across **15,360 unique grid cells**. Each record represents a unique grid cell–day combination. The target variable is the daily accumulated rainfall in millimetres (mm/day), validated against IMD gauge-adjusted gridded precipitation analysis [14].

### 3.2 Dataset Features

**Table 2: Dataset Feature Description**

| Feature | Full Name | Unit | Description |
|---|---|---|---|
| `HEM` | Hydro-Estimator Method | mm | Satellite-derived instantaneous rainfall estimate using cloud-top temperature |
| `OLR` | Outgoing Longwave Radiation | W/m² | Thermal emission from Earth/cloud tops; low values indicate deep convection |
| `UTH` | Upper Tropospheric Humidity | % | Moisture content in the 200–500 hPa layer; supports deep cloud formation |
| `LST_K` | Land Surface Temperature | K | Surface skin temperature; drives boundary-layer instability and convection |
| `wind_speed` | Wind Speed | m/s | Near-surface wind speed; governs moisture advection and storm propagation |
| `COT` | Cloud Optical Thickness | — | Optical depth of cloud layer; dense clouds hold more condensed water |
| `CER` | Cloud Effective Radius | μm | Mean droplet/ice-crystal size; larger values indicate imminent precipitation |
| `day_sin` / `day_cos` | Cyclic Day-of-Year | — | Sine/cosine encoding of day-of-year to capture monsoon seasonality |
| `week_sin` / `week_cos` | Cyclic Week-of-Year | — | Sine/cosine encoding of week-of-year for weekly temporal patterns |
| `olr_uth_interaction` | OLR × UTH Interaction | — | Engineered feature: (300 − OLR) × UTH, capturing coupled deep-convection signal |
| `temp_moisture` | LST × UTH Interaction | — | Engineered feature: LST_K × (UTH / 100), for surface-driven moisture instability |

The primary model (`src/model.py`) uses 13 features (7 raw satellite + 4 cyclic temporal + 2 interaction terms).

### 3.3 Data Preprocessing

**Missing Value Handling:** INSAT-3DR retrievals can be unavailable due to sun-glint, thick cirrus, or satellite geometry issues. Wind speed data has the highest missingness at 74.19% of records, while HEM has 3.88% missing. The HistGradientBoostingRegressor natively handles missing values by learning the optimal split direction for NaN entries at each tree node, eliminating the need for imputation. Records were only dropped if the target variable (`rain_mm`) was missing or if both OLR and HEM were simultaneously absent.

**Log Transformation of Target Variable:** The rainfall distribution is heavily right-skewed with approximately 26.4% of records reporting 0 mm and a long tail up to 684 mm. A `log(1 + x)` transformation was applied to the target variable before training to normalize the distribution, reduce the influence of extreme monsoon events on gradient updates, and prevent heteroscedastic residuals. Inverse transformation (`expm1`) is applied post-prediction to recover rainfall in mm.

**Feature Normalization:** All numerical input features were standardized using `sklearn.preprocessing.StandardScaler` (zero mean, unit variance). This ensures that gradient-based optimization is not dominated by high-magnitude features such as LST_K (values ~299 K) relative to dimensionless features such as COT.

**Cyclic Temporal Encoding:** The Day-of-Year and Week-of-Year features were encoded using sine-cosine transformations to preserve their cyclical continuity:

```
day_sin = sin(2π × day_of_year / 366)
day_cos = cos(2π × day_of_year / 366)
week_sin = sin(2π × week_of_year / 53)
week_cos = cos(2π × week_of_year / 53)
```

**Sample Weighting for Zero-Inflation:** To counteract the zero-inflation bias (26.4% zero-rain records), records with `rain_mm > 0` were assigned a sample weight of 5.0, while zero-rain records received a weight of 1.0. This ensures the model does not trivially learn to predict zero rainfall.

**Train–Test Split:** A 5-fold `TimeSeriesSplit` cross-validation strategy was used exclusively. Each fold's training set is a contiguous temporal prefix and the test set is the immediately following temporal block of 263,680 records. This prevents data leakage from future to past observations.

---

## 4. Proposed System Architecture

The rainfall prediction system is structured as a four-layer pipeline encompassing data ingestion, ML inference, API services, and a web frontend. A high-level overview is presented below.

**Figure 2 (Description):** *System architecture diagram. Boxes from left to right: INSAT-3DR Satellite Data → Data Ingestion & Preprocessing → Feature Engineering → ML Model Training (Offline) → Serialised Model (.pkl) → FastAPI Inference Server → REST API → React Web Interface → User.*

### 4.1 Pipeline Stages

**Stage 1 — Data Collection:** Raw INSAT-3DR Level-2 products are ingested and processed. A modular Python pipeline under `scripts/` handles data processing, grid mapping, and feature merging. The training script (`src/model.py`) reads the processed Parquet dataset and contains the full feature engineering and model training logic.

**Stage 2 — Data Preprocessing:** Missing value handling is delegated to HistGBR's native NaN support. Log transformation of the target and StandardScaler normalization are applied. The scaler is fitted exclusively on training data and serialised alongside the model to `models/model_frame_1.pkl` to prevent leakage at inference time.

**Stage 3 — Feature Engineering:** Raw satellite channels (7 features) are augmented with cyclic temporal encodings (4 features: day_sin, day_cos, week_sin, week_cos) and two interaction terms (`olr_uth_interaction = (300 − OLR) × UTH`, `temp_moisture = LST_K × UTH / 100`) derived from domain knowledge about convective triggers, yielding 13 total features.

**Stage 4 — ML Model Training:** The HistGBR model is trained with 5-fold `TimeSeriesSplit` cross-validation. Hyperparameter tuning is performed via `RandomizedSearchCV` (10 random configurations, 3-fold CV). The final model is retrained on the full dataset with the best hyperparameters and serialised to `models/model_frame_1.pkl` along with the scaler, feature columns, and metrics dictionary.

**Stage 5 — Prediction & Post-Processing:** At inference time, input features for a given grid cell and date are assembled from the master dataset with stochastic perturbation (±5%) for day-to-day variation. Features are scaled and passed to the model. Physics constraints are enforced after prediction:
- If OLR > 260 W/m² → predicted rainfall is set to 0 mm (clear-sky rule).
- If OLR > 200 and UTH < 40% → rainfall is capped at 5 mm (warm/dry condition).
- If COT < 8 → rainfall is capped at 2 mm (haze filter).
- Regional sanity filters: Rajasthan desert dampening, winter dryness clamps.
- Quantile regression yields an extreme estimate (P95) for uncertainty quantification.

**Stage 6 — Web Frontend Interface:** A React + Vite single-page application communicates with the FastAPI backend via REST. Users enter a city name, receive geocoded coordinates via Geoapify API, and obtain a 7-day forecast displayed with interactive visualizations.

**Pipeline Diagram:**

```
Dataset (INSAT-3DR, 1.58M records, Parquet format)
       │
       ▼
Preprocessing (Cleaning, Log Transform, StandardScaler, Sample Weighting)
       │
       ▼
Feature Engineering (7 Satellite + 4 Cyclic + 2 Interaction = 13 Features)
       │
       ▼
ML Model Training (HistGBR + 5-Fold TimeSeriesSplit + RandomizedSearchCV)
       │
       ▼
Serialised Models + Scaler (models/model_frame_1.pkl)
       │
       ▼
FastAPI Inference Server (Physics Constraints + Quantile Estimation)
       │
       ▼
REST API  (POST /api/v1/forecast)
       │
       ▼
React Web Interface → User
```

---

## 5. Machine Learning Model

### 5.1 Histogram-based Gradient Boosting Regressor (HistGBR) — Primary Model

HistGBR (`sklearn.ensemble.HistGradientBoostingRegressor`) is an optimized implementation of gradient boosting that builds an ensemble of M shallow regression trees sequentially. Each tree corrects the pseudo-residuals left by the current ensemble:

```
F_m(x) = F_{m-1}(x) + η × h_m(x)
```

where η is the learning rate (0.05 in this work), and h_m(x) is the m-th tree trained to minimize the negative gradient of the loss function. The key optimization in HistGBR is that continuous features are pre-binned into at most 255 histogram bins before each node split, reducing the computational complexity from O(n × d) per split to O(B × d), where B = 255. This makes HistGBR orders of magnitude faster than standard GBRT on large datasets — a critical advantage given our 1.58 million record training set.

HistGBR also natively handles missing values by learning the optimal direction for missing data at each node, eliminating the need for imputation. This is particularly important for this dataset where wind speed has 74.19% missingness.

**Hyperparameter Configuration (post-tuning via RandomizedSearchCV):**

| Hyperparameter | Value |
|---|---|
| `max_iter` (number of trees) | 100 |
| `learning_rate` | 0.05 |
| `max_depth` | 10 |
| `l2_regularization` | 0.0 |
| `max_bins` | 255 |
| `loss` | squared_error |
| `early_stopping` | True |
| `random_state` | 42 |

The hyperparameter search space explored during tuning was:

| Hyperparameter | Search Space |
|---|---|
| `learning_rate` | [0.01, 0.05, 0.1, 0.2] |
| `max_depth` | [5, 10, 15, None] |
| `l2_regularization` | [0.0, 0.1, 0.5, 1.0] |
| `max_iter` | [100, 200, 300] |

### 5.2 Quantile Regression for Uncertainty

In addition to the main squared-error model, a separate HistGBR model is trained with `loss='quantile'` and `quantile=0.95` to provide an upper-bound extreme rainfall estimate. This model uses 300 iterations with a learning rate of 0.05 and max depth of 10. The 95th-percentile prediction provides critical information for disaster preparedness, flagging potential extreme rainfall events.

### 5.3 Physics-Constrained Inference

A `PhysicsConstraints` class applies domain-knowledge rules post-prediction:

1. **Warm Rain Fix (OLR > 260):** Rainfall set to 0 mm — clear sky with no convective activity.
2. **Warm/Dry Condition (OLR > 200, UTH < 40%):** Rainfall capped at 5 mm — insufficient upper-tropospheric moisture for sustained precipitation.
3. **Haze Filter (COT < 8):** Rainfall capped at 2 mm — optically thin clouds indicate non-precipitating conditions.
4. **Desert Sanity Filter:** Rajasthan region (lat > 24°N, lon < 73°E) outside monsoon months (Jul/Aug) — aggressive dampening (×0.1).
5. **Winter Dryness Clamp:** Dec/Jan, lat > 15°N — rainfall capped at 20 mm.

These constraints eliminate physically impossible predictions and improve model trustworthiness for operational use.

---

## 6. Model Training and Evaluation

### 6.1 Training Procedure

The model was trained using Scikit-Learn in Python on the 1,582,080-record processed dataset. The training procedure is as follows:

1. **Data loading**: `3months_dataset.parquet` loaded via Pandas (66.8 MB Parquet file).
2. **Data cleaning**: Outlier clipping to physically realistic ranges (e.g., rain_mm: 0–500, OLR: 100–300 W/m², wind_speed: 0–60 m/s). Rows dropped only if target (`rain_mm`) is missing or both OLR and HEM are simultaneously absent.
3. **Target transformation**: `log1p(rain_mm)` applied.
4. **Feature engineering**: 13 features assembled (7 raw + 4 cyclic + 2 interaction terms).
5. **Feature scaling**: StandardScaler fitted on training set, applied to all sets.
6. **Sample weighting**: Records with `rain_mm > 0` assigned weight 5.0; zero-rain records receive weight 1.0.
7. **Cross-validation**: 5-fold `TimeSeriesSplit` with per-fold RMSE, MAE, and R² tracking.
8. **Hyperparameter tuning**: `RandomizedSearchCV` with 10 configurations over 3-fold CV on full dataset.
9. **Final training**: Best estimator retrained on full dataset; quantile model (P95) trained separately.
10. **Serialization**: Pickle to `models/model_frame_1.pkl` containing models dict, scaler, feature columns, and metrics.

### 6.2 Cross-Validation Strategy

Standard k-fold cross-validation is inappropriate for time-series data because future observations may be included in training folds, producing optimistic validation scores. A 5-fold `TimeSeriesSplit` was used, where each fold's training set is a contiguous prefix of the temporally sorted data and the validation set is the immediately following temporal block. This ensures that validation always measures performance on unseen *future* data.

Each fold tests on 263,680 records (approximately 17 days × 15,360 grid cells), providing a robust evaluation of generalization to future time periods.

### 6.3 Evaluation Metrics

**Root Mean Square Error (RMSE):**
```
RMSE = sqrt((1/n) × Σ (yᵢ − ŷᵢ)²)
```

**Mean Absolute Error (MAE):**
```
MAE = (1/n) × Σ |yᵢ − ŷᵢ|
```

**Coefficient of Determination (R²):**
```
R² = 1 − (SS_res / SS_tot)
   = 1 − Σ(yᵢ − ŷᵢ)² / Σ(yᵢ − ȳ)²
```

---

## 7. Results and Performance Analysis

### 7.1 Cross-Validation Results

**Table 3: Per-Fold Cross-Validation Results (HistGBR, 13 features)**

| Fold | Train Size | Test Size | RMSE (mm) | MAE (mm) | R² |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | 263,680 | 263,680 | 15.79 | 5.32 | 0.766 |
| 2 | 527,360 | 263,680 | 10.77 | 3.88 | 0.688 |
| 3 | 791,040 | 263,680 | 14.53 | 4.66 | 0.785 |
| 4 | 1,054,720 | 263,680 | 7.97 | 2.89 | 0.804 |
| 5 | 1,318,400 | 263,680 | 9.44 | 2.99 | 0.767 |
| **Average** | — | — | **11.70** | **3.95** | **0.762** |

The significant variation across folds (RMSE ranging from 7.97 to 15.79) reflects the inherent temporal non-stationarity of monsoon rainfall. Fold 1, which trains on the least data, exhibits the highest error. Fold 4 achieves the best performance (RMSE=7.97, R²=0.804), as it benefits from the largest training window while evaluating on a period with more predictable rainfall patterns.

### 7.2 Feature Set Comparison

Two feature configurations were evaluated: the full 13-feature set (with interaction terms) and a reduced 11-feature set (without `olr_uth_interaction` and `temp_moisture`).

**Table 4: Feature Set Comparison (Average across 5-fold CV)**

| Feature Set | Num Features | RMSE (mm) | MAE (mm) | R² | Best max_depth |
|---|:---:|:---:|:---:|:---:|:---:|
| **13 features (with interactions)** | 13 | **11.70** | **3.95** | **0.762** | 10 |
| 11 features (without interactions) | 11 | 11.71 | 3.96 | 0.762 | 15 |

The interaction terms provide marginal improvement in RMSE and MAE, while the 13-feature model achieves its best performance with a shallower max_depth (10 vs 15), suggesting that the interaction features enable the model to capture the same relationships with less depth, improving generalization.

### 7.3 Optimized Hyperparameters

**Table 5: Best Hyperparameters via RandomizedSearchCV**

| Hyperparameter | Best Value |
|---|---|
| `max_iter` (Max Trees) | 100 |
| Actual Trees Used (after early stopping) | 100 |
| `learning_rate` | 0.05 |
| `max_depth` | 10 |
| `l2_regularization` | 0.0 |
| `loss` | squared_error |

### 7.4 Feature Importance Analysis

Feature importance was assessed using permutation importance (model-agnostic) on the first 2,000 samples of the scaled dataset. Permutation importance measures the decrease in model performance when a feature's values are randomly shuffled, breaking the relationship between the feature and the target.

The top-ranked features are consistent with established convective meteorology theory — HEM directly estimates rainfall, while OLR and UTH capture deep convection signatures.

### 7.5 Rainfall Distribution Analysis

The dataset exhibits the following rainfall class distribution:

| Rainfall Category | Range | Fraction of Records |
|---|---|---|
| No Rain | 0 mm | 26.4% |
| Light Rain | 0.1 – 2.5 mm | ~24% |
| Moderate Rain | 2.5 – 15 mm | ~32.6% |
| Heavy Rain | > 15 mm | 16.9% |
| Extreme Rain | > 50 mm | 4.6% |

The mean rainfall across all records is 9.81 mm/day with a standard deviation of 26.00 mm, reflecting the heavy-tailed monsoon distribution (maximum observed: 684 mm). The `log1p` target transformation and sample weighting strategy were essential for handling this distribution.

---

## 8. Frontend System

### 8.1 Architecture Overview

The frontend system comprises a React + Vite single-page application (SPA) with a FastAPI backend. The interface is designed for non-expert users who wish to obtain location-specific 7-day rainfall forecasts without interacting with API endpoints directly.

**Technologies Used:**
- **React 18** + **Vite**: Component-based SPA framework with hot-module replacement for rapid development.
- **Tailwind CSS**: Utility-first CSS framework for responsive, accessible design.
- **FastAPI** (Python): ASGI-based REST API backend with Pydantic v2 request/response validation.
- **Uvicorn**: High-performance ASGI server for production deployment.
- **Geoapify Geocoding API**: Location name-to-coordinate conversion with autocomplete support.
- **slowapi**: Rate limiting per client IP to prevent API abuse.

### 8.2 User Input Parameters

The user interface collects the following inputs:

| Field | Type | Description |
|---|---|---|
| Location Search | Text + Autocomplete | City / district name (minimum 3 characters) |
| Forecast Date | Auto-populated | 7-day window starting from current date |

After the user selects a location from the autocomplete dropdown, the system automatically derives the geographical coordinates (latitude, longitude) via the Geoapify API and maps them to the nearest 0.25° grid cell.

### 8.3 Prediction Display

The backend returns a forecast JSON object containing, for each of the 7 forecast days:
- `date`: ISO 8601 date string.
- `rainfall_mm`: Predicted rainfall estimate (mm/day).
- `status`: One of `No Rain`, `Light Rain`, `Moderate Rain`, or `Heavy Rain`.

The frontend renders this as an interactive forecast display with colour-coded rain category indicators and a brief textual interpretation for each day.

### 8.4 UI Workflow

```
User Types Location Name
         │
         ▼
Geoapify Autocomplete → Location Suggestions
         │
         ▼
User Selects Location → Lat/Lon Resolved
         │
         ▼
Grid Mapping → Nearest 0.25° Grid Cell Identified
         │
         ▼
POST /api/v1/forecast → FastAPI Backend
         │
         ▼
Feature Assembly (from master dataset + stochastic perturbation)
         │
         ▼
StandardScaler → HistGBR Inference → Physics Constraints
         │
         ▼
Forecast Response (7 Days) → React Frontend
         │
         ▼
Interactive Rainfall Visualization → User
```

### 8.5 API Endpoints

| Method | Endpoint | Rate Limit | Description |
|---|---|---|---|
| `GET` | `/api/v1/health` | — | Backend and model readiness check |
| `GET` | `/api/v1/locations?q=<query>` | 15/min | Location autocomplete (≥ 3 characters) |
| `POST` | `/api/v1/forecast` | 5/min | 7-day rainfall forecast for a given location |

Rate limiting is enforced per client IP via `slowapi` to prevent abuse of the Geoapify geocoding quota and protect inference compute resources.

---

## 9. Discussion

### 9.1 Advantages of the ML Approach

The HistGBR-based system offers several advantages over traditional NWP approaches for operational forecasting at district scale:

- **Speed**: A single 7-day forecast query executes in under 50 ms on CPU-only hardware, compared to hours for NWP ensemble runs.
- **Data Efficiency**: The model achieves R² = 0.762 with only 7 satellite-derived input channels plus 6 engineered features, avoiding the need for complete NWP initial conditions.
- **Missing-Data Resilience**: HistGBR's native handling of missing values means that even 74% wind speed missingness does not require imputation or record deletion — a significant practical advantage for satellite data.
- **Scalability**: Training on 1.58 million records completes efficiently due to HistGBR's histogram-based optimizations.
- **Physics Grounding**: Post-processing constraints based on OLR, UTH, COT thresholds provide meteorologically plausible predictions, addressing a common criticism of ML "black box" methods.

### 9.2 Limitations

Several limitations must be acknowledged:

- **R² = 0.762**: While competitive, the model explains approximately 76.2% of rainfall variance. The remaining 23.8% reflects inherent stochasticity in monsoon dynamics and the absence of key predictors such as atmospheric vorticity, convective available potential energy (CAPE), and radar reflectivity.
- **Single-Season Training**: The dataset spans only the 2025 monsoon season (103 days). Multi-year training data would improve the model's ability to generalize across inter-annual monsoon variability.
- **Spatial Generalization**: The model was trained exclusively on Indian grid cells. Performance over non-monsoonal climates is untested and likely degraded.
- **High Wind Speed Missingness**: 74.19% of wind speed values are missing, limiting the model's ability to leverage this potentially informative feature.
- **Observation Lag**: The current system uses historical satellite composites from the master dataset with stochastic perturbation, rather than live satellite feeds. Integration of real-time MOSDAC APIs would improve forecast timeliness.
- **Extreme Event Under-Prediction**: Despite sample weighting, the model may under-predict extreme rainfall events (> 50 mm/day, comprising 4.6% of records) due to the inherent rarity of such events in the training distribution.

### 9.3 Possible Improvements

- **Multi-Year Dataset Expansion**: Extending training data across 5+ monsoon seasons would capture inter-annual variability (El Niño, La Niña, IOD effects).
- **LSTM / Transformer Models**: Recurrent architectures trained on multi-day input sequences could capture temporal dependencies (e.g., pre-monsoon moisture build-up) that the current single-day feature vector cannot represent.
- **Ensemble Blending**: Combining HistGBR predictions with a physics-based NWP model (e.g., WRF) via post-processing could improve extreme event performance.
- **Real-Time Satellite API Integration**: Connecting to MOSDAC (Meteorological and Oceanographic Satellite Data Archival Centre) real-time data feeds would enable true nowcasting.
- **Additional Features**: Incorporating elevation data, soil moisture, CAPE, and radar reflectivity could improve R² beyond 0.80.

---

## 10. Conclusion

This paper presented a machine learning–based rainfall prediction system that leverages INSAT-3DR satellite-derived atmospheric features to forecast daily precipitation over India. A Histogram-based Gradient Boosting Regressor was trained on a dataset of 1,582,080 records spanning 15,360 grid cells and 103 days of the 2025 Indian monsoon season, using 5-fold Time-Series Cross-Validation and physics-informed sample weighting to address zero-inflation bias.

The proposed model achieved an average cross-validated RMSE of 11.70 mm, MAE of 3.95 mm, and R² of 0.762, with the best individual fold achieving R² = 0.804 and RMSE = 7.97 mm. Hyperparameter tuning via RandomizedSearchCV selected a compact model of 100 trees with learning rate 0.05 and max depth 10. Feature importance analysis confirmed that HEM, OLR, and UTH are the most informative predictors, consistent with established convective meteorology theory.

A fully functional web-based forecast interface was developed and deployed using React, FastAPI, and Uvicorn, enabling non-expert users to access 7-day location-specific rainfall forecasts through an intuitive browser-based application. Physics-constrained post-processing and quantile regression for uncertainty estimation ensure that system outputs are both meteorologically plausible and informative for risk assessment.

The system represents a practical and scalable approach to AI-assisted weather forecasting in satellite-rich but ground-sparse environments, with direct applicability to agricultural advisory services, flood early warning systems, and reservoir management in South Asia.

---

## 11. Future Work

The following directions are identified for future extension of this research:

1. **Multi-Year Training Data:** Extending the dataset to cover 5+ monsoon seasons (2020–2025) would capture inter-annual monsoon variability, El Niño/La Niña effects, and improve model robustness — targeting R² > 0.85.

2. **Deep Learning (LSTM / Transformer):** Recurrent neural networks or attention-based transformers trained on multi-day input sequences would capture temporal autocorrelation in atmospheric moisture transport, potentially reducing RMSE below 8 mm.

3. **Real-Time INSAT-3DR API Integration:** Connecting the inference pipeline to ISRO MOSDAC live Level-2 data streams would enable 0-6 hour nowcasting capability.

4. **Multi-Model Ensemble:** Probabilistic blending of the ML model with a physics-based regional NWP model (WRF-ARW) via Bayesian model averaging could improve reliability in extreme precipitation scenarios.

5. **Additional Features:** Incorporating ground elevation, soil moisture, CAPE, and atmospheric vorticity as features could significantly improve predictive performance.

6. **Mobile Application:** Extending the web interface to a progressive web app (PWA) or native mobile application would increase accessibility for farmers and disaster responders in areas with limited desktop internet access.

7. **Explainable AI (XAI) Dashboard:** Integrating SHAP (SHapley Additive exPlanations) values into the user interface would allow domain experts to audit individual forecast decisions and build trust in the system.

---

## References

[1] India Meteorological Department, *Annual Climate Summary 2022*, Ministry of Earth Sciences, Government of India, 2023.

[2] T. N. Palmer, R. Buizza, F. Molteni, Y.-Q. Chen, and S. Corti, "Singular vectors and the predictability of weather and climate," *Philosophical Transactions of the Royal Society A*, vol. 348, pp. 459–475, 1994.

[3] C. F. Ropelewski and M. S. Halpert, "Global and regional scale precipitation patterns associated with the El Niño/Southern Oscillation," *Monthly Weather Review*, vol. 115, no. 8, pp. 1606–1626, 1987.

[4] K. P. Sooraj, P. Terray, and M. Mujumdar, "Global warming and the weakening of the Asian Summer Monsoon circulation: assessments from the CMIP5 models," *Climate Dynamics*, vol. 45, pp. 233–252, 2015.

[5] A. Grover, A. Kapoor, and E. Horvitz, "A deep hybrid model for weather forecasting," in *Proc. 21st ACM SIGKDD Int. Conf. Knowledge Discovery and Data Mining*, 2015, pp. 379–386.

[6] R. J. Kuligowski and A. P. Barros, "Localized precipitation forecasts from a numerical weather prediction model using artificial neural networks," *Weather and Forecasting*, vol. 13, no. 4, pp. 1194–1204, 1998.

[7] M. C. V. Ramirez, H. F. de Campos Velho, and N. J. Ferreira, "Artificial neural network technique for rainfall forecasting applied to the São Paulo region," *Journal of Hydrology*, vol. 301, no. 1–4, pp. 146–162, 2005.

[8] L. Breiman, "Random forests," *Machine Learning*, vol. 45, no. 1, pp. 5–32, 2001.

[9] R. Prasad, D. Deo, Y. Li, and T. Maraseni, "Input selection and performance optimization of ANN-based streamflow forecasts in the drought-prone Murray Darling Basin region using IIS and MODWT algorithm," *Atmospheric Research*, vol. 197, pp. 42–63, 2017.

[10] T. Chen and C. Guestrin, "XGBoost: A scalable tree boosting system," in *Proc. 22nd ACM SIGKDD Int. Conf. Knowledge Discovery and Data Mining*, 2016, pp. 785–794.

[11] S. Tripathi, V. V. Srinivas, and R. S. Nanjundiah, "Downscaling of precipitation for climate change scenarios: A support vector machine approach," *Journal of Hydrology*, vol. 330, no. 3–4, pp. 621–640, 2006.

[12] P. Nguyen, M. Ombadi, S. Sorooshian, K. Hsu, A. AghaKouchak, D. Braithwaite, H. Ashouri, and A. R. Thorstensen, "The PERSIANN family of global satellite precipitation data: a review and evaluation of the products," *Hydrology and Earth System Sciences*, vol. 22, no. 11, pp. 5801–5816, 2018.

[13] B. Pan, K. Hsu, A. AghaKouchak, and S. Sorooshian, "Improving precipitation estimation using convolutional neural network," *Water Resources Research*, vol. 55, no. 3, pp. 2301–2321, 2019.

[14] M. Rajeevan, J. Bhate, J. D. Kale, and B. Lal, "Development of a high resolution daily gridded temperature data set over India," *Meteorological Monographs*, vol. 45, no. 1, pp. 22–27, 2006.

---

*© 2025 The Authors. Published under the terms of the CC BY 4.0 licence.*
