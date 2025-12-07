# Rainfall Prediction Model (AI-Based) 🌦️

This project implements an advanced AI-based rainfall prediction system using **INSAT-3DR satellite data** and **Machine Learning (HistGradientBoosting Regressor)**. It predicts daily rainfall amounts (in mm) for locations across India for the next 7 days.

![UI Screenshot](image.png)

## 🚀 Features

*   **Satellite-Driven**: Uses realistic satellite parameters like:
    *   **HEM** (Hydro-Estimator Rainfall)
    *   **OLR** (Outgoing Longwave Radiation)
    *   **UTH** (Upper Tropospheric Humidity)
    *   **WDP** (Wind Derived Products - Speed, Vorticity, Shear)
    *   **LST** (Land Surface Temperature)
*   **Advanced Regression**: Predicts exact rainfall quantity using a Gradient Boosting model with Log-Transformation for high accuracy (**R² Step: ~0.76**).
*   **Interactive UI**: Modern, glassmorphism-based interface with dynamic weather animations and detailed 7-day forecasts.
*   **Realistic Simulation**: Simulates physically consistent weather patterns for future dates.

## 🛠️ Setup & Installation

1.  **Clone the repository** (if applicable).
2.  **Install Dependencies**:
    ```bash
    pip install flask pandas numpy scikit-learn
    ```

## 🏃‍♂️ How to Run

Follow these steps to set up the data, train the model, and launch the application.

### 1. Generate Dataset
Generate the synthetic satellite dataset (physically correlated) to simulate realistic weather patterns.
```bash
python generate_data.py
```
*This creates `data_processed/master_dataset.parquet`.*

### 2. Train the Model
Train the HistGradientBoosting Regressor on the generated data.
```bash
python model.py
```
*This saves the trained model and metrics to `models/model_frame_1.pkl`.*

### 3. Start the Application
Launch the Flask web server.
```bash
python app.py
```
*Access the app at `http://127.0.0.1:5000`*

## 📂 Project Structure

*   `app.py`: Main Flask application handling API requests and serving the frontend.
*   `model.py`: Script to train the regression model and save artifacts.
*   `generate_data.py`: Utility to generate correlated synthetic satellite data.
*   `templates/index.html`: The frontend user interface.
*   `data_processed/`: Contains the spatial grid (`india_grid.csv`) and generated datasets.
*   `models/`: Stores the trained model binary (`.pkl`).

## 📊 Model Performance
*   **R² Score**: ~0.76 (High Predictive Power)
*   **RMSE**: ~11.8 mm

---
*Developed for Rainfall Prediction Project - 6th Sem*
