# Feature Engineering in the Rainfall Prediction Model

Feature engineering is a critical part of this model to help the machine learning algorithm (`HistGradientBoostingRegressor`) better understand the non-linear, temporal, and physical relationships in meteorological data.

The feature engineering pipeline is implemented in the `RainfallPredictor.feature_engineering()` method in `src/model.py`, and is identically reconstructed during inference in `src/app.py`.

Here is a breakdown of how feature engineering is being used in the project:

## 1. Cyclic Encoding for Time Features
Rainfall and weather patterns are highly seasonal. However, standard numerical representations of time (like day 1 vs. day 365) trick models into thinking the end of the year is far away from the beginning of the new year, when in reality, they are consecutive.

To solve this, **Sine and Cosine transformations** are applied to the day of the year and week of the year to preserve their cyclical, continuous nature:
*   **`day_sin` / `day_cos`**: $sin(2\pi \cdot \frac{\text{day\_of\_year}}{366})$ and $cos(2\pi \cdot \frac{\text{day\_of\_year}}{366})$
*   **`week_sin` / `week_cos`**: $sin(2\pi \cdot \frac{\text{week\_of\_year}}{53})$ and $cos(2\pi \cdot \frac{\text{week\_of\_year}}{53})$

This ensures that December 31st and January 1st are represented as coordinates close to each other in the feature space.

## 2. Meteorological Interaction Features
Instead of relying entirely on the model to figure out complex physical relationships between different variables, explicit interaction terms are derived based on atmospheric physics:

*   **`olr_uth_interaction`**: Calculated as `(300 - olr) * uth`. 
    *   **OLR (Outgoing Longwave Radiation)**: Lower values indicate taller, colder clouds.
    *   **UTH (Upper Tropospheric Humidity)**: Higher values indicate more moisture.
    *   *Why it works:* Subtracting OLR from 300 inverts the scale so that higher numbers mean deeper clouds. Multiplying this by UTH creates a powerful combined feature that surges when there is *both* deep convection *and* ample moisture—a primary indicator of heavy rainfall.
    
*   **`temp_moisture`**: Calculated as `lst_k * (uth / 100)`.
    *   *Why it works:* It combines Land Surface Temperature (LST) and Humidity (UTH). High surface temperatures drive convection, but rain only occurs if moisture is available. This feature explicitly links the thermal trigger with the moisture supply.

## 3. Target Variable Transformation
Rainfall data (`rain_mm`) is typically zero-inflated (it doesn't rain most days) and heavily right-skewed (few extreme rainfall events).
*   **Log Transformation (`np.log1p`)**: Before training, the target variable is transformed using `y_log = np.log1p(y)` (which computes `log(1 + y)`). This compresses the long tail of extreme rain events, making the target distribution more bell-shaped and easier for the regressor to fit.
*   **Inverse Transformation (`np.expm1`)**: During inference (`app.py`), the model predicts the log value, which is converted back to millimeters using `np.expm1(pred_log)`.

## 4. Feature Scaling (`StandardScaler`)
Different features have vastly different numerical ranges (e.g., `olr` ranges from 100-300, `wind_speed` from 0-60, and `day_sin` from -1 to 1). If unscaled, features with larger numbers would dominate the model's cost function.
*   All input features are standardized using `sklearn.preprocessing.StandardScaler` to have a mean of 0 and a variance of 1.

## 5. Domain-Specific Data Clipping (Cleaning)
Before feature engineering, raw physical variables are rigidly clamped to realistic meteorological thresholds in the `clean_data()` step.
*   For example: `lst_k` is clamped between 180 and 340 Kelvin; `uth` between 0 and 100%. This removes extreme outliers or sensor errors that could severely warp the model.

## 6. Simulated Features during Inference (`app.py`)
Because future satellite data isn't available at the time of prediction, `app.py` features a `get_realistic_features()` function. 
*   It looks up the geographical grid and the target date's month/day.
*   It deterministically samples from historical data for that exact grid to populate base features (`olr`, `uth`, etc.).
*   A calculated uniform noise (`rng.uniform(0.95, 1.05)`) is injected to simulate slight, realistic variations rather than repeating historical values perfectly. Afterwards, all engineered features (interactions and cyclic time) are built on top of this sampled data.
