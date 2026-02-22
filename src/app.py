from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import pickle
import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta
from model import PhysicsConstraints

load_dotenv()

# Resolve project root (one level up from src/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, 'templates'))

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
    model_path = os.path.join(BASE_DIR, 'models', 'model_frame_1.pkl')
    if os.path.exists(model_path):
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
            # Support for new multi-model structure (Honest/Quantile models)
            if 'models' in model_data:
                model = model_data['models']['main'] # Use main model for default predictions
            else:
                model = model_data.get('model') # Fallback for old format
            
            metrics = model_data.get('metrics', {'RMSE': 'N/A', 'R2': 'N/A'})
            scaler = model_data.get('scaler')
        print("Model loaded successfully.")
        print(f"Model Metrics: {metrics}")
    else:
        print("Model not found. Please run training script (model.py).")
        
    # Load Grid
    grid_path = os.path.join(BASE_DIR, 'data', 'grid', 'grid_definition.parquet')
    if os.path.exists(grid_path):
        grid_df = pd.read_parquet(grid_path)
        print(f"Grid loaded: {len(grid_df)} cells.")
    else:
        print("Grid file not found.")
    # Load Master Dataset for realistic sampling
    master_path = os.path.join(BASE_DIR, 'data', 'finaldata', '3months_dataset.parquet')
    if os.path.exists(master_path):
        master_df = pd.read_parquet(master_path)
        print(f"Master dataset loaded: {len(master_df)} records.")
    else:
        print("Master dataset not found for sampling.")

def get_lat_lon(location_name):
    api_key = os.environ.get('OPENCAGE_API_KEY')
    default_coords = (20.5937, 78.9629)
    if not api_key:
        print("Warning: OPENCAGE_API_KEY not found in environment variables.")
        return default_coords
        
    url = f"https://api.opencagedata.com/geocode/v1/json?q={location_name}&key={api_key}&countrycode=in"
    try:
        response = requests.get(url)
        data = response.json()
        if data and data.get('results') and len(data['results']) > 0:
            geometry = data['results'][0]['geometry']
            return geometry['lat'], geometry['lng']
    except Exception as e:
        print(f"Error fetching location from OpenCage: {e}")
        
    return default_coords

def find_nearest_grid(lat, lon):
    if grid_df is None:
        return None
    distances = np.sqrt((grid_df['lat_center'] - lat)**2 + (grid_df['lon_center'] - lon)**2)
    nearest_idx = distances.argmin()
    return grid_df.iloc[nearest_idx]

def get_realistic_features(grid_id, date_target=None):
    """
    Get realistic features for a given grid.
    Samples from historical data for that grid to simulate realistic weather conditions.
    """
    default_features = {
        'hem': 0, 'wind_speed': 10, 'uth': 40, 'olr': 250, 
        'lst_k': 300, 'cer': 10, 'cot': 10
    }
    
    # Generate deterministic seed based on grid and date
    if date_target:
        seed = int(grid_id) + date_target.year * 10000 + date_target.month * 100 + date_target.day
    else:
        seed = int(grid_id)
        
    # Ensure seed is within numpy random state range
    seed = seed % (2**32 - 1)
        
    if master_df is None:
        rng = np.random.default_rng(seed)
        for k in default_features:
            default_features[k] = default_features[k] * rng.uniform(0.95, 1.05)
        return default_features

    grid_data = master_df[master_df['grid_id'] == grid_id]
    
    if grid_data.empty:
        sample = master_df.sample(1, random_state=seed).iloc[0]
    else:
        sample = grid_data.sample(1, random_state=seed).iloc[0]

    features = {
        'hem': sample.get('hem', 0),
        'wind_speed': sample.get('wind_speed', 10),
        'uth': sample.get('uth', 40),
        'olr': sample.get('olr', 250),
        'lst_k': sample.get('lst_k', 300),
        'cer': sample.get('cer', 10),
        'cot': sample.get('cot', 10)
    }
    
    # Add deterministic noise
    rng = np.random.default_rng(seed)
    for k in features:
        features[k] = features[k] * rng.uniform(0.95, 1.05)
        
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
        

        # Feature columns must match training exactly - Updated to match model.py order
        feature_cols = [
            'wind_speed', 'uth', 'olr', 'lst_k', 'cer', 'cot', 'hem',
            'day_sin', 'day_cos', 'week_sin', 'week_cos',
            'olr_uth_interaction', 'temp_moisture'
        ]

        for i in range(7):
            date_target = current_date_obj + timedelta(days=i)
            
            # 1. Get Base Satellite Features
            features_dict = get_realistic_features(grid_id, date_target)
            
            # 2. Add Time Features (Cyclic)
            day_of_year = date_target.timetuple().tm_yday
            week_of_year = date_target.isocalendar()[1]
            
            features_dict['day_sin'] = np.sin(2 * np.pi * day_of_year / 366)
            features_dict['day_cos'] = np.cos(2 * np.pi * day_of_year / 366)
            features_dict['week_sin'] = np.sin(2 * np.pi * week_of_year / 53)
            features_dict['week_cos'] = np.cos(2 * np.pi * week_of_year / 53)

            # 3. Add Interaction Features
            features_dict['olr_uth_interaction'] = (300 - features_dict.get('olr', 250)) * features_dict.get('uth', 40)
            features_dict['temp_moisture'] = features_dict.get('lst_k', 300) * (features_dict.get('uth', 40) / 100)

            # 4. Create DataFrame for Input
            input_data = [features_dict.get(col, 0) for col in feature_cols]
            input_df = pd.DataFrame([input_data], columns=feature_cols)
            
            # 5. Scale Features
            if scaler:
                input_df_scaled = scaler.transform(input_df)
            else:
                input_df_scaled = input_df
            
            # 6. Predict (Log Scale)
            pred_log = model.predict(input_df_scaled)[0]
            
            # 7. Inverse Transform (expm1)
            pred_rainfall = np.expm1(pred_log)
            pred_rainfall = max(0, pred_rainfall)
            
            # --- Apply Physics Constraints (Post-Processing) ---
            # Construct features dict for constraints (needs lat, lon, month, olr, uth)
            constraint_features = {
                'latitude': float(grid_cell['lat_center']),
                'longitude': float(grid_cell['lon_center']),
                'month': date_target.month,
                'olr': features_dict.get('olr', 300),
                'uth': features_dict.get('uth', 0),
                'elevation': 0 # Default (TODO: Add elevation map if critical)
            }
            
            raw_pred = pred_rainfall
            pred_rainfall, clamp_reason = PhysicsConstraints.apply_post_inference_adjustments(pred_rainfall, constraint_features)
            
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
            'model_metrics': metrics,
            'grid_info': {
                'grid_id': int(grid_id),
                'latitude': float(grid_cell['lat_center']),
                'longitude': float(grid_cell['lon_center'])
            }
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('q', '')
    if not query or len(query) < 2:
        return jsonify([])
        
    api_key = os.environ.get('OPENCAGE_API_KEY')
    if not api_key:
        return jsonify([])
        
    url = f"https://api.opencagedata.com/geocode/v1/json?q={query}&key={api_key}&countrycode=in&limit=5"
    try:
        response = requests.get(url)
        data = response.json()
        suggestions = []
        seen = set()
        
        for res in data.get('results', []):
            name = res['formatted']
            if name not in seen:
                seen.add(name)
                suggestions.append(name)
                
        return jsonify(suggestions)
    except Exception as e:
        print(f"Error in autocomplete: {e}")
        return jsonify([])

# Removed /cities endpoint as locations are now dynamic

# ... map data endpoint remains the same ...
@app.route('/map-data', methods=['GET'])
def get_map_data():
    try:
        grid_path = os.path.join(BASE_DIR, 'data', 'grid', 'grid_definition.parquet')
        if not os.path.exists(grid_path):
             return jsonify([])
        
        grid = pd.read_parquet(grid_path)
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
