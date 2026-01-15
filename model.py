import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import pickle
import os
import warnings
from performance_utils import (
    timed, optimize_dataframe_dtypes, sample_large_dataset,
    perf_monitor, chunked_dataframe_reader
)
import performance_config as config

warnings.filterwarnings('ignore')

class RainfallPredictor:
    def __init__(self, data_path='data_processed/2_days/finaldata/final_dataset.parquet'):
        """Initialize the rainfall prediction model"""
        self.data_path = data_path
        self.model = None
        self.scaler = StandardScaler()
        # Updated features based on new dataset
        self.feature_columns = [
            'hem', 'wind_speed', 'uth', 'olr', 'lst_k', 'cer', 'cot',
            'month', 'day_of_year'
        ]
        self.target_column = 'rain_mm'
        self.df = None
        self.metrics = {}

    @timed("load_and_preprocess_data")
    def load_and_preprocess_data(self):
        """Load and preprocess the dataset"""
        print(f"Loading dataset from {self.data_path}...")
        
        if not os.path.exists(self.data_path):
            csv_path = self.data_path.replace('.parquet', '.csv')
            if os.path.exists(csv_path):
                 self.df = pd.read_csv(csv_path)
            else:
                raise FileNotFoundError(f"Data file not found at {self.data_path}")
        else:
            self.df = pd.read_parquet(self.data_path)

        # Optimize data types for memory efficiency
        self.df = optimize_dataframe_dtypes(self.df)

        # Handle missing values
        initial_rows = len(self.df)
        self.df = self.df.dropna(subset=self.feature_columns + [self.target_column])
        print(f"Removed {initial_rows - len(self.df)} rows with missing values")
        
        # Ensure month/day_of_year exist (if not in parquet, derive from date)
        if 'month' not in self.df.columns or 'day_of_year' not in self.df.columns:
            if 'date' in self.df.columns:
                self.df['date'] = pd.to_datetime(self.df['date'])
                self.df['month'] = self.df['date'].dt.month
                self.df['day_of_year'] = self.df['date'].dt.dayofyear
        
        print(f"Dataset loaded: {len(self.df)} records")
        print(f"Memory usage: {self.df.memory_usage(deep=True).sum() / (1024**2):.2f} MB")
        return self.df

    def prepare_features(self):
        """Prepare feature matrix and target vector"""
        X = self.df[self.feature_columns]
        y = self.df[self.target_column]
        
        # Log transform target to handle skewness (zero-inflated data)
        # We use log1p (log(1+x)) to handle zeros
        y_transformed = np.log1p(y)
        
        return X, y, y_transformed

    @timed("train_model")
    def train_model(self, test_size=0.2, random_state=42):
        """Train the HistGradientBoostingRegressor"""
        print("\nPreparing features...")
        X, y_original, y_transformed = self.prepare_features()

        # Split data
        X_train, X_test, y_train_log, y_test_log = train_test_split(
            X, y_transformed, test_size=test_size, random_state=random_state
        )
        
        # Keep original scale y_test for final evaluation
        _, _, _, y_test_original = train_test_split(
            X, y_original, test_size=test_size, random_state=random_state
        )

        print(f"Training set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples")

        # Scale features
        print("Scaling features...")
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train HistGradientBoostingRegressor (Better for large datasets than Random Forest)
        print("\nTraining HistGradientBoostingRegressor...")
        
        # Optimize model parameters for performance
        model_params = {
            'max_iter': 500,
            'learning_rate': 0.05,
            'max_depth': 10,
            'random_state': random_state,
            'early_stopping': True,
            'validation_fraction': 0.1,
            'n_iter_no_change': 10
        }
        
        if config.ENABLE_MODEL_OPTIMIZATION:
            # Additional optimizations for large datasets
            model_params['max_leaf_nodes'] = 31  # Limit tree complexity
            print("Model optimization enabled")
        
        self.model = HistGradientBoostingRegressor(**model_params)

        self.model.fit(X_train_scaled, y_train_log)

        # Evaluate model
        print("\nEvaluating model...")
        
        # Predict log values
        y_pred_log = self.model.predict(X_test_scaled)
        
        # Inverse transform predictions to original scale (exp(x) - 1)
        y_pred_original = np.expm1(y_pred_log)
        y_pred_original = np.maximum(0, y_pred_original) # Ensure no negatives

        rmse = np.sqrt(mean_squared_error(y_test_original, y_pred_original))
        r2 = r2_score(y_test_original, y_pred_original)
        mae = mean_absolute_error(y_test_original, y_pred_original)
        
        self.metrics = {
            'RMSE': round(rmse, 4),
            'R2': round(r2, 4),
            'MAE': round(mae, 4),
            'Test_Samples': len(X_test),
            'Training_Samples': len(X_train)
        }

        print(f"\n{'='*50}")
        print(f"Model Evaluation Metrics (Original Scale):")
        print(f"Root Mean Squared Error (RMSE): {rmse:.4f}")
        print(f"Mean Absolute Error (MAE): {mae:.4f}")
        print(f"R2 Score: {r2:.4f}")
        print(f"{'='*50}")

        return self.metrics

    def save_model(self, filepath='models/model_frame_1.pkl'):
        """Save the trained model, metrics, and scaler"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'metrics': self.metrics,
            'target_transform': 'log1p' # Metadata to know we used log transform
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"\nModel and metrics saved to {filepath}")

def main():
    print("="*60)
    print("RAINFALL PREDICTION MODEL - PHASE 1 RE-TRAINING (IMPROVED)")
    print("Using HistGradientBoosting + Log Transform")
    print("="*60)

    try:
        predictor = RainfallPredictor()
        predictor.load_and_preprocess_data()
        predictor.train_model()
        predictor.save_model()
        
        # Print performance summary
        print("\n" + "="*60)
        print("Training Complete!")
        print("="*60)
        
        if config.ENABLE_PROFILING:
            perf_monitor.print_summary()
            
    except Exception as e:
        print(f"\nError during training: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
