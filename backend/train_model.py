import pandas as pd
import numpy as np
import os
import pickle
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def train_frame_1_model(data_path="data_processed/master_dataset.parquet"):
    """
    Trains Frame 1 model (Simple Linear Regression) on the merged dataset.
    """
    print(f"Loading data from {data_path}...")
    if not os.path.exists(data_path):
        print("Data file not found.")
        return

    df = pd.read_parquet(data_path)
    
    # Define features and target
    features = ['HEM_daily', 'WDP_wind_mean', 'WDP_vorticity', 'WDP_shear', 
                'UTH_daily', 'OLR_daily', 'LST_mean', 'LST_max', 'CMP_cloud_mean']
    target = 'IMC_daily_total'
    
    X = df[features]
    y = df[target]
    
    # Split data
    print("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    print("Training Linear Regression model...")
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    print(f"Model Performance:")
    print(f"MAE: {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R2 Score: {r2:.4f}")
    
    # Save model
    output_dir = "models"
    os.makedirs(output_dir, exist_ok=True)
    model_path = os.path.join(output_dir, "model_frame_1.pkl")
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_frame_1_model()
