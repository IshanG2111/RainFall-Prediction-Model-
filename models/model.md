# INSAT-3DR AI Rainfall Prediction Model

## Overview
This model utilizes machine learning to predict daily rainfall (in mm) based on satellite meteorological data and temporal features. It is designed to handle the complex, non-linear relationships between atmospheric parameters and precipitation.

## Model Architecture
- **Algorithm**: `HistGradientBoostingRegressor` (Histogram-based Gradient Boosting).
- **Implementation**: Scikit-Learn (`sklearn.ensemble`).
- **Key Characteristics**:
    - **Gradient Boosting**: Builds an ensemble of decision trees sequentially, with each tree correcting the errors of the previous ones.
    - **Histogram-based**: Optimized for speed and efficiency on large datasets by binning continuous features.
    - **Non-linear**: Capable of capturing complex weather patterns that linear models miss.

## Features (Inputs)
The model consumes 9 input features, primarily derived from **INSAT-3DR** satellite data:

1.  **HEM**: Hydro-Estimator Method (Satellite-derived rainfall estimate).
2.  **Wind Speed**: Surface wind speed (m/s).
3.  **UTH**: Upper Tropospheric Humidity (%).
4.  **OLR**: Outgoing Longwave Radiation (W/m²). Low OLR indicates high, cold clouds (storms).
5.  **LST_K**: Land Surface Temperature (Kelvin).
6.  **CER**: Cloud Effective Radius (microns).
7.  **COT**: Cloud Optical Thickness.
8.  **Month**: Temporal feature to capture seasonal variances (Monsoon vs. Dry season).
9.  **Day of Year**: Temporal feature for finer daily granularity.

## Preprocessing Pipeline
1.  **Data Cleaning**: Rows with missing values in critical columns are dropped.
2.  **Target Transformation**: 
    - Rainfall data makes a **Log Transformation** (`log(1 + x)`) applied to the target variable (`rain_mm`) before training.
    - This handles the "zero-inflated" nature of rainfall data (many days with 0mm) and reduces the impact of extreme outliers (heavy storms).
3.  **Feature Scaling**:
    - **StandardScaler**: All input features are normalized (mean=0, variance=1) to ensure the model treats all features equally regardless of their raw units (e.g., Kelvin vs. Percentage).

## Training Configuration
- **Max Iterations**: 500 trees.
- **Learning Rate**: 0.05.
- **Max Depth**: 10 (Allows capturing deep interactions between features).
- **Validation**: 80/20 Train-Test split.

## Performance
- **R² Score**: ~0.92 (Explains 92% of the variance in rainfall).
- **RMSE**: ~6.9 mm (Average error margin).

## Inference Workflow (Prediction)
1.  **Input**: City/Grid Location + Date.
2.  **Feature Extraction**: Retrieves historical/satellite parameters for that specific grid cell.
3.  **Scaling**: Applies the saved `StandardScaler`.
4.  **Prediction**: Model predicts the log-rainfall value.
5.  **Inverse Transform**: The prediction is converted back to millimeters via exponential transformation (`exp(x) - 1`).
6.  **Classification**: 
    - < 0.1mm: No Rain
    - 0.1 - 2.5mm: Light Rain
    - 2.5 - 15mm: Moderate Rain
    - > 15mm: Heavy Rain
