from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Global variables
model = None
grid_df = None

def load_resources():
    global model, grid_df
    
    # Load Model
    model_path = 'models/model_frame_1.pkl'
    if os.path.exists(model_path):
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        print("Model loaded successfully.")
    else:
        print("Model not found. Please run training script.")
        
    # Load Grid
    grid_path = 'data_processed/india_grid.csv'
    if os.path.exists(grid_path):
        grid_df = pd.read_csv(grid_path)
        print(f"Grid loaded: {len(grid_df)} cells.")
    else:
        print("Grid file not found.")

def get_lat_lon(city_name):
    # Mock geocoding for major cities
    cities = {
        'Delhi': (28.61, 77.20),
        'Mumbai': (19.07, 72.87),
        'Bangalore': (12.97, 77.59),
        'Chennai': (13.08, 80.27),
        'Kolkata': (22.57, 88.36),
        'Hyderabad': (17.38, 78.48),
        'Pune': (18.52, 73.85),
        'Jaipur': (26.91, 75.78),
        'Ahmedabad': (23.02, 72.57),
        'Bhubaneswar': (20.29, 85.82)
    }
    return cities.get(city_name, (20.59, 78.96)) # Default to center of India

def find_nearest_grid(lat, lon):
    if grid_df is None:
        return None
    
    # Simple Euclidean distance
    distances = np.sqrt((grid_df['lat_center'] - lat)**2 + (grid_df['lon_center'] - lon)**2)
    nearest_idx = distances.argmin()
    return grid_df.iloc[nearest_idx]

def generate_mock_features():
    # Generate random features for prediction
    # These match the features used in training
    return {
        'HEM_daily': np.random.uniform(0, 100),
        'WDP_wind_mean': np.random.uniform(0, 50),
        'WDP_vorticity': np.random.normal(0, 5),
        'WDP_shear': np.random.uniform(0, 30),
        'UTH_daily': np.random.uniform(20, 100),
        'OLR_daily': np.random.uniform(150, 300),
        'LST_mean': np.random.uniform(15, 45),
        'LST_max': np.random.uniform(20, 50),
        'CMP_cloud_mean': np.random.uniform(0, 1)
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        city = data.get('city', 'Delhi')
        start_date_str = data.get('date')
        
        if not start_date_str:
            return jsonify({'error': 'No date provided'}), 400
            
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500

        lat, lon = get_lat_lon(city)
        grid_cell = find_nearest_grid(lat, lon)
        
        if grid_cell is None:
            return jsonify({'error': 'Grid system not initialized'}), 500

        predictions = []
        current_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        
        for i in range(7):
            # Generate features
            features = generate_mock_features()
            
            # Prepare input dataframe
            input_df = pd.DataFrame([features])
            
            # Predict
            pred_rainfall = model.predict(input_df)[0]
            pred_rainfall = max(0, pred_rainfall) # Ensure non-negative
            
            # Determine status
            if pred_rainfall < 2.5:
                status = "No Rain"
            elif pred_rainfall < 10:
                status = "Light Rain"
            elif pred_rainfall < 50:
                status = "Moderate Rain"
            else:
                status = "Heavy Rain"
                
            # Calculate probability (heuristic based on rainfall amount for this mock)
            # In a real classifier, we'd use predict_proba
            prob = min(95, int(pred_rainfall * 2 + np.random.randint(0, 20)))
            if status == "No Rain":
                prob = min(20, prob)
            
            pred_date = (current_date + timedelta(days=i)).strftime("%a, %b %d")
            
            predictions.append({
                'Date': pred_date,
                'Temperature': f"{features['LST_max']:.1f}°C",
                'Humidity': f"{features['UTH_daily']:.0f}%",
                'Pressure': f"{int(features['OLR_daily'])} hPa", # Mock mapping
                'Predicted_Rainfall': f"{pred_rainfall:.1f} mm",
                'Status': status,
                'RainProbability': prob
            })
            
        return jsonify(predictions)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/cities', methods=['GET'])
def get_cities():
    cities = ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata', 
              'Hyderabad', 'Pune', 'Jaipur', 'Ahmedabad', 'Bhubaneswar']
    return jsonify(cities)

if __name__ == '__main__':
    load_resources()
    app.run(debug=True, port=5000)
