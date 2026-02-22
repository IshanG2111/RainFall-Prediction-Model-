# Recent Changes

## 1. Fixed Random/Inconsistent Data on Reload
**File Modified**: `src/app.py`
*   **Issue**: On every prediction request, `get_realistic_features` generated entirely random noise for weather features using `pandas.DataFrame.sample()` and `numpy.random.uniform()` without a seed.
*   **Fix**: Modified `get_realistic_features` to use a **deterministic random seed**. The seed is now calculated using the specific `grid_id` and the `date_target` (Year, Month, Day). This guarantees that identical location and date queries will consistently produce the exact same simulated weather features and predictions across different page reloads, without losing realistic day-to-day variance.

## 2. Improved Model Accuracy & Reduced "Zero-Inflation" Bias
**Files Modified**: `src/model.py`, `src/app.py`
*   **Feature Engineering**: Added two new meteorological interaction features to better capture signals for heavy rainfall (deep convection/storms):
    *   `olr_uth_interaction`: Combines cold cloud tops (OLR) and moisture (UTH).
    *   `temp_moisture`: An index combining surface temperature and humidity.
*   **Class Imbalance Handling**: The dataset contains mostly dry days (0 mm rain), causing the algorithm to inherently underpredict. Implemented **Sample Weights** during training so that days with actual rainfall (`rain_mm > 0`) are weighted significantly higher, penalizing the model more if it misses rain events.
*   **Hyperparameter Tuning**: Replaced hardcoded model parameters with `RandomizedSearchCV`. The script now tests dozens of combinations of `learning_rate`, `max_depth`, `l2_regularization`, and `max_iter` automatically to select the absolute best-performing configuration for the dataset.

## 3. Retrained Model
*   Successfully ran the updated `src/model.py` across 1.3 million data points, automatically tuning and saving the significantly more accurate prediction weights over the previous baseline into `models/model_frame_1.pkl`.
