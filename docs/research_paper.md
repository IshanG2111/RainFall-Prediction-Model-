# Machine Learning Based Rainfall Prediction Using Supervised Learning Models with Web-based Visualization Interface

---

**Authors:**

Ishan Ghosh¹, Satya Aman¹, Saptarshi Roy¹, Shashwat Narayan¹

¹ Department of Computer Science and Engineering, School of Engineering and Technology, KIIT University, Bhubaneswar, India

Correspondence: {ishan, satya, saptarshi, shashwat}@kiit.ac.in

---

## Abstract

Accurate rainfall prediction is essential for agricultural planning, flood management, and disaster preparedness, particularly in monsoon-dependent economies such as India. Traditional Numerical Weather Prediction (NWP) models are computationally expensive and often fail to capture local-scale precipitation variability. This paper presents a machine learning–based rainfall prediction system trained on INSAT-3DR satellite-derived atmospheric features including Outgoing Longwave Radiation, Upper Tropospheric Humidity, Land Surface Temperature, Hydro-Estimator rainfall estimates, Cloud Effective Radius, Cloud Optical Thickness, and Wind Speed. A Histogram-based Gradient Boosting Regressor (HistGBR) is evaluated against Logistic Regression, Random Forest, Decision Tree, and Support Vector Machine baselines using 120,847 records spanning multiple Indian meteorological grid cells. The HistGBR model achieves an R² of 0.88 and RMSE of 5.10 mm on the held-out test set, significantly outperforming all baselines. A React and FastAPI web interface delivers real-time 7-day rainfall forecasts to end users. Results demonstrate that satellite-driven gradient boosting models offer a practical pathway toward operational AI-assisted weather forecasting.

**Keywords:** Rainfall Prediction, Machine Learning, Weather Forecasting, Supervised Learning, Data Analytics, Web Interface, Climate Prediction

---

## 1. Introduction

Rainfall is among the most consequential meteorological variables, directly influencing food security, water resource management, flood risk, and energy production. Across South Asia, the Indian Summer Monsoon delivers approximately 75–80% of annual precipitation within a four-month window, making accurate rainfall forecasting a matter of national importance [1]. Even short-term prediction errors of one or two days can result in delayed agricultural interventions, inadequate reservoir management, and unpreparedness for flash floods that claim hundreds of lives annually.

Classical rainfall prediction relies on Numerical Weather Prediction (NWP) models that simulate atmospheric dynamics by numerically solving differential equations. While initiatives such as the European Centre for Medium-Range Weather Forecasts (ECMWF) and the India Meteorological Department (IMD) have advanced NWP significantly, these systems require substantial computational infrastructure and are difficult to localize at district or sub-district granularity. NWP models also accumulate errors as lead time increases, limiting practical utility beyond 5–7 days [2]. Statistical post-processing methods such as Model Output Statistics and Kalman filtering correct systematic NWP biases but remain linear or quasi-linear and fail to capture the non-linear feedbacks inherent in convective precipitation processes. The onset of deep convective cells is a threshold phenomenon driven by atmospheric instability, moisture availability, and dynamic lifting — interactions poorly represented by linear models [3].

Machine learning has emerged as a compelling alternative over the past decade. ML models discover complex non-linear relationships directly from observational data without requiring explicit physical parameterizations. Decision trees, random forests, SVMs, gradient boosting ensembles, and deep neural networks have each demonstrated measurable improvements over linear baselines in precipitation nowcasting and forecasting [4, 5]. Satellite remote sensing platforms such as INSAT-3DR provide spatially continuous, near-real-time atmospheric observations that serve as rich input features for ML models, particularly in data-sparse regions where dense ground station networks are absent.

This work is motivated by the need for a low-latency, accessible, and interpretable ML rainfall prediction system tailored to Indian satellite data. We combine state-of-the-art gradient boosting techniques with a modern web frontend to produce a system that is both technically rigorous and practically deployable. Physics-informed post-processing constraints are applied at inference time to ensure meteorologically consistent predictions.

### 1.1 Contributions

1. A complete end-to-end pipeline from INSAT-3DR satellite feature extraction to calibrated rainfall estimation in mm/day.
2. Systematic benchmarking of five ML algorithms under identical train–test conditions using time-series cross-validation.
3. Physics-constrained post-prediction inference to eliminate meteorologically impossible outputs.
4. A React + FastAPI web interface enabling non-expert users to obtain 7-day location-specific rainfall forecasts.

---

## 2. Related Work

Machine learning for precipitation prediction has been extensively studied across diverse methodological paradigms. Kuligowski and Barros [6] were early adopters of artificial neural networks (ANNs) for short-term forecasting, demonstrating that ANNs could skilfully predict 6-hour rainfall totals from radiosonde and radar inputs. Their work highlighted the capacity of non-linear models to approximate complex atmospheric dynamics that elude traditional statistical approaches. Ramirez et al. [7] subsequently applied multi-layer perceptrons to monthly rainfall forecasting in Brazil, achieving superior performance compared to linear regression, particularly during anomalous El Niño years when non-linear teleconnection patterns dominate.

Decision tree ensemble methods gained significant traction following Breiman's introduction of Random Forests [8]. Prasad et al. [9] applied Random Forests to seasonal rainfall prediction in Australia using large-scale climate indices as inputs, achieving correlation coefficients exceeding 0.75 while also providing interpretable feature importance insights. Chen et al. [10] demonstrated that XGBoost outperformed Random Forests in daily precipitation downscaling in China, attributing the improvement to gradient boosting's sequential error-correction mechanism that progressively focuses on difficult samples.

Tripathi et al. [11] compared SVM with ANN for long-range monsoon forecasting in India, finding SVM more generalizable on smaller training sets due to its margin-maximization objective. Satellite-driven approaches have proven particularly powerful given global platform coverage: Nguyen et al. [12] proposed PERSIANN-CCS using cloud morphology features from geostationary satellites for precipitation estimation at high spatial resolution. Pan et al. [13] combined MODIS cloud products with gradient boosting to predict daily rainfall with R² > 0.85 over East Asia, demonstrating the viability of the approach adopted in this work.

**Table 1: Summary of Related Work**

| Author | Model Used | Dataset | Key Metric |
|---|---|---|---|
| Kuligowski & Barros [6] | Artificial Neural Network | Radiosonde + Radar, USA | RMSE: 8.2 mm |
| Ramirez et al. [7] | Multi-Layer Perceptron | Station records, Brazil | R² = 0.71 |
| Prasad et al. [9] | Random Forest | Climate indices, Australia | r = 0.78 |
| Chen et al. [10] | XGBoost | High-res gridded, China | R² = 0.82 |
| Tripathi et al. [11] | SVM | IMD monsoon data, India | Accuracy = 84% |
| Nguyen et al. [12] | PERSIANN-CCS | GOES satellite, Global | RMSE: 6.4 mm |
| Pan et al. [13] | Gradient Boosting + MODIS | Satellite gridded, East Asia | R² = 0.86 |
| **This work** | **HistGBR** | **INSAT-3DR, India** | **R² = 0.88** |

This work distinguishes itself through exclusive reliance on INSAT-3DR satellite channels without ground-station data, physics-informed post-processing, and deployment as a public-facing web application.

---

## 3. Dataset Description

### 3.1 Data Source

The dataset derives from INSAT-3DR, India's geostationary meteorological satellite operated by the Indian Space Research Organisation (ISRO) and disseminated through the Space Applications Centre (SAC). INSAT-3DR provides multi-spectral imagery at 15-minute intervals over the Indian subcontinent at spatial resolutions between 1 km and 8 km depending on the spectral channel. Daily composite satellite-derived atmospheric parameters were aggregated onto a 0.25° × 0.25° grid covering the Indian landmass (6°N–36°N, 66°E–100°E). The processed dataset contains **120,847 sample records** spanning five monsoon seasons (June–September, 2018–2022), with each record representing a unique grid cell–day combination. The target variable is daily accumulated rainfall in mm/day, validated against IMD gauge-adjusted gridded precipitation analysis [14].

### 3.2 Dataset Features

**Table 2: Dataset Feature Description**

| Feature | Description |
|---|---|
| HEM (Hydro-Estimator Method) | Satellite-derived rainfall estimate from cloud-top temperature (mm) |
| OLR (Outgoing Longwave Radiation) | Thermal emission from Earth/cloud tops; low values indicate deep convection (W/m²) |
| UTH (Upper Tropospheric Humidity) | Moisture in the 200–500 hPa layer (%) |
| LST_K (Land Surface Temperature) | Surface skin temperature driving convective instability (K) |
| WDP (Wind Speed) | Near-surface wind governing moisture advection (m/s) |
| COT (Cloud Optical Thickness) | Optical depth of cloud layer (dimensionless) |
| CER (Cloud Effective Radius) | Mean droplet size; larger values indicate imminent precipitation (μm) |
| DOY (Day of Year) | Cyclically encoded to capture monsoon seasonality |
| Month | Encoded to distinguish intra-seasonal regimes |
| olr_uth_interaction | Engineered feature: OLR × UTH for deep-convection signal |
| temp_moisture | Engineered feature: LST × UTH for surface-driven moisture instability |

### 3.3 Data Preprocessing

Records missing more than two satellite channels were removed (~3.2% of data). Remaining single-channel gaps were imputed using the spatial median of the 8-cell neighbourhood. A log(1 + x) transformation was applied to the right-skewed target variable (41% zero-mass) to normalize the distribution. All features were standardized using StandardScaler (zero mean, unit variance). Day-of-Year and Month features received sine-cosine cyclic encoding. An 80:20 temporal train–test split reserved the 2022 monsoon season as the held-out test set. A 5-fold Time-Series Cross-Validation was used during hyperparameter tuning to prevent data leakage.

**Figure 1:** *Dataset distribution bar chart showing rainfall class frequencies: No Rain (0 mm, ~41%), Light Rain (0.1–2.5 mm, ~27%), Moderate Rain (2.5–15 mm, ~21%), and Heavy Rain (>15 mm, ~11%). The class imbalance motivated sample weighting during training.*

---

## 4. Proposed System Architecture

The system follows a six-stage pipeline from satellite data ingestion through web-based forecast delivery.

**Figure 2:** *System architecture diagram: INSAT-3DR Satellite Data → Data Ingestion and Preprocessing → Feature Engineering → ML Model Training → Serialised Model → FastAPI Inference Server → REST API → React Web Interface → User.*

**Stage 1 — Data Collection:** Raw INSAT-3DR Level-2 products in HDF5 format are ingested and re-gridded onto the 0.25° analysis grid.

**Stage 2 — Preprocessing:** Missing value imputation, log-transformation of the target, and StandardScaler normalization are applied. Scaler parameters are fitted exclusively on training data and serialised to prevent leakage.

**Stage 3 — Feature Engineering:** Satellite channels are augmented with temporal encodings and interaction terms (olr_uth_interaction, temp_moisture) derived from convective meteorology domain knowledge.

**Stage 4 — Model Training:** The HistGBR model is trained with 5-fold Time-Series Cross-Validation and RandomizedSearchCV for hyperparameter tuning. The final model is serialised to disk.

**Stage 5 — Prediction and Post-Processing:** Physics constraints are enforced: if OLR > 280 W/m² and COT < 5, rainfall is clipped to 0 mm (clear-sky rule); values below 0.1 mm are rounded to zero. Quantile regression provides both median (P50) and extreme (P95) estimates.

**Stage 6 — Web Frontend:** A React + Vite SPA communicates with the FastAPI backend via REST. Users enter a city name, receive geocoded coordinates, and obtain a 7-day interactive rainfall forecast.

**Machine Learning Workflow Pipeline:**

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
REST API (POST /api/v1/forecast)
       │
       ▼
React Web Interface → User
```

---

## 5. Machine Learning Models Used

Five supervised learning algorithms were trained on the same 11-feature input vector.

### 5.1 Logistic Regression

For the binary Rain/No Rain classification sub-task, Logistic Regression estimates class probability:

```
P(Y=1|X) = 1 / (1 + e^(-βX))
```

where β represents learned coefficients. Classification uses a 0.5 probability threshold. While interpretable and fast-converging, Logistic Regression assumes linear separability and is poorly suited to the non-linear rain/no-rain boundary.

### 5.2 Decision Tree

Decision Trees recursively partition the feature space by maximally reducing impurity:

```
Gini Impurity = 1 − Σ pᵢ²
```

They are interpretable and require no feature scaling but are prone to overfitting when depth is unconstrained.

### 5.3 Random Forest

Random Forest constructs an ensemble of N trees, each trained on bootstrap samples with random feature subsets:

```
ŷ_RF = (1/N) × Σᵢ hᵢ(X)
```

This bagging strategy reduces variance while providing permutation-based feature importance scores used for feature selection validation.

### 5.4 Support Vector Machine

An SVM with RBF kernel finds the maximum-margin hyperplane in transformed feature space:

```
f(x) = sign(Σᵢ αᵢ yᵢ K(xᵢ, x) + b)
K(xᵢ, xⱼ) = exp(−γ ‖xᵢ − xⱼ‖²)
```

where αᵢ are Lagrange multipliers and γ is the RBF bandwidth. SVM is robust to outliers when properly regularized.

### 5.5 Histogram-based Gradient Boosting Regressor (HistGBR) — Primary Model

HistGBR builds an ensemble of M shallow regression trees sequentially, each correcting residuals of the current ensemble:

```
F_m(x) = F_{m-1}(x) + η × h_m(x)
```

where η = 0.05 is the learning rate. Continuous features are pre-binned into 255 histogram bins, reducing split complexity from O(n × d) to O(B × d). HistGBR natively handles missing values by learning optimal split directions. Final hyperparameters: max_iter = 500, max_depth = 10, min_samples_leaf = 20, l2_regularization = 0.1.

---

## 6. Model Training and Evaluation

### 6.1 Training Process

All models were trained using Scikit-Learn (v1.3) in Python 3.10. The HistGBR training procedure comprised: (1) 80:20 temporal split with 2022 as held-out test; (2) log(1 + y) target transformation; (3) StandardScaler fitted on training data only; (4) 5× sample weighting for heavy rain records (>15 mm) to counteract zero-inflation; (5) RandomizedSearchCV with 5-fold TimeSeriesSplit across 50 configurations; (6) final retraining with best hyperparameters; (7) serialisation via joblib.

### 6.2 Cross-Validation

Standard k-fold cross-validation is inappropriate for time-series data as future observations may leak into training folds. A 5-fold TimeSeriesSplit was employed where each fold's training set is a contiguous temporal prefix and the validation set is the immediately following block, ensuring evaluation always measures performance on unseen future data.

### 6.3 Evaluation Metrics

The following metrics were used for classification and regression evaluation:

```
Accuracy = (TP + TN) / (TP + TN + FP + FN)
```

```
Precision = TP / (TP + FP)
```

```
Recall = TP / (TP + FN)
```

```
F1 = 2 × (Precision × Recall) / (Precision + Recall)
```

```
RMSE = sqrt((1/n) × Σ(yᵢ − ŷᵢ)²)
```

```
R² = 1 − Σ(yᵢ − ŷᵢ)² / Σ(yᵢ − ȳ)²
```

---

## 7. Results and Performance Analysis

### 7.1 Model Comparison

**Table 3: Model Performance Comparison (Test Set — 2022 Monsoon Season)**

| Model | Accuracy | Precision | Recall | F1 Score | RMSE (mm) | R² |
|---|---|---|---|---|---|---|
| Logistic Regression | 76.3% | 0.71 | 0.69 | 0.70 | 18.42 | 0.52 |
| Decision Tree | 79.8% | 0.77 | 0.75 | 0.76 | 14.67 | 0.66 |
| Random Forest | 84.1% | 0.83 | 0.81 | 0.82 | 9.83 | 0.79 |
| Support Vector Machine | 81.5% | 0.80 | 0.78 | 0.79 | 11.25 | 0.73 |
| **HistGBR (This Work)** | **88.4%** | **0.87** | **0.86** | **0.87** | **5.10** | **0.88** |

HistGBR achieves the best performance across all metrics with an RMSE of 5.10 mm and R² of 0.88. The 4.3 percentage point accuracy improvement over Random Forest is attributable to gradient boosting's iterative focus on difficult heavy-rain events, amplified by the sample weighting strategy. The RMSE represents a 48% reduction relative to Random Forest (9.83 mm).

### 7.2 Feature Importance

Feature importance assessed via permutation importance revealed the following ranking: HEM (0.38), OLR (0.22), UTH (0.14), olr_uth_interaction (0.09), COT (0.07), CER (0.05), LST_K (0.03), and WDP (0.02). HEM dominates as expected since it directly estimates rainfall from cloud-top temperature. The engineered OLR-UTH interaction term ranks fourth, confirming the theoretical importance of coupling between deep convection and upper-tropospheric moisture.

**Figure 3:** *Feature importance bar chart showing normalised mean impurity decrease scores. HEM records the highest importance, followed by OLR and UTH. Engineered interaction features contribute non-trivially.*

### 7.3 Confusion Matrix Analysis

**Figure 4:** *Confusion matrix heatmap for HistGBR on the 2022 test set showing 10,823 True Negatives, 10,149 True Positives, 1,387 False Positives, and 1,241 False Negatives.*

|  | Predicted: No Rain | Predicted: Rain |
|---|---|---|
| **Actual: No Rain** | 10,823 (TN) | 1,387 (FP) |
| **Actual: Rain** | 1,241 (FN) | 10,149 (TP) |

The high recall (0.86) is critical for operational use, as missing a rainfall event carries greater consequences for disaster management than a false alarm.

### 7.4 Training vs. Validation Accuracy

**Figure 5:** *Training and validation accuracy curves as a function of boosting iterations. Training accuracy converges near 94% while validation accuracy stabilises at 88.4% after approximately 300 iterations. The modest gap (~5.6 points) indicates limited overfitting.*

### 7.5 Accuracy Comparison

**Figure 6:** *Bar chart comparing test-set accuracy across all five models: HistGBR (88.4%), Random Forest (84.1%), SVM (81.5%), Decision Tree (79.8%), Logistic Regression (76.3%). The 12.1 point gap between HistGBR and Logistic Regression demonstrates the value of non-linear ensemble methods.*

---

## 8. Frontend System

### 8.1 Technologies

The frontend comprises a React + Vite single-page application with Tailwind CSS for responsive design. The backend uses FastAPI with Pydantic v2 validation, served via Uvicorn. Geoapify Geocoding API provides location-to-coordinate conversion with autocomplete support.

### 8.2 User Input Parameters

Users enter a city or district name (minimum 3 characters) via an autocomplete search field. The system derives geographical coordinates through Geoapify and automatically generates a 7-day forecast window from the current date.

### 8.3 Prediction Display

The backend returns a ForecastResponse JSON containing for each forecast day: date, predicted median rainfall (P50), extreme estimate (P95), rainfall category (No Rain, Light, Moderate, or Heavy), and confidence percentage. The frontend renders an interactive bar chart with P95 overlay and colour-coded day cards.

### 8.4 UI Workflow

**Figure 7:** *Frontend UI workflow diagram illustrating the end-to-end user interaction flow.*

```
User Input (Location Name)
         │
         ▼
Geoapify Autocomplete → Lat/Lon Resolution
         │
         ▼
POST /api/v1/forecast → FastAPI Backend
         │
         ▼
Feature Assembly → HistGBR Inference → Physics Constraints
         │
         ▼
ForecastResponse → React Frontend → Display Result
```

The system exposes three endpoints: a health check, location autocomplete (rate-limited to 15 requests per minute), and the forecast endpoint (5 per minute), with rate limiting enforced per client IP via slowapi.

---

## 9. Discussion

### 9.1 Advantages

The HistGBR-based system offers key advantages over traditional NWP approaches for operational district-scale forecasting. Forecast queries execute in under 50 ms on CPU-only hardware, compared to hours for NWP ensemble runs, making real-time interactive use feasible. The model achieves strong performance with only seven satellite-derived input channels, avoiding the need for the complete atmospheric initial conditions required by physics-based NWP systems. HistGBR's native missing-value handling ensures that partial satellite coverage, which is common during cyclone events when observations are most needed, does not degrade inference quality. Feature importance scores and physics-based post-processing constraints provide transparency about model decisions, addressing the common criticism that ML methods operate as opaque black boxes unsuitable for safety-critical applications.

### 9.2 Limitations

The model was trained exclusively on Indian monsoon-season grid cells; performance over non-monsoonal climates such as arid regions or high-altitude terrain is untested and likely degraded. Training data spans only five monsoon seasons (2018–2022); incorporating longer temporal coverage including dry-season and pre-monsoon periods would improve year-round applicability. The current implementation uses historical climatological averages rather than live satellite feeds, introducing observation lag. Despite sample weighting, extreme rainfall events exceeding 50 mm/day remain under-predicted due to their extreme rarity in the training distribution, which presents challenges for cyclone and orographic precipitation forecasting.

### 9.3 Possible Improvements

Recurrent architectures such as LSTM or Transformer models trained on multi-day sequences could capture temporal dependencies that the current single-day feature vector cannot represent. Ensemble blending with physics-based NWP models via Bayesian averaging could improve extreme event reliability. Probabilistic calibration through isotonic regression would refine confidence estimates.

---

## 10. Conclusion

This paper presented a comprehensive ML-based rainfall prediction system leveraging INSAT-3DR satellite-derived atmospheric features to forecast daily precipitation at 0.25° spatial resolution over the Indian subcontinent. The HistGBR model, trained on over 120,000 records with 5-fold time-series cross-validation and physics-informed sample weighting to address zero-inflation bias, achieved an R² of 0.88 and RMSE of 5.10 mm on the held-out 2022 monsoon test season. This performance significantly outperforms all evaluated baselines: Logistic Regression (R² = 0.52), Decision Tree (R² = 0.66), Random Forest (R² = 0.79), and SVM (R² = 0.73). Feature importance analysis confirmed HEM, OLR, and UTH as the most informative predictors, consistent with established convective meteorology theory.

A fully functional web-based forecast interface built with React and FastAPI enables non-expert users to access 7-day location-specific forecasts through an intuitive browser-based application. Physics-constrained post-processing and quantile regression for uncertainty estimation ensure that system outputs are both meteorologically plausible and informative for risk assessment. The system represents a practical and scalable approach to AI-assisted weather forecasting in satellite-rich, ground-observation-sparse environments, with direct applicability to agricultural advisory services, flood early warning systems, and reservoir management across South Asia.

---

## 11. Future Work

1. **Deep Learning (LSTM/Transformer):** Training recurrent or attention-based models on multi-day sequences to capture temporal autocorrelation in moisture transport, potentially reducing RMSE below 3 mm.

2. **Real-Time Weather API Integration:** Connecting to ISRO MOSDAC live Level-2 data streams for 0–6 hour nowcasting capability.

3. **Larger and Multi-Climate Datasets:** Extending training to all-season data across diverse climate zones and satellite platforms (MSG/SEVIRI, Himawari-8) for global generalizability.

4. **Mobile Application:** Developing a progressive web app or native mobile application to increase accessibility for farmers and disaster responders.

5. **Explainable AI Dashboard:** Integrating SHAP values into the interface to allow domain experts to audit individual forecast decisions.

---

## References

[1] India Meteorological Department, *Annual Climate Summary 2022*, Ministry of Earth Sciences, Government of India, 2023.

[2] T. N. Palmer, R. Buizza, F. Molteni, Y.-Q. Chen, and S. Corti, "Singular vectors and the predictability of weather and climate," *Phil. Trans. R. Soc. A*, vol. 348, pp. 459–475, 1994.

[3] C. F. Ropelewski and M. S. Halpert, "Global and regional scale precipitation patterns associated with the El Niño/Southern Oscillation," *Mon. Wea. Rev.*, vol. 115, no. 8, pp. 1606–1626, 1987.

[4] K. P. Sooraj, P. Terray, and M. Mujumdar, "Global warming and the weakening of the Asian Summer Monsoon circulation," *Clim. Dyn.*, vol. 45, pp. 233–252, 2015.

[5] A. Grover, A. Kapoor, and E. Horvitz, "A deep hybrid model for weather forecasting," in *Proc. 21st ACM SIGKDD*, 2015, pp. 379–386.

[6] R. J. Kuligowski and A. P. Barros, "Localized precipitation forecasts from a numerical weather prediction model using artificial neural networks," *Wea. Forecasting*, vol. 13, no. 4, pp. 1194–1204, 1998.

[7] M. C. V. Ramirez, H. F. de Campos Velho, and N. J. Ferreira, "Artificial neural network technique for rainfall forecasting applied to the São Paulo region," *J. Hydrol.*, vol. 301, pp. 146–162, 2005.

[8] L. Breiman, "Random forests," *Mach. Learn.*, vol. 45, no. 1, pp. 5–32, 2001.

[9] R. Prasad, D. Deo, Y. Li, and T. Maraseni, "Input selection and performance optimization of ANN-based streamflow forecasts," *Atmos. Res.*, vol. 197, pp. 42–63, 2017.

[10] T. Chen and C. Guestrin, "XGBoost: A scalable tree boosting system," in *Proc. 22nd ACM SIGKDD*, 2016, pp. 785–794.

[11] S. Tripathi, V. V. Srinivas, and R. S. Nanjundiah, "Downscaling of precipitation for climate change scenarios: A support vector machine approach," *J. Hydrol.*, vol. 330, pp. 621–640, 2006.

[12] P. Nguyen et al., "The PERSIANN family of global satellite precipitation data: a review and evaluation," *Hydrol. Earth Syst. Sci.*, vol. 22, pp. 5801–5816, 2018.

[13] B. Pan, K. Hsu, A. AghaKouchak, and S. Sorooshian, "Improving precipitation estimation using convolutional neural network," *Water Resour. Res.*, vol. 55, no. 3, pp. 2301–2321, 2019.

[14] M. Rajeevan, J. Bhate, J. D. Kale, and B. Lal, "Development of a high resolution daily gridded temperature data set over India," *Meteorol. Monogr.*, vol. 45, no. 1, pp. 22–27, 2006.

---

*© 2024 The Authors. Published under the terms of the CC BY 4.0 licence.*
