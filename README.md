# Rainfall Prediction Model

A machine learning-based rainfall prediction system using Linear Regression to forecast rainfall for the next 7 days based on weather parameters.

## Features

- **Linear Regression Model**: Predicts rainfall based on Temperature, Humidity, and Pressure
- **7-Day Forecast**: Generates predictions for the next week with simulated weather variations
- **Web Interface**: Modern, dark-themed UI for interactive predictions
- **CLI Support**: Command-line interface for quick predictions
- **Comprehensive Dataset**: Uses Indian rainfall data across states and years (1901-2015)

## Dataset

The project uses `rainfall_india_states_linear_regression_cleaned.csv`, which contains:
- Historical rainfall data for Indian states
- Monthly rainfall measurements (JAN-DEC)
- Annual rainfall totals
- Seasonal aggregations (Jan-Feb, Mar-May, Jun-Sep, Oct-Dec)
- Data spanning from 1901 to 2015

## Project Structure

```
RainFall-Prediction-Model-/
├── app.py                          # Flask web application
├── main.py                         # CLI prediction script
├── templates/
│   └── index.html                  # Web UI template
├── rainfall_india_states_linear_regression_cleaned.csv  # Main dataset
├── rainfall_data.csv               # Sample dataset
└── README.md
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd RainFall-Prediction-Model-
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install pandas numpy scikit-learn flask
   ```

## Usage

### Web Interface

1. **Start the Flask application**
   ```bash
   python app.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://127.0.0.1:5000
   ```

3. **Select a date** and click "Predict Next 7 Days" to see the forecast

### Command Line Interface

Run the prediction script directly:
```bash
python main.py
```

This will:
- Load the dataset
- Train the Linear Regression model
- Display the Mean Squared Error
- Generate and display 7-day rainfall predictions

## Model Details

- **Algorithm**: Linear Regression
- **Features**: Temperature (°C), Humidity (%), Pressure (hPa)
- **Target**: Rainfall (mm)
- **Train-Test Split**: 80-20
- **Evaluation Metric**: Mean Squared Error (MSE)

## Rainfall Categories

The model classifies predictions into four categories:
- **No Rain**: < 0.5mm
- **Light Rain**: 0.5mm - 5mm
- **Moderate Rain**: 5mm - 15mm
- **Heavy Rain**: > 15mm

## Technologies Used

- **Python 3.x**
- **pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations
- **scikit-learn**: Machine learning model
- **Flask**: Web framework
- **HTML/CSS/JavaScript**: Frontend interface

## Future Enhancements

- Integration with real-time weather APIs
- Support for multiple locations
- Advanced ML models (Random Forest, Neural Networks)
- Historical data visualization
- Mobile-responsive design improvements

## License

This project is open-source and available for educational purposes.
