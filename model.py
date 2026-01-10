import pandas as pd
import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error, classification_report
from sklearn.inspection import permutation_importance
import pickle
import os
import warnings

import warnings

warnings.filterwarnings('ignore')

class PhysicsConstraints:
    """
    Handles physics-based constraints and sanity checks for the Rainfall Model.
    Ref: Physics-Based Rules for Rainfall Prediction (Indian Context)
    """
    
    @staticmethod
    def apply_hard_clamps(df, is_processed=False):
        """
        Apply hard physical clamps to the dataframe.
        Used for both training (data cleaning) and inference (post-processing).
        
        Args:
            df (pd.DataFrame): Dataframe with features (hem, olr, uth, etc.) and 'rain_mm' (if training/cleaning).
            is_processed (bool): If True, assumes input is processed features ready for inference. 
                                 If False, assumes raw data during cleaning.
        """
        # We need specific columns. If they are missing, we skip those rules or warn.
        # Required: olr, uth, wind_speed, lst_k, cer, cot
        # Optional: rain_mm, date/month (for seasonal rules), lat/lon (for spatial rules)
        
        # Working with a copy to avoid SettingWithCopy warnings on slices if any
        df = df.copy()
        
        # --- 1. Warm Rain Fix (OLR) ---
        # Rule: OLR > 260 => Rain = 0
        mask_warm_rain = df['olr'] > 260
        if 'rain_mm' in df.columns:
            df.loc[mask_warm_rain, 'rain_mm'] = 0
            
        # --- 2. Warm Cloud Moisture Check ---
        # Rule: OLR > 200 AND UTH < 40% => Rain <= 5
        mask_warm_dry = (df['olr'] > 200) & (df['uth'] < 40)
        if 'rain_mm' in df.columns:
            df.loc[mask_warm_dry, 'rain_mm'] = df.loc[mask_warm_dry, 'rain_mm'].clip(upper=5)
            
        # --- 3. Haze Filter (Aerosol) ---
        # Rule: COT < 8 => Rain <= 2
        feature_cot = 'cot' if 'cot' in df.columns else None
        if feature_cot:
            mask_haze = df[feature_cot] < 8
            if 'rain_mm' in df.columns:
                df.loc[mask_haze, 'rain_mm'] = df.loc[mask_haze, 'rain_mm'].clip(upper=2)
                
        return df

    @staticmethod
    def get_regime(row):
        """
        Determine the meteorological regime based on OLR, UTH, etc.
        Returns: Str (Regime Name)
        """
        olr = row.get('olr', 300)
        
        if olr > 260:
            return "Clear/Haze"
        elif 220 <= olr <= 260:
            # Check UTH for Shallow Monsoon vs just Warm
            uth = row.get('uth', 0)
            if uth >= 70: 
                return "Shallow Monsoon"
            return "Warm Cloud"
        elif 140 <= olr < 190:
            return "Deep Convection"
        elif olr < 140:
            return "Cyclone/Storm"
        
        return "Transitional"

    @staticmethod
    def apply_post_inference_adjustments(prediction, features):
        """
        Apply sanity checks and adjustments to a single prediction result.
        
        Args:
            prediction (float): The raw predicted rainfall (mm).
            features (dict): The input features used for prediction. 
                             Must include: lat, lon, month, olr, uth, etc.
        
        Returns:
            float: Adjusted rainfall prediction.
            str: Status/Reason for adjustment (optional)
        """
        final_rain = prediction
        reason = "Model Raw"
        
        lat = features.get('latitude', 0)
        lon = features.get('longitude', 0)
        month = features.get('month', 1) 
        olr = features.get('olr', 250)
        uth = features.get('uth', 50)
        elevation = features.get('elevation', 0) # Assuming we might have this, else 0
        
        # --- Hard Clamps (Redundant safeguard) ---
        if olr > 260:
            return 0.0, "Physical Clamp (OLR > 260)"
            
        if olr > 200 and uth < 40:
            final_rain = min(final_rain, 5.0)
            reason = "Physical Clamp (Warm/Dry)"

        # --- Sanity: Desert Check ---
        # IF Lat > 24°N AND Lon < 73°E (Rajasthan) AND Month != {Jul, Aug}
        is_rajasthan = (lat > 24) and (lon < 73)
        is_monsoon = month in [7, 8]
        if is_rajasthan and not is_monsoon:
            if final_rain > 10:
                final_rain *= 0.1 # Aggressive dampen
                reason = "Desert Sanity Filter"

        # --- Sanity: Winter Dryness ---
        # Month {12, 1} AND Lat > 15°N => Rain <= 20
        if month in [12, 1] and lat > 15:
            if final_rain > 20:
                final_rain = 20.0
                reason = "Winter Dryness Clamp"

        return final_rain, reason

class RainfallPredictor:
    def __init__(self, data_path='data_processed/2_days/finaldata/final_dataset.parquet'):
        """Initialize the rainfall prediction model"""
        self.data_path = data_path
        self.model = None
        self.scaler = StandardScaler()
        # Initial raw features
        self.raw_features = [
             'hem', 'wind_speed', 'uth', 'olr', 'lst_k', 'cer', 'cot'
        ]
        # Features after engineering
        self.feature_columns = [] 
        self.target_column = 'rain_mm'
        self.df = None
        self.metrics = {}

    def load_data(self):
        """Load the dataset"""
        print(f"Loading dataset from {self.data_path}...")
        
        if not os.path.exists(self.data_path):
            csv_path = self.data_path.replace('.parquet', '.csv')
            if os.path.exists(csv_path):
                 self.df = pd.read_csv(csv_path)
            else:
                raise FileNotFoundError(f"Data file not found at {self.data_path}")
        else:
            self.df = pd.read_parquet(self.data_path)
        
        print(f"Initial load: {len(self.df)} records")

    def clean_data(self):
        """Perform data cleaning and outlier clipping based on domain knowledge"""
        print("Cleaning data and clipping outliers...")
        
        # Enforce realistic value ranges by clipping
        ranges = {
            'rain_mm': (0, 300),
            'hem': (0, 300),
            'uth': (0, 100),
            'olr': (100, 300),
            'lst_k': (180, 340),
            'wind_speed': (0, 60),
            'cer': (4, 30),
            'cot': (0, 50)
        }

        for col, (min_val, max_val) in ranges.items():
            if col in self.df.columns:
                self.df[col] = self.df[col].clip(lower=min_val, upper=max_val)

        # Apply Physics-Based Hard Clamps (Training Phase)
        # This removes/fixes physically impossible data points from the training set
        self.df = PhysicsConstraints.apply_hard_clamps(self.df)

        # Drop rows with NaN in critical columns after clipping
        self.df = self.df.dropna(subset=self.raw_features + [self.target_column])
        print(f"Data after cleaning: {len(self.df)} records")

    def feature_engineering(self):
        """Generate lag features and cyclic time features"""
        print("Performing feature engineering...")
        
        # Ensure date column exists and sort by it for lags and splitting
        if 'date' in self.df.columns:
            self.df['date'] = pd.to_datetime(self.df['date'])
            self.df = self.df.sort_values('date').reset_index(drop=True)
        else:
            # If no date, proceed with assumption that data is somewhat ordered or cannot do time-split accurately
            print("WARNING: 'date' column not found. Assuming data is temporally ordered.")

        # --- Cyclic Encoding for Time ---
        # Generate day_of_year and month if not present
        if 'date' in self.df.columns:
            self.df['day_of_year'] = self.df['date'].dt.dayofyear
            self.df['week_of_year'] = self.df['date'].dt.isocalendar().week.astype(int)
        
        # Sin/Cos transforms
        # Day of year (1-366)
        self.df['day_sin'] = np.sin(2 * np.pi * self.df['day_of_year'] / 366)
        self.df['day_cos'] = np.cos(2 * np.pi * self.df['day_of_year'] / 366)
        
        # Week of year (1-53)
        self.df['week_sin'] = np.sin(2 * np.pi * self.df['week_of_year'] / 53)
        self.df['week_cos'] = np.cos(2 * np.pi * self.df['week_of_year'] / 53)


        # --- Lag Features ---
        # CRITICAL UPDATE: The dataset contains non-consecutive dates (monthly/scattered).
        # Calculating 'yesterday's rain' (Lag 1) is impossible. 
        # Previous logic using shift() on Date-sorted data mixed different grids.
        # We will REMOVE lag features as they are not valid for this specific dataset structure.
        # Instead, we rely on the strong satellite (HEM, OLR) and seasonal (Day/Week sin/cos) signals.
        
        # Define final feature set
        self.feature_columns = self.raw_features + [
            'day_sin', 'day_cos', 'week_sin', 'week_cos'
        ]
        
        print(f"Data after feature engineering: {len(self.df)} records")

    def train_evaluate(self):
        """Train model with time-aware split and evaluate"""
        print("\nStarting Model Training & Evaluation...")
        
        # Prepare X and y
        X = self.df[self.feature_columns]
        y = self.df[self.target_column]
        
        # Log-transform target for training (handle zero-inflation/skew)
        y_log = np.log1p(y)

        # Time-aware split (Forward Chaining principle: Train on past, Test on future)
        # Split at 80% mark
        split_idx = int(len(self.df) * 0.8)
        
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train_log, y_test_log = y_log.iloc[:split_idx], y_log.iloc[split_idx:]
        y_test_original = y.iloc[split_idx:] # For final eval
        
        print(f"Training set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples")

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train with HistGradientBoostingRegressor
        # Try different loss functions
        losses = ['squared_error', 'absolute_error', 'poisson'] # 'quantile' requires quantile value
        best_rmse = float('inf')
        best_model = None
        
        print("\nTraining with different loss functions...")
        
        for loss in losses:
            print(f"  > Training with loss='{loss}'...")
            try:
                model = HistGradientBoostingRegressor(
                    loss=loss,
                    max_iter=500,
                    learning_rate=0.05,
                    max_depth=10,
                    early_stopping=True,
                    random_state=42
                )
                model.fit(X_train_scaled, y_train_log)
                
                # Validation check on this fold
                val_pred_log = model.predict(X_test_scaled)
                val_pred = np.expm1(val_pred_log)
                val_pred = np.maximum(0, val_pred)
                rmse = np.sqrt(mean_squared_error(y_test_original, val_pred))
                
                print(f"    RMSE: {rmse:.4f}")
                
                if rmse < best_rmse:
                    best_rmse = rmse
                    best_model = model
                    self.model = model
            except Exception as e:
                print(f"    Failed: {e}")

        # Final Evaluation with Best Model
        print(f"\nBest Model RMSE: {best_rmse:.4f}")
        
        # Predictions
        y_pred_log = self.model.predict(X_test_scaled)
        y_pred = np.expm1(y_pred_log)
        y_pred = np.maximum(0, y_pred)

        # Metrics
        rmse = np.sqrt(mean_squared_error(y_test_original, y_pred))
        mae = mean_absolute_error(y_test_original, y_pred)
        r2 = r2_score(y_test_original, y_pred)

        self.metrics = {
            'RMSE': rmse,
            'MAE': mae,
            'R2': r2,
            'Test_Samples': len(X_test)
        }
        
        print(f"\n{'='*30}")
        print("FINAL EVALUATION METRICS")
        print(f"{'='*30}")
        print(f"RMSE: {rmse:.4f}")
        print(f"MAE:  {mae:.4f}")
        print(f"R²:   {r2:.4f}")
        
        # Rain Occurrence Evaluation
        # Convert to binary classification: Rain (>= 0.1mm) vs No Rain
        y_true_binary = (y_test_original >= 0.1).astype(int)
        y_pred_binary = (y_pred >= 0.1).astype(int)
        
        print(f"\nRain Occurrence Classification Report:")
        print(classification_report(y_true_binary, y_pred_binary, target_names=['No Rain', 'Rain']))

        # Feature Importance
        print("\nCalculating Feature Importance (Permutation)...")
        result = permutation_importance(self.model, X_test_scaled, y_test_log, n_repeats=10, random_state=42, n_jobs=-1)
        sorted_idx = result.importances_mean.argsort()

        print("\nFeature Importance Ranking:")
        for i in sorted_idx[::-1]:
            print(f"{self.feature_columns[i]:<20}: {result.importances_mean[i]:.4f}")

    def save_model(self, filepath='models/model_frame_1.pkl'):
        """Save the trained model and artifacts"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'metrics': self.metrics,
            'target_transform': 'log1p'
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"\nModel saved to {filepath}")

def main():
    predictor = RainfallPredictor()
    predictor.load_data()
    predictor.clean_data()
    predictor.feature_engineering()
    predictor.train_evaluate()
    predictor.save_model()

if __name__ == "__main__":
    main()
