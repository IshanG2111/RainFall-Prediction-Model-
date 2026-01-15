from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime, timedelta
from performance_utils import (
    LRUCache, timed, optimize_dataframe_dtypes, 
    GridIndex, perf_monitor, sample_large_dataset
)
import performance_config as config

app = Flask(__name__)

# Global variables
model_data = None
model = None
metrics = None
scaler = None
grid_df = None
master_df = None
grid_index = None

# Caching
prediction_cache = LRUCache(
    max_size=config.MAX_CACHE_ENTRIES, 
    ttl_seconds=config.CACHE_TTL_SECONDS
) if config.ENABLE_CACHE else None

grid_cache = LRUCache(
    max_size=config.GRID_CACHE_SIZE,
    ttl_seconds=config.CACHE_TTL_SECONDS * 2
) if config.ENABLE_CACHE else None

@timed("load_resources")
def load_resources():
    global model_data, model, metrics, scaler, grid_df, master_df, grid_index
    
    # Load Model
    model_path = 'models/model_frame_1.pkl'
    if os.path.exists(model_path):
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
            model = model_data['model']
            metrics = model_data.get('metrics', {'RMSE': 'N/A', 'R2': 'N/A'})
            scaler = model_data.get('scaler')
        print("✓ Model loaded successfully.")
        print(f"  Model Metrics: {metrics}")
    else:
        print("⚠ Model not found. Please run training script (model.py).")
        
    # Load Grid with optimization
    grid_path = 'data_processed/2_days/grid/grid_definition.parquet'
    if os.path.exists(grid_path):
        grid_df = pd.read_parquet(grid_path)
        grid_df = optimize_dataframe_dtypes(grid_df)
        
        # Build spatial index for fast lookups
        if config.ENABLE_GRID_INDEX:
            grid_index = GridIndex(grid_df)
            print(f"✓ Grid loaded with spatial index: {len(grid_df)} cells.")
        else:
            print(f"✓ Grid loaded: {len(grid_df)} cells.")
    else:
        print("⚠ Grid file not found.")

    # Load Master Dataset with optimizations
    master_path = 'data_processed/2_days/finaldata/final_dataset.parquet'
    if os.path.exists(master_path):
        if config.USE_LAZY_LOADING:
            # For huge datasets, sample or load on-demand
            temp_df = pd.read_parquet(master_path)
            
            # Check if dataset is large
            data_size_mb = temp_df.memory_usage(deep=True).sum() / (1024**2)
            if data_size_mb > config.MAX_MEMORY_MB:
                print(f"⚠ Large dataset detected ({data_size_mb:.1f}MB). Applying sampling...")
                master_df = sample_large_dataset(temp_df)
            else:
                master_df = temp_df
            
            master_df = optimize_dataframe_dtypes(master_df)
            print(f"✓ Master dataset loaded: {len(master_df)} records ({master_df.memory_usage(deep=True).sum() / (1024**2):.1f}MB)")
        else:
            master_df = pd.read_parquet(master_path)
            print(f"✓ Master dataset loaded: {len(master_df)} records.")
    else:
        print("⚠ Master dataset not found for sampling.")

def get_lat_lon(city_name):
    # Comprehensive list of major Indian cities
    cities = {
        'Delhi': (28.6139, 77.2090), 'Mumbai': (19.0760, 72.8777), 'Bangalore': (12.9716, 77.5946),
        'Chennai': (13.0827, 80.2707), 'Kolkata': (22.5726, 88.3639), 'Hyderabad': (17.3850, 78.4867),
        'Pune': (18.5204, 73.8567), 'Jaipur': (26.9124, 75.7873), 'Ahmedabad': (23.0225, 72.5714),
        'Bhubaneswar': (20.2961, 85.8245), 'Lucknow': (26.8467, 80.9462), 'Kanpur': (26.4499, 80.3319),
        'Nagpur': (21.1458, 79.0882), 'Indore': (22.7196, 75.8577), 'Thane': (19.2183, 72.9781),
        'Bhopal': (23.2599, 77.4126), 'Visakhapatnam': (17.6868, 83.2185), 'Patna': (25.5941, 85.1376),
        'Vadodara': (22.3072, 73.1812), 'Ghaziabad': (28.6692, 77.4538), 'Ludhiana': (30.9010, 75.8573),
        'Agra': (27.1767, 78.0081), 'Nashik': (19.9975, 73.7898), 'Ranchi': (23.3441, 85.3096),
        'Faridabad': (28.4089, 77.3178), 'Meerut': (28.9845, 77.7064), 'Rajkot': (22.3039, 70.8022),
        'Surat': (21.1702, 72.8311), 'Varanasi': (25.3176, 82.9739), 'Srinagar': (34.0837, 74.7973),
        'Aurangabad': (19.8762, 75.3433), 'Dhanbad': (23.7957, 86.4304), 'Amritsar': (31.6340, 74.8723),
        'Navi Mumbai': (19.0330, 73.0297), 'Allahabad': (25.4358, 81.8463), 'Howrah': (22.5958, 88.2636),
        'Gwalior': (26.2183, 78.1828), 'Jabalpur': (23.1815, 79.9864), 'Coimbatore': (11.0168, 76.9558),
        'Vijayawada': (16.5062, 80.6480), 'Jodhpur': (26.2389, 73.0243), 'Madurai': (9.9252, 78.1198),
        'Raipur': (21.2514, 81.6296), 'Kota': (25.0961, 75.8482), 'Guwahati': (26.1445, 91.7364),
        'Chandigarh': (30.7333, 76.7794), 'Trivandrum': (8.5241, 76.9366), 'Mysore': (12.2958, 76.6394),
        'Tiruchirappalli': (10.7905, 78.7047), 'Bareilly': (28.3670, 79.4304), 'Dehradun': (30.3165, 78.0322),
        'Cuttack': (20.4625, 85.8830), 'Kochi': (9.9312, 76.2673), 'Udaipur': (24.5854, 73.7125)
    }
    # Case insensitive lookup
    city_map = {k.lower(): v for k, v in cities.items()}
    return city_map.get(city_name.lower(), (20.5937, 78.9629))

@timed("find_nearest_grid")
def find_nearest_grid(lat, lon):
    if grid_df is None:
        return None
    
    # Check cache first
    if grid_cache:
        cache_key = f"{lat:.4f},{lon:.4f}"
        cached = grid_cache.get(cache_key)
        if cached is not None:
            return cached
    
    # Use spatial index if available
    if grid_index and config.ENABLE_GRID_INDEX:
        result = grid_index.find_nearest(lat, lon)
    else:
        # Fallback to numpy vectorized calculation
        from performance_utils import vectorized_distance
        distances = vectorized_distance(lat, lon, 
                                       grid_df['lat_center'].values,
                                       grid_df['lon_center'].values)
        nearest_idx = distances.argmin()
        result = grid_df.iloc[nearest_idx]
    
    # Cache result
    if grid_cache:
        grid_cache.put(cache_key, result)
    
    return result

@timed("get_realistic_features")
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

    # Filter for specific grid
    grid_data = master_df[master_df['grid_id'] == grid_id]
    
    if grid_data.empty:
        # Sample from overall dataset if no data for this grid
        if len(master_df) > 0:
            sample = master_df.sample(1).iloc[0]
        else:
            return default_features
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
@timed("predict_endpoint")
def predict():
    try:
        data = request.get_json()
        city = data.get('city', 'Delhi')
        start_date_str = data.get('date')
        
        if not start_date_str:
            return jsonify({'error': 'No date provided'}), 400
            
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500

        # Check cache for this prediction
        cache_key = f"{city}:{start_date_str}"
        if prediction_cache:
            cached_result = prediction_cache.get(cache_key)
            if cached_result is not None:
                return jsonify(cached_result)

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

        # Vectorized prediction preparation
        all_inputs = []
        dates = []
        
        for i in range(7):
            date_target = current_date_obj + timedelta(days=i)
            dates.append(date_target)
            
            # 1. Get Base Satellite Features
            features_dict = get_realistic_features(grid_id)
            
            # 2. Add Time Features
            features_dict['month'] = date_target.month
            features_dict['day_of_year'] = date_target.timetuple().tm_yday
            
            # 3. Create input row
            input_data = [features_dict.get(col, 0) for col in feature_cols]
            all_inputs.append((input_data, features_dict))
        
        # Batch prediction - process all 7 days at once
        input_matrix = np.array([inp[0] for inp in all_inputs])
        input_df = pd.DataFrame(input_matrix, columns=feature_cols)
        
        # 4. Scale Features
        if scaler:
            input_df_scaled = scaler.transform(input_df)
        else:
            input_df_scaled = input_df
        
        # 5. Batch Predict (Log Scale)
        pred_logs = model.predict(input_df_scaled)
        
        # 6. Process predictions
        for i, (date_target, pred_log) in enumerate(zip(dates, pred_logs)):
            features_dict = all_inputs[i][1]
            
            # Inverse Transform (expm1)
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
        
        result = {
            'predictions': predictions,
            'model_metrics': metrics
        }
        
        # Cache the result
        if prediction_cache:
            prediction_cache.put(cache_key, result)
            
        return jsonify(result)

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
@timed("map_data_endpoint")
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

@app.route('/performance', methods=['GET'])
def get_performance_stats():
    """Endpoint to get performance statistics"""
    stats = perf_monitor.get_stats()
    cache_info = {}
    if prediction_cache:
        cache_info['prediction_cache_size'] = prediction_cache.size()
    if grid_cache:
        cache_info['grid_cache_size'] = grid_cache.size()
    
    return jsonify({
        'performance_metrics': stats,
        'cache_info': cache_info,
        'config': {
            'caching_enabled': config.ENABLE_CACHE,
            'max_cache_entries': config.MAX_CACHE_ENTRIES,
            'grid_index_enabled': config.ENABLE_GRID_INDEX,
            'lazy_loading': config.USE_LAZY_LOADING
        }
    })

if __name__ == '__main__':
    load_resources()
    print("\n" + "="*70)
    print("Application Ready")
    print("="*70)
    print(f"Caching: {'Enabled' if config.ENABLE_CACHE else 'Disabled'}")
    print(f"Grid Index: {'Enabled' if config.ENABLE_GRID_INDEX else 'Disabled'}")
    print(f"Performance Monitoring: {'Enabled' if config.ENABLE_PROFILING else 'Disabled'}")
    print("="*70 + "\n")
    app.run(debug=True, port=5000)
