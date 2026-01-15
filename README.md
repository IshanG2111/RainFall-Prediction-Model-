# Rainfall Prediction Model (AI-Based) 🌦️

This project implements an advanced AI-based rainfall prediction system using **INSAT-3DR satellite data** and **Machine Learning ( )**. It predicts daily rainfall amounts (in mm) for locations across India for the next 7 days.

![UI Screenshot](image.png)

## 🚀 Features

*   **Satellite-Driven**: Uses realistic satellite parameters like:
    *   **HEM** (Hydro-Estimator Rainfall)
    *   **OLR** (Outgoing Longwave Radiation)
    *   **UTH** (Upper Tropospheric Humidity)
    *   **WDP** (Wind Derived Products - Speed)
    *   **LST** (Land Surface Temperature / Cloud Top Temp)
    *   **COT** (Cloud Optical Thickness)
    *   **CER** (Cloud Effective Radius)
*   **Advanced Regression**: Predicts exact rainfall quantity using a **HistGradientBoostingRegressor** with Log-Transformation for high accuracy.
*   **Interactive UI**: Modern, glassmorphism-based interface with dynamic weather animations and detailed 7-day forecasts.
*   **Geolocation**: Uses a 0.25° grid system to find the nearest weather data for selected cities.

## 🛠️ Setup & Installation

1.  **Clone the repository** (if applicable).
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## 🏃‍♂️ How to Run

Follow these steps to train the model and launch the application.

### 1. Train the Model
Train the HistGradientBoosting Regressor on the processed dataset.
```bash
python model.py
```
*This saves the trained model and metrics to `models/model_frame_1.pkl`.*

### 2. Start the Application
Launch the Flask web server.
```bash
python app.py
```
*Access the app at `http://127.0.0.1:5000`*

## 📂 Project Structure

*   `app.py`: Main Flask application handling API requests, grid lookup, and serving the frontend.
*   `model.py`: Script to train the regression model and save artifacts.
*   `model_details.md`: Detailed documentation of model architecture and prediction logic.
*   `requirements.txt`: List of Python dependencies.
*   `templates/index.html`: The frontend user interface.
*   `data_processed/`: Contains the processed parquet datasets and grid definitions.
*   `models/`: Stores the trained model binary (`.pkl`).

## 📊 Model Performance
*   **R² Score**: ~0.93 (High Predictive Power)
*   **RMSE**: ~6.90 mm
*   **MAE**: ~2.97 mm

## ⚡ Performance Optimizations (NEW)
This project includes advanced performance optimizations for handling large datasets:
*   **Memory Efficiency**: 37% memory reduction through optimized data types
*   **Fast Predictions**: 85x faster with batch processing (0.04ms vs 3.74ms per prediction)
*   **Smart Caching**: LRU cache with TTL for predictions and grid lookups (70-90% hit rate)
*   **Spatial Indexing**: 5.8x faster location-to-grid mapping
*   **Scalability**: Handles datasets from 30K to 10M+ rows with configurable sampling
*   **Monitoring**: Built-in performance profiling and metrics API

See [PERFORMANCE_GUIDE.md](PERFORMANCE_GUIDE.md) for detailed documentation and [PERFORMANCE_ANALYSIS.md](PERFORMANCE_ANALYSIS.md) for benchmark results.

---
*Developed for Rainfall Prediction Project - 6th Sem*
