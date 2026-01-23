# Honest & Realistic Rainfall Prediction Model 🌦️

This project implements an advanced, scientifically grounded AI system for rainfall prediction using **INSAT-3DR satellite data** and **Machine Learning**. 

Unlike standard "black box" models, this system is designed to be **Honest** (transparent evaluation, proper uncertainty quantification) and **Realistic** (enforcing physical meteorological laws).

![UI Screenshot](image.png)

## 🚀 Key Innovation: Honest & Realistic AI

### 1. Honest Evaluation
-   **No Cheating**: We use **5-Fold Time-Series Cross-Validation** to test the model on "future" unseen data, preventing data leakage.
-   **Data Integrity**: The model learns from **broken/incomplete data** (handling missing sensor readings) rather than discarding 75% of the dataset.

### 2. Realistic Physics
-   **Physics Constraints**: Post-processing logic enforces meoreological rules (e.g., *Clear Sky = No Rain*) to stop the AI from "hallucinating" rain.
-   **Uncertainty Quantification**: The model predicts both the **Most Likely Rain** and an **Extreme Scenario (95th Percentile)** to capture cyclone risks.

## 📡 Features

*   **Satellite-Driven**: Uses realistic satellite parameters:
    *   **HEM** (Hydro-Estimator Rainfall) - Primary Satellite Signal
    *   **OLR** (Outgoing Longwave Radiation) - Cloud Top Height
    *   **UTH** (Upper Tropospheric Humidity) - Moisture Source
    *   **LST** (Land Surface Temperature) - Convection Trigger
    *   **WDP** (Wind Speed) - Moisture Transport
    *   **COT** & **CER** - Cloud Microphysics
*   **Temporal Intelligence**: Uses Cyclic Time features (Sine/Cosine of Day/Week) to capture seasonality without overfitting to specific years.
*   **Advanced Architecture**: 
    *   **HistGradientBoostingRegressor** for native missing value handling.
    *   **Quantile Regression** for uncertainty ranges.

## 📊 Model Performance (Honest Benchmarks)
Tested on ~120,000 records using Time-Series Split:

*   **RMSE**: **5.10 mm** (High Precision)
*   **R² Score**: **0.88** (Strong Predictive Power)
*   **MAE**: **0.54 mm** (Low Average Error)

---

## 🛠️ Setup & Installation

1.  **Clone the repository**.
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## 🏃‍♂️ How to Run

### 1. Train the Model
Train the HistGradientBoosting Regressor (Main + Quantile Models).
```bash
python model.py
```
*Saves trained models to `models/model_frame_1.pkl`.*

### 2. Start the Application
Launch the Flask web server.
```bash
python app.py
```
*Access the app at `http://127.0.0.1:5000`*

## 📂 Project Structure

*   `app.py`: Flask web application (Inference Engine).
*   `model.py`: Training script with Physics Constraints & Validation.
*   `Rainfall_Prediction_Features.md`: Detailed feature documentation.
*   `physics.md`: Scientific background & Applied constraints.
*   `data_processed/`: Processed parquet datasets.
*   `models/`: Trained model binaries.

---
*Developed for Rainfall Prediction Project - 6th Sem*
