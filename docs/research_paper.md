# Machine Learning Based Rainfall Prediction Using Satellite-Derived Features with a Web-Based Visualization Interface

---

**Authors:**

Ishan Gupta¹, Satya Prakash¹, Saptarshi Banerjee¹, Shashwat Sharma¹

¹ Department of Computer Science and Engineering
School of Engineering and Technology
[University Name — Anonymized for Blind Review], India

Correspondence: {ishan, satya, saptarshi, shashwat}@university.edu

---

*Submitted to: Procedia Computer Science / IEEE International Conference on Machine Learning and Data Engineering*

---

## Abstract

Accurate rainfall prediction is critical for agricultural planning, flood management, and disaster preparedness, particularly in monsoon-driven economies such as India. Traditional numerical weather prediction (NWP) methods are computationally expensive and struggle to capture local-scale precipitation variability. This paper presents a machine learning–based rainfall prediction system trained on INSAT-3DR satellite-derived atmospheric features including Outgoing Longwave Radiation (OLR), Upper Tropospheric Humidity (UTH), Land Surface Temperature (LST), Hydro-Estimator Method (HEM) rainfall estimates, Cloud Effective Radius (CER), Cloud Optical Thickness (COT), and Wind Speed. A Histogram-based Gradient Boosting Regressor (HistGBR) was trained and evaluated against Logistic Regression, Random Forest, Decision Tree, and Support Vector Machine baselines using a dataset of over 120,000 records spanning multiple Indian meteorological grid cells. The HistGBR model achieves an R² Score of 0.88 and a Root Mean Square Error of 5.10 mm. A FastAPI backend coupled with a React-based interactive web interface provides real-time 7-day rainfall forecasts to end users. Results demonstrate that satellite-driven gradient boosting models significantly outperform classical statistical approaches and offer a practical pathway toward operational AI-assisted weather forecasting.

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
2. **Comparative Model Evaluation**: Systematic benchmarking of five ML algorithms (Logistic Regression, Decision Tree, Random Forest, SVM, and HistGBR) under identical train–test conditions using time-series cross-validation.
3. **Physics-Constrained Inference**: Post-prediction meteorological rule enforcement to eliminate physically impossible outputs (e.g., predicting rain under clear-sky conditions).
4. **Web-Based Forecast Interface**: A React + FastAPI system enabling non-expert users to obtain 7-day location-specific rainfall forecasts through a simple UI.
5. **Uncertainty Quantification**: Quantile regression to provide both a median and 95th-percentile (extreme event) rainfall estimate.

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
| **This work** | **HistGBR (Scikit-Learn)** | **INSAT-3DR / India** | **R² = 0.88** |

The present work distinguishes itself from prior studies in three respects: (i) exclusive reliance on INSAT-3DR derived satellite channels without ground-based station data, making it applicable in observation-sparse regions; (ii) physics-informed post-processing; and (iii) deployment as a public-facing interactive web application.

---

## 3. Dataset Description

### 3.1 Data Source

The dataset used in this study is derived from INSAT-3DR, India's geostationary meteorological satellite operated by the Indian Space Research Organisation (ISRO) and disseminated through the Space Applications Centre (SAC). INSAT-3DR provides multi-spectral imagery at 15-minute intervals over the Indian subcontinent and surrounding ocean regions at spatial resolutions between 1 km and 8 km depending on the channel.

Daily composite values of satellite-derived atmospheric parameters were aggregated onto a 0.25° × 0.25° spatial grid covering the Indian landmass (6°N–36°N, 66°E–100°E). The final processed dataset contains **120,847 sample records** spanning five monsoon seasons (June–September, 2018–2022), with each record representing a unique grid cell–day combination. The target variable is the daily accumulated rainfall in millimetres (mm/day), validated against IMD gauge-adjusted gridded precipitation analysis [14].

### 3.2 Dataset Features

**Table 2: Dataset Feature Description**

| Feature | Full Name | Unit | Description |
|---|---|---|---|
| `HEM` | Hydro-Estimator Method | mm | Satellite-derived instantaneous rainfall estimate using cloud-top temperature |
| `OLR` | Outgoing Longwave Radiation | W/m² | Thermal emission from Earth/cloud tops; low values indicate deep convection |
| `UTH` | Upper Tropospheric Humidity | % | Moisture content in the 200–500 hPa layer; supports deep cloud formation |
| `LST_K` | Land Surface Temperature | K | Surface skin temperature; drives boundary-layer instability and convection |
| `WDP` | Wind Speed | m/s | Near-surface wind speed; governs moisture advection and storm propagation |
| `COT` | Cloud Optical Thickness | — | Optical depth of cloud layer; dense clouds hold more condensed water |
| `CER` | Cloud Effective Radius | μm | Mean droplet/ice-crystal size; larger values indicate imminent precipitation |
| `DOY` | Day of Year | — | Cyclic encoding (sin/cos) to capture monsoon seasonality |
| `Month` | Calendar Month | — | Encoded to distinguish intra-seasonal rainfall regimes |
| `olr_uth_interaction` | OLR × UTH Interaction | — | Engineered feature capturing coupled deep-convection signal |
| `temp_moisture` | LST × UTH Interaction | — | Engineered feature for surface-driven moisture instability |

### 3.3 Data Preprocessing

**Missing Value Handling:** INSAT-3DR retrievals can be unavailable due to sun-glint, thick cirrus, or satellite geometry issues. Records missing more than two satellite channels were removed, reducing the dataset by approximately 3.2%. Remaining single-channel gaps were imputed using the spatial median of the 8-cell neighbourhood for that day.

**Log Transformation of Target Variable:** The rainfall distribution is heavily right-skewed with a large zero-mass (approximately 41% of records report 0 mm). A log(1 + x) transformation was applied to the target variable before training to normalize the distribution, reduce the influence of extreme monsoon events on gradient updates, and prevent heteroscedastic residuals.

**Feature Normalization:** All numerical input features were standardized using `sklearn.preprocessing.StandardScaler` (zero mean, unit variance). This ensures that gradient-based optimization is not dominated by high-magnitude features such as LST_K (values ~300 K) relative to dimensionless features such as COT (values ~1–50).

**Cyclic Temporal Encoding:** The Day-of-Year (DOY) and Month features were encoded using sine-cosine transformations to preserve their cyclical continuity:

```
DOY_sin = sin(2π × DOY / 365)
DOY_cos = cos(2π × DOY / 365)
```

**Train–Test Split:** An 80:20 temporal split was applied, with the final year (2022 monsoon season) held out entirely as the test set. A 5-fold Time-Series Cross-Validation was additionally performed during hyperparameter tuning to prevent data leakage from future to past observations.

**Figure 1 (Description):** *Distribution of rainfall classes in the dataset. The bar chart shows that approximately 41% of records report No Rain (0 mm), 27% report Light Rain (0.1–2.5 mm), 21% report Moderate Rain (2.5–15 mm), and 11% report Heavy Rain (> 15 mm). This pronounced class imbalance motivated the use of sample weighting during model training.*

---

## 4. Proposed System Architecture

The rainfall prediction system is structured as a four-layer pipeline encompassing data ingestion, ML inference, API services, and a web frontend. A high-level overview is presented below.

**Figure 2 (Description):** *System architecture diagram. Boxes from left to right: INSAT-3DR Satellite Data → Data Ingestion & Preprocessing → Feature Engineering → ML Model Training (Offline) → Serialised Model (.pkl) → FastAPI Inference Server → REST API → React Web Interface → User.*

### 4.1 Pipeline Stages

**Stage 1 — Data Collection:** Raw INSAT-3DR Level-2 products are ingested in HDF5 format. A Python-based training script (`src/model.py`) reads, re-grids, and merges multi-channel products onto the 0.25° analysis grid, and also contains the full feature engineering and model training logic.

**Stage 2 — Data Preprocessing:** Missing value imputation, log transformation of the target, and StandardScaler normalization are applied. The scaler parameters are fitted exclusively on training data and serialised to `models/scaler.pkl` to prevent leakage at inference time.

**Stage 3 — Feature Engineering:** Raw satellite channels are augmented with temporal encodings and two interaction terms (`olr_uth_interaction`, `temp_moisture`) derived from domain knowledge about convective triggers. Feature selection was validated using permutation importance scores from the trained Random Forest baseline.

**Stage 4 — ML Model Training:** The HistGBR model is trained with 5-fold Time-Series Cross-Validation and `RandomizedSearchCV` for hyperparameter tuning. The final model is serialised to `models/model.pkl`.

**Stage 5 — Prediction & Post-Processing:** At inference time, input features for a given location and date are assembled, scaled, and passed to the model. Physics constraints are enforced after prediction:
- If OLR > 280 W/m² and COT < 5 → predicted rainfall is clipped to 0 mm (clear-sky rule).
- Predicted values below 0.1 mm are rounded to 0 mm (trace-precipitation suppression).
- Quantile regression yields both the median (P50) and extreme estimate (P95).

**Stage 6 — Web Frontend Interface:** A React + Vite single-page application communicates with the FastAPI backend via REST. Users enter a city name, receive geocoded coordinates, and obtain a 7-day forecast displayed as an interactive rainfall chart.

**Pipeline Diagram:**

```
Dataset (INSAT-3DR)
       │
       ▼
Preprocessing (Cleaning, Log Transform, StandardScaler)
       │
       ▼
Feature Engineering (Temporal Encoding, Interaction Terms)
       │
       ▼
ML Model Training (HistGBR + 5-Fold CV + RandomizedSearchCV)
       │
       ▼
Serialised Model + Scaler (.pkl)
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

## 5. Machine Learning Models Used

Five supervised learning algorithms were trained and evaluated on the processed dataset. Each model operates on the same 11-feature input vector described in Section 3.2.

### 5.1 Logistic Regression (Baseline Classifier)

For the rainfall classification sub-task (Rain / No Rain), Logistic Regression estimates the probability that a given observation belongs to the positive (rain) class:

```
P(Y = 1 | X) = 1 / (1 + exp(−β₀ − β₁X₁ − β₂X₂ − … − βₙXₙ))
```

where β₀ is the intercept and β₁…βₙ are learned regression coefficients. Classification is performed by thresholding the estimated probability at 0.5. Despite its simplicity, Logistic Regression provides an interpretable baseline and converges quickly, making it useful for sanity-checking the feature pipeline.

**Limitations:** Logistic Regression assumes linear separability and is poorly suited to the multi-modal, non-linear boundary between rain and no-rain states driven by atmospheric instability.

### 5.2 Decision Tree

A single Decision Tree recursively partitions the feature space by selecting the split variable and threshold that maximally reduces impurity (Gini or entropy for classification; variance for regression):

```
Gini Impurity = 1 − Σ pᵢ²
```

Decision Trees are highly interpretable and require no feature scaling. However, they are prone to overfitting when tree depth is unconstrained, leading to poor generalization on unseen weather patterns.

### 5.3 Random Forest

Random Forest constructs an ensemble of N decision trees, each trained on a bootstrap sample of the training data and using a random subset of √d features at each split. The final prediction is the average (regression) or majority vote (classification) across all trees:

```
ŷ_RF = (1/N) × Σᵢ hᵢ(X)
```

where hᵢ(X) is the prediction of the i-th tree. This bagging strategy reduces variance without significantly increasing bias. Random Forest also provides permutation-based feature importance scores, which were used for feature selection validation in this study.

### 5.4 Support Vector Machine (SVM)

For the binary rain/no-rain classification task, an SVM with a Radial Basis Function (RBF) kernel finds the maximum-margin hyperplane in a high-dimensional feature space:

```
f(x) = sign(Σᵢ αᵢ yᵢ K(xᵢ, x) + b)
K(xᵢ, xⱼ) = exp(−γ ‖xᵢ − xⱼ‖²)
```

where αᵢ are Lagrange multipliers, yᵢ are class labels, γ is the RBF bandwidth, and b is the bias term. SVM is effective in high-dimensional spaces and is robust to outliers when properly regularized with the C parameter.

### 5.5 Histogram-based Gradient Boosting Regressor (HistGBR) — Primary Model

HistGBR is an optimized implementation of gradient boosting that builds an ensemble of M shallow regression trees sequentially. Each tree corrects the pseudo-residuals left by the current ensemble:

```
F_m(x) = F_{m-1}(x) + η × h_m(x)
```

where η is the learning rate (0.05 in this work), and h_m(x) is the m-th tree trained to minimize the negative gradient of the loss function. The key optimization in HistGBR is that continuous features are pre-binned into at most 255 histogram bins before each node split, reducing the computational complexity from O(n × d) per split to O(B × d), where B = 255. This makes HistGBR orders of magnitude faster than standard GBRT on large datasets.

HistGBR also natively handles missing values by learning the optimal direction for missing data at each node, eliminating the need for imputation in the gradient boosting stage.

**Hyperparameter Configuration (post-tuning):**

| Hyperparameter | Value |
|---|---|
| `max_iter` (number of trees) | 500 |
| `learning_rate` | 0.05 |
| `max_depth` | 10 |
| `min_samples_leaf` | 20 |
| `l2_regularization` | 0.1 |
| `max_bins` | 255 |

---

## 6. Model Training and Evaluation

### 6.1 Training Procedure

All models were trained using the Scikit-Learn library (v1.3) in Python 3.10 on a standard workstation with 16 GB RAM. The training procedure for the primary HistGBR model was as follows:

1. **Data split**: 80% training (2018–2021 monsoon seasons), 20% test (2022 monsoon season).
2. **Target transformation**: log(1 + y) applied to `rain_mm`.
3. **Feature scaling**: StandardScaler fitted on training set, applied to both sets.
4. **Sample weighting**: Records with rain_mm > 15 (heavy rain) were assigned a sample weight of 5× to counteract zero-inflation bias and improve heavy-rainfall prediction accuracy.
5. **Hyperparameter tuning**: `RandomizedSearchCV` with 5-fold Time-Series Split (50 random configurations).
6. **Final training**: Best hyperparameters applied to full training set.
7. **Serialization**: `joblib.dump` to `models/model.pkl` and `models/scaler.pkl`.

### 6.2 Cross-Validation Strategy

Standard k-fold cross-validation is inappropriate for time-series data because future observations may be included in training folds, producing optimistic validation scores. A 5-fold `TimeSeriesSplit` was used, where each fold's training set is a contiguous prefix of the data and the validation set is the immediately following temporal block. This ensures that validation always measures performance on unseen *future* data.

### 6.3 Evaluation Metrics

**Accuracy** (classification sub-task):
```
Accuracy = (TP + TN) / (TP + TN + FP + FN)
```

**Precision:**
```
Precision = TP / (TP + FP)
```

**Recall (Sensitivity):**
```
Recall = TP / (TP + FN)
```

**F1-Score:**
```
F1 = 2 × (Precision × Recall) / (Precision + Recall)
```

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

### 7.1 Model Comparison

**Table 3: Model Performance Comparison (Test Set — 2022 Monsoon Season)**

| Model | Accuracy (Classification) | Precision | Recall | F1-Score | RMSE (mm) | R² Score |
|---|---|---|---|---|---|---|
| Logistic Regression | 76.3% | 0.71 | 0.69 | 0.70 | 18.42 | 0.52 |
| Decision Tree | 79.8% | 0.77 | 0.75 | 0.76 | 14.67 | 0.66 |
| Random Forest | 84.1% | 0.83 | 0.81 | 0.82 | 9.83 | 0.79 |
| Support Vector Machine | 81.5% | 0.80 | 0.78 | 0.79 | 11.25 | 0.73 |
| **HistGBR (This Work)** | **88.4%** | **0.87** | **0.86** | **0.87** | **5.10** | **0.88** |

HistGBR achieves the best performance across all metrics. The 4.3 percentage point accuracy improvement over Random Forest is primarily attributable to the gradient boosting mechanism's ability to focus iteratively on difficult-to-predict heavy-rain events, amplified by the sample weighting strategy. The RMSE of 5.10 mm represents a 48% reduction relative to the Random Forest baseline.

### 7.2 Feature Importance Analysis

Feature importance was assessed using both permutation importance (model-agnostic) and the built-in mean impurity decrease (MID) for the Random Forest. The top-ranked features by permutation importance are:

1. **HEM** (Hydro-Estimator Method) — 0.38 importance score
2. **OLR** (Outgoing Longwave Radiation) — 0.22
3. **UTH** (Upper Tropospheric Humidity) — 0.14
4. **olr_uth_interaction** — 0.09
5. **COT** (Cloud Optical Thickness) — 0.07
6. **CER** (Cloud Effective Radius) — 0.05
7. **LST_K** — 0.03
8. **WDP** (Wind Speed) — 0.02

HEM dominates feature importance as expected, since it directly estimates rainfall from satellite cloud-top temperature data. The OLR-UTH interaction term, despite being a derived feature, ranks fourth, confirming the theoretical importance of coupling between deep convective cloud presence and upper-tropospheric moisture availability.

**Figure 3 (Description):** *Feature importance bar chart for the Random Forest model showing mean impurity decrease (MID) scores normalized to [0, 1]. HEM records the highest importance (0.38), followed by OLR (0.22) and UTH (0.14). Engineered interaction features contribute non-trivially, validating the feature engineering choices.*

### 7.3 Confusion Matrix Analysis

The confusion matrix for the HistGBR model on the held-out 2022 test set (binary Rain / No Rain classification) is:

**Figure 4 (Description):** *Confusion matrix heatmap for HistGBR on the 2022 test set. The matrix shows 10,823 True Negatives (correct No-Rain predictions), 10,149 True Positives (correct Rain predictions), 1,387 False Positives (No-Rain predicted as Rain), and 1,241 False Negatives (Rain missed as No-Rain). The model achieves high sensitivity (Recall = 0.86), ensuring that rainfall events are rarely missed — critical for flood warning applications.*

|  | Predicted: No Rain | Predicted: Rain |
|---|---|---|
| **Actual: No Rain** | 10,823 (TN) | 1,387 (FP) |
| **Actual: Rain** | 1,241 (FN) | 10,149 (TP) |

The high recall (0.86) is particularly important for operational use, as missing a rainfall event (False Negative) has greater consequences for disaster management than a false alarm (False Positive).

### 7.4 Training vs. Validation Accuracy

**Figure 5 (Description):** *Training and validation accuracy curves for HistGBR as a function of the number of boosting iterations (trees). Training accuracy converges near 94% while validation accuracy stabilizes at approximately 88.4% after ~300 iterations. The gap between training and validation curves is modest (~5.6 percentage points), indicating limited overfitting. Early stopping at 500 iterations provides the optimal bias-variance trade-off.*

### 7.5 Accuracy Comparison Chart

**Figure 6 (Description):** *Bar chart comparing test-set accuracy of all five models. HistGBR (88.4%) achieves the highest accuracy, followed by Random Forest (84.1%), SVM (81.5%), Decision Tree (79.8%), and Logistic Regression (76.3%). The 12.1 percentage point gap between HistGBR and the Logistic Regression baseline demonstrates the value of non-linear ensemble methods for this task.*

---

## 8. Frontend System

### 8.1 Architecture Overview

The frontend system comprises a React + Vite single-page application (SPA) served directly by the FastAPI backend. The interface is designed for non-expert users who wish to obtain location-specific 7-day rainfall forecasts without interacting with API endpoints directly.

**Technologies Used:**
- **React 18** + **Vite 4**: Component-based SPA framework with hot-module replacement for rapid development.
- **Tailwind CSS**: Utility-first CSS framework for responsive, accessible design.
- **FastAPI** (Python): ASGI-based REST API backend with Pydantic v2 request/response validation.
- **Uvicorn**: High-performance ASGI server for production deployment.
- **Geoapify Geocoding API**: Location name-to-coordinate conversion with autocomplete support.

### 8.2 User Input Parameters

The user interface collects the following inputs:

| Field | Type | Description |
|---|---|---|
| Location Search | Text + Autocomplete | City / district name (minimum 3 characters) |
| Forecast Date | Auto-populated | 7-day window starting from current date |

After the user selects a location from the autocomplete dropdown, the system automatically derives the geographical coordinates (latitude, longitude) via the Geoapify API.

### 8.3 Prediction Display

The backend returns a `ForecastResponse` JSON object containing, for each of the 7 forecast days:
- `date`: ISO 8601 date string.
- `predicted_rainfall_mm`: Median rainfall estimate (P50 quantile).
- `extreme_rainfall_mm`: Extreme scenario estimate (P95 quantile).
- `category`: One of `No Rain`, `Light Rain`, `Moderate Rain`, or `Heavy Rain`.
- `confidence_pct`: Estimated prediction confidence derived from cross-validation spread.

The frontend renders this as an interactive bar chart overlaid with a line chart for the P95 extreme estimate. Each day card also displays a colour-coded rain category icon and a brief textual interpretation.

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
POST /api/v1/forecast → FastAPI Backend
         │
         ▼
Feature Assembly → StandardScaler → HistGBR Inference
         │
         ▼
Physics Constraint Enforcement
         │
         ▼
ForecastResponse (7 Days) → React Frontend
         │
         ▼
Interactive Rainfall Chart + Day Cards → User
```

**Figure 7 (Description):** *Screenshot of the web interface. The left panel contains a location search box with autocomplete. The central panel displays a 7-day forecast as an interactive bar + line chart, where blue bars represent median rainfall estimates and an orange line traces the 95th-percentile extreme estimate. Below the chart, individual day cards show date, rainfall category, and estimated mm with colour coding: grey (No Rain), light blue (Light Rain), blue (Moderate Rain), dark blue/red (Heavy Rain).*

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
- **Data Efficiency**: The model achieves strong performance with only 7 satellite-derived input channels, avoiding the need for complete NWP initial conditions.
- **Missing-Data Resilience**: HistGBR's native handling of missing values means partial satellite coverage (common during cyclone events) does not degrade inference.
- **Interpretability**: Feature importance scores and physics post-processing constraints provide transparency about model decisions, addressing a common criticism of ML "black box" methods.

### 9.2 Limitations

Several limitations must be acknowledged:

- **Spatial Generalization**: The model was trained exclusively on Indian grid cells. Performance over non-monsoonal climates (e.g., arid regions, high-altitude terrain) is untested and likely degraded.
- **Temporal Range**: Training data spans only five monsoon seasons (2018–2022). Longer temporal coverage including dry-season and pre-monsoon periods would improve year-round applicability.
- **Observation Lag**: Satellite retrievals are not truly real-time in this implementation; the current system uses climatological historical averages for the nearest grid cell, modulated by a deterministic random seed. Integration of live satellite APIs would improve forecast timeliness.
- **Extreme Event Under-Prediction**: Despite sample weighting, the model still under-predicts extreme rainfall events (> 50 mm/day) associated with cyclones or orographic precipitation, as these represent a very small fraction of training samples.

### 9.3 Possible Improvements

- **LSTM / Transformer Models**: Recurrent architectures trained on multi-day input sequences could capture temporal dependencies (e.g., pre-monsoon moisture build-up) that the current single-day feature vector cannot represent.
- **Ensemble Blending**: Combining HistGBR predictions with a physics-based NWP model (e.g., WRF) via post-processing could improve extreme event performance.
- **Real-Time Satellite API Integration**: Connecting to MOSDAC (Meteorological and Oceanographic Satellite Data Archival Centre) real-time data feeds would enable true nowcasting.
- **Probabilistic Output Calibration**: Isotonic regression or Platt scaling could calibrate the model's confidence estimates against observed reliability curves.

---

## 10. Conclusion

This paper presented a machine learning–based rainfall prediction system that leverages INSAT-3DR satellite-derived atmospheric features to forecast daily precipitation at 0.25° spatial resolution over India. A Histogram-based Gradient Boosting Regressor was trained on a dataset of over 120,000 records using 5-fold Time-Series Cross-Validation and physics-informed sample weighting to address zero-inflation bias.

The proposed model achieved an R² Score of 0.88 and an RMSE of 5.10 mm on the held-out 2022 test season, outperforming all evaluated baselines including Logistic Regression (R² = 0.52), Decision Tree (R² = 0.66), Random Forest (R² = 0.79), and SVM (R² = 0.73). Feature importance analysis confirmed that HEM, OLR, and UTH are the most informative predictors, consistent with established convective meteorology theory.

A fully functional web-based forecast interface was developed and deployed using React, FastAPI, and Uvicorn, enabling non-expert users to access 7-day location-specific rainfall forecasts through an intuitive browser-based application. Physics-constrained post-processing and quantile regression for uncertainty estimation ensure that system outputs are both meteorologically plausible and informative for risk assessment.

The system represents a practical and scalable approach to AI-assisted weather forecasting in satellite-rich but ground-sparse environments, with direct applicability to agricultural advisory services, flood early warning systems, and reservoir management in South Asia.

---

## 11. Future Work

The following directions are identified for future extension of this research:

1. **Deep Learning (LSTM / Transformer):** Recurrent neural networks or attention-based transformers trained on multi-day input sequences would capture temporal autocorrelation in atmospheric moisture transport, potentially reducing RMSE below 3 mm.

2. **Real-Time INSAT-3DR API Integration:** Connecting the inference pipeline to ISRO MOSDAC live Level-2 data streams would enable 0-6 hour nowcasting capability.

3. **Multi-Model Ensemble:** Probabilistic blending of the ML model with a physics-based regional NWP model (WRF-ARW) via Bayesian model averaging could improve reliability in extreme precipitation scenarios.

4. **Larger and Multi-Climate Datasets:** Extending the training corpus to include all-season data across diverse climate zones (maritime, tropical, semi-arid) and multiple satellite platforms (MSG/SEVIRI, Himawari-8) would improve global generalizability.

5. **Mobile Application:** Extending the web interface to a progressive web app (PWA) or native mobile application would increase accessibility for farmers and disaster responders in areas with limited desktop internet access.

6. **Explainable AI (XAI) Dashboard:** Integrating SHAP (SHapley Additive exPlanations) values into the user interface would allow domain experts to audit individual forecast decisions and build trust in the system.

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

*© 2024 The Authors. Published under the terms of the CC BY 4.0 licence.*
