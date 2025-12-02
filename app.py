from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import main

app = Flask(__name__)

# Global variables to hold model and initial state
model = None
last_known_weather = None

def initialize_model():
    global model, last_known_weather
    data_file = "rainfall_data.csv"
    df = main.load_data(data_file)
    if df is not None:
        X, y = main.preprocess_data(df)
        model = main.train_model(X, y)
        last_row = df.iloc[-1]
        last_known_weather = [last_row['Temperature'], last_row['Humidity'], last_row['Pressure']]
        print("Model initialized successfully.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    start_date_str = data.get('date')
    
    if not start_date_str:
        return jsonify({'error': 'No date provided'}), 400
        
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    if model is None:
        return jsonify({'error': 'Model not initialized'}), 500

    predictions = []
    # Start from the last known weather from the dataset
    # In a real app, we might want to fetch historical weather for the start_date if it's in the past,
    # or forecast data if it's in the future. 
    # Here we stick to the simulation logic from main.py.
    current_weather = list(last_known_weather) 
    
    for i in range(7):
        current_date = start_date + timedelta(days=i)
        
        # Simulate weather changes (random small fluctuations)
        # Temp +/- 1, Humidity +/- 2, Pressure +/- 1
        current_weather[0] += np.random.uniform(-1, 1)
        current_weather[1] += np.random.uniform(-2, 2)
        current_weather[2] += np.random.uniform(-1, 1)
        
        # Ensure realistic bounds
        current_weather[1] = min(100, max(0, current_weather[1])) # Humidity 0-100
        
        input_features = np.array([current_weather]).reshape(1, -1)
        predicted_rainfall = model.predict(input_features)[0]
        
        # Rainfall cannot be negative
        predicted_rainfall = max(0, predicted_rainfall)
        
        status = "No Rain"
        if predicted_rainfall > 0.5:
            status = "Light Rain"
        if predicted_rainfall > 5:
            status = "Moderate Rain"
        if predicted_rainfall > 15:
            status = "Heavy Rain"
            
        predictions.append({
            "Date": current_date.strftime('%a, %b %d'),
            "Temperature": f"{current_weather[0]:.1f}°C",
            "Humidity": f"{current_weather[1]:.1f}%",
            "Pressure": f"{current_weather[2]:.1f}hPa",
            "Predicted_Rainfall": f"{predicted_rainfall:.2f}mm",
            "Status": status
        })
        
    return jsonify(predictions)

if __name__ == '__main__':
    initialize_model()
    app.run(debug=True, port=5000)
