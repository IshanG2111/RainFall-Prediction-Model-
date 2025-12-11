from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Global variables
model_data = None
model = None
metrics = None
scaler = None
grid_df = None
master_df = None

def load_resources():
    global model_data, model, metrics, scaler, grid_df, master_df
    
    # Load Model
    model_path = 'models/model_frame_1.pkl'
    if os.path.exists(model_path):
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
            model = model_data['model']
            metrics = model_data.get('metrics', {'RMSE': 'N/A', 'R2': 'N/A'})
            scaler = model_data.get('scaler')
        print("Model loaded successfully.")
        print(f"Model Metrics: {metrics}")
    else:
        print("Model not found. Please run training script (model.py).")
        
    # Load Grid
    grid_path = 'data_processed/2_days/grid/grid_definition.parquet'
    if os.path.exists(grid_path):
        grid_df = pd.read_parquet(grid_path)
        print(f"Grid loaded: {len(grid_df)} cells.")
    else:
        print("Grid file not found.")

    # Load Master Dataset for realistic sampling
    master_path = 'data_processed/2_days/finaldata/final_dataset.parquet'
    if os.path.exists(master_path):
        master_df = pd.read_parquet(master_path)
        print(f"Master dataset loaded: {len(master_df)} records.")
    else:
        print("Master dataset not found for sampling.")

def get_lat_lon(city_name):
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
    return cities.get(city_name, (20.59, 78.96))

def find_nearest_grid(lat, lon):
    if grid_df is None:
        return None
    distances = np.sqrt((grid_df['lat_center'] - lat)**2 + (grid_df['lon_center'] - lon)**2)
    nearest_idx = distances.argmin()
    return grid_df.iloc[nearest_idx]

def get_realistic_features(grid_id):
    """
    Get realistic features for a given grid.
    Samples from historical data for that grid to simulate realistic weather conditions.
    """
    default_features = {
        'hem': 0, 'wind_speed': 10, 'uth': 40, 'olr': 250, 
        'lst_k': 300, 'cer': 10, 'cot': 10
    }
    
    if master_df is None:
        return default_features

    grid_data = master_df[master_df['grid_id'] == grid_id]
    
    if grid_data.empty:
        sample = master_df.sample(1).iloc[0]
    else:
        sample = grid_data.sample(1).iloc[0]

    features = {
        'hem': sample.get('hem', 0),
        'wind_speed': sample.get('wind_speed', 10),
        'uth': sample.get('uth', 40),
        'olr': sample.get('olr', 250),
        'lst_k': sample.get('lst_k', 300),
        'cer': sample.get('cer', 10),
        'cot': sample.get('cot', 10)
    }
    
    # Add noise
    for k in features:
        features[k] = features[k] * np.random.uniform(0.95, 1.05)
        
    return features

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
            
        grid_id = grid_cell['grid_id']

        predictions = []
        current_date_obj = datetime.strptime(start_date_str, "%Y-%m-%d")
        
        # Feature columns must match training exactly
        feature_cols = [
            'hem', 'wind_speed', 'uth', 'olr', 'lst_k', 'cer', 'cot',
            'month', 'day_of_year'
        ]

        for i in range(7):
            date_target = current_date_obj + timedelta(days=i)
            
            # 1. Get Base Satellite Features
            features_dict = get_realistic_features(grid_id)
            
            # 2. Add Time Features
            features_dict['month'] = date_target.month
            features_dict['day_of_year'] = date_target.timetuple().tm_yday
            
            # 3. Create DataFrame for Input
            input_data = [features_dict.get(col, 0) for col in feature_cols]
            input_df = pd.DataFrame([input_data], columns=feature_cols)
            
            # 4. Scale Features
            if scaler:
                input_df_scaled = scaler.transform(input_df)
            else:
                input_df_scaled = input_df
            
            # 5. Predict (Log Scale)
            pred_log = model.predict(input_df_scaled)[0]
            
            # 6. Inverse Transform (expm1)
            pred_rainfall = np.expm1(pred_log)
            pred_rainfall = max(0, pred_rainfall)
            
            # Determine status
            if pred_rainfall < 0.1:
                status = "No Rain"
            elif pred_rainfall < 2.5:
                status = "Light Rain"
            elif pred_rainfall < 15:
                status = "Moderate Rain"
            else:
                status = "Heavy Rain"
                
            pred_date_str = date_target.strftime("%a, %b %d")
            
            predictions.append({
                'Date': pred_date_str,
                 'Temperature': f"{features_dict['lst_k'] - 273.15:.1f}°C", # LST is in Kelvin
                'Humidity': f"UTH: {features_dict['uth']:.0f}%",
                'Pressure': f"OLR: {int(features_dict['olr'])} W/m²", 
                'Predicted_Rainfall': f"{pred_rainfall:.1f} mm",
                'Status': status,
                # Simple probability heuristic based on prediction magnitude
                'RainProbability': min(100, int(100 * (1 - np.exp(-pred_rainfall/5)))), 
                'Details': {
                    'Wind Speed': f"{features_dict['wind_speed']:.1f} m/s",
                    'COT': f"{features_dict['cot']:.2f}",
                    'CER': f"{features_dict['cer']:.2f}",
                    'HEM': f"{features_dict['hem']:.2f}"
                }
            })
            
        return jsonify({
            'predictions': predictions,
            'model_metrics': metrics
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/cities', methods=['GET'])
def get_cities():
    cities = ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata', 
              'Hyderabad', 'Pune', 'Jaipur', 'Ahmedabad', 'Bhubaneswar']
    return jsonify(cities)

# ... map data endpoint remains the same ...
@app.route('/map-data', methods=['GET'])
def get_map_data():
    try:
        if not os.path.exists('data_processed/2_days/grid/grid_definition.parquet'):
             return jsonify([])
        
        grid = pd.read_parquet('data_processed/2_days/grid/grid_definition.parquet')
        if master_df is not None:
             # Just map some real data
            vis_df = master_df.copy()
            if 'date' in vis_df.columns:
                 first_date = vis_df['date'].iloc[0]
                 vis_df = vis_df[vis_df['date'] == first_date]
            
            merged = pd.merge(grid, vis_df, on='grid_id', how='left').fillna(0)
            
            heatmap_data = []
            for _, row in merged.iterrows():
                val = row.get('rain_mm', 0)
                if val > 0:
                    heatmap_data.append([
                        row['lat_center'],
                        row['lon_center'],
                        min(1.0, val / 50.0)
                    ])
            return jsonify(heatmap_data)
        return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    load_resources()
    app.run(debug=True, port=5000)
