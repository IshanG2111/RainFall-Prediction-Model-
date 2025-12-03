# 🌧️ Rainfall Prediction Model

An AI-powered rainfall prediction system using Linear Regression to forecast rainfall for the next 7 days with an interactive, premium web interface.

## ✨ Features

### Core Functionality
- **Linear Regression Model**: Predicts rainfall based on Temperature, Humidity, and Pressure
- **7-Day Forecast**: Generates predictions for the next week with simulated weather variations
- **Rainfall Probability**: Calculates and displays rainfall probability percentage (0-100%)
- **CLI Support**: Command-line interface for quick predictions
- **Comprehensive Dataset**: Uses Indian rainfall data across states and years (1901-2015)

### Premium UI/UX
- **Tomorrow's Forecast Hero Card**: Prominently displays tomorrow's prediction with large animated probability counter
- **Animated CountUp**: Smooth number animations for rainfall probability percentages
- **Glassmorphism Design**: Modern frosted glass effects with backdrop blur
- **Color-Coded Status**: Visual indicators for No Rain, Light Rain, Moderate Rain, and Heavy Rain
- **Responsive Layout**: Optimized for desktop and mobile devices
- **Minimal Dark Theme**: Clean, professional interface with gradient accents
- **Smooth Animations**: Staggered card animations and transitions for enhanced user experience
### Visuals
- **Preview Image**: A screenshot of the web interface to showcase the design
![Screenshot of the Rainfall Prediction Model web interface](image.png)

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

3. **Select a date** and click "Generate Forecast" to see:
   - **Tomorrow's Forecast**: Large hero card with animated rainfall probability percentage
   - **7-Day Overview**: Grid of remaining 6 days with individual probability counters
   - **Weather Details**: Temperature, humidity, and pressure for each day
   - **Color-coded status**: Visual indicators based on rainfall intensity

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

### Backend
- **Python 3.x**
- **pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations
- **scikit-learn**: Machine learning model (Linear Regression)
- **Flask**: Web framework for API and serving

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with CSS variables, gradients, and animations
- **JavaScript (ES6+)**: Interactive functionality and animations
- **Inter Font**: Premium typography from Google Fonts
- **Glassmorphism**: Frosted glass UI effects with backdrop-filter
- **Custom CountUp Animation**: Vanilla JS implementation for number animations

## Future Enhancements

- Integration with real-time weather APIs (OpenWeatherMap, Weather.gov)
- Support for multiple locations with geolocation
- Advanced ML models (Random Forest, LSTM Neural Networks, XGBoost)
- Historical data visualization with interactive charts
- Export forecast data to PDF/CSV
- Push notifications for severe weather alerts
- Weather radar integration
- Hourly forecast in addition to daily predictions

## License

This project is open-source and available for educational purposes.
