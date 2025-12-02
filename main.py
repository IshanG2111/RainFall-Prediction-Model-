import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import datetime

def load_data(filepath):
    """Loads rainfall data from a CSV file."""
    try:
        df = pd.read_csv(filepath)
        return df
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None

def preprocess_data(df):
    """Preprocesses the data for training."""
    # Convert Date to ordinal to use it as a feature if needed, 
    # but for simple prediction based on weather metrics, we might just use Temp, Humidity, Pressure.
    # Let's use Temperature, Humidity, and Pressure to predict Rainfall.
    
    # Check for missing values
    df = df.dropna()
    
    X = df[['Temperature', 'Humidity', 'Pressure']]
    y = df['Rainfall']
    
    return X, y

def train_model(X, y):
    """Trains a Linear Regression model."""
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"Model Training Completed. Mean Squared Error: {mse:.2f}")
    
    return model

def predict_next_7_days(model, last_known_weather):
    """
    Predicts rainfall for the next 7 days.
    Since we don't have a weather forecast API, we will simulate future weather 
    by slightly varying the last known weather conditions.
    """
    print("\n--- Rainfall Prediction for Next 7 Days ---")
    
    current_weather = list(last_known_weather) # [Temp, Humidity, Pressure]
    
    predictions = []
    
    for i in range(1, 8):
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
            "Day": i,
            "Temperature": f"{current_weather[0]:.1f}C",
            "Humidity": f"{current_weather[1]:.1f}%",
            "Pressure": f"{current_weather[2]:.1f}hPa",
            "Predicted Rainfall": f"{predicted_rainfall:.2f}mm",
            "Status": status
        })
        
        print(f"Day {i}: {status} ({predicted_rainfall:.2f}mm) | Temp: {current_weather[0]:.1f}C, Hum: {current_weather[1]:.1f}%, Press: {current_weather[2]:.1f}hPa")

    return predictions

if __name__ == "__main__":
    data_file = "rainfall_data.csv"
    df = load_data(data_file)
    
    if df is not None:
        X, y = preprocess_data(df)
        model = train_model(X, y)
        
        # Get the last row of data to base our future "forecast" on
        last_row = df.iloc[-1]
        last_known_weather = [last_row['Temperature'], last_row['Humidity'], last_row['Pressure']]
        
        predict_next_7_days(model, last_known_weather)
