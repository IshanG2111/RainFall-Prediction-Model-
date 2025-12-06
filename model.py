import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class RainfallPredictor:
    def __init__(self, data_path='resources/india_2000_2024_daily_weather.csv'):
        """Initialize the rainfall prediction model"""
        self.data_path = data_path
        self.model = None
        self.city_encoder = LabelEncoder()
        self.feature_columns = None
        self.df = None
        
    def load_and_preprocess_data(self):
        """Load and preprocess the dataset"""
        print("Loading dataset...")
        self.df = pd.read_csv(self.data_path)
        
        # Convert date to datetime
        self.df['date'] = pd.to_datetime(self.df['date'])
        
        # Remove any rows with missing values
        initial_rows = len(self.df)
        self.df = self.df.dropna()
        print(f"Removed {initial_rows - len(self.df)} rows with missing values")
        
        # Create target variable: Will it rain tomorrow? (rain_sum > 0)
        self.df = self.df.sort_values(['city', 'date'])
        self.df['rain_tomorrow'] = self.df.groupby('city')['rain_sum'].shift(-1)
        self.df['rain_tomorrow'] = (self.df['rain_tomorrow'] > 0).astype(int)
        
        # Create rain_today feature
        self.df['rain_today'] = (self.df['rain_sum'] > 0).astype(int)
        
        # Remove last row for each city (no tomorrow data)
        self.df = self.df.groupby('city').apply(lambda x: x.iloc[:-1]).reset_index(drop=True)
        
        # Encode city
        self.df['city_encoded'] = self.city_encoder.fit_transform(self.df['city'])
        
        print(f"Dataset loaded: {len(self.df)} records")
        print(f"Cities: {self.df['city'].unique()}")
        print(f"Date range: {self.df['date'].min()} to {self.df['date'].max()}")
        print(f"Rain tomorrow distribution: {self.df['rain_tomorrow'].value_counts().to_dict()}")
        
        return self.df
    
    def prepare_features(self):
        """Prepare feature matrix and target vector"""
        # Select features for training
        self.feature_columns = [
            'city_encoded',
            'temperature_2m_max',
            'temperature_2m_min',
            'apparent_temperature_max',
            'apparent_temperature_min',
            'precipitation_sum',
            'wind_speed_10m_max',
            'wind_gusts_10m_max',
            'rain_today'
        ]
        
        X = self.df[self.feature_columns]
        y = self.df['rain_tomorrow']
        
        return X, y
    
    def train_model(self, test_size=0.2, random_state=42):
        """Train the Random Forest model"""
        print("\nPreparing features...")
        X, y = self.prepare_features()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        print(f"Training set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples")
        
        # Train Random Forest Classifier
        print("\nTraining Random Forest model...")
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=random_state,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n{'='*50}")
        print(f"Model Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        print(f"{'='*50}")
        
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['No Rain', 'Rain']))
        
        print("\nConfusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        print(cm)
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'Feature': self.feature_columns,
            'Importance': self.model.feature_importances_
        }).sort_values('Importance', ascending=False)
        
        print("\nTop Features by Importance:")
        print(feature_importance)
        
        return accuracy
    
    def predict_next_7_days(self, city, start_date=None):
        """
        Predict rainfall for the next 7 days for a given city
        Uses the last known weather data for that city and makes sequential predictions
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train_model() first.")
        
        # Get the most recent data for the city
        city_data = self.df[self.df['city'] == city].sort_values('date')
        
        if len(city_data) == 0:
            raise ValueError(f"City '{city}' not found in dataset")
        
        # Get the last record for this city
        last_record = city_data.iloc[-1].copy()
        
        # If start_date is provided, use it; otherwise use the day after the last record
        if start_date is None:
            current_date = last_record['date'] + timedelta(days=1)
        else:
            current_date = pd.to_datetime(start_date)
        
        predictions = []
        
        # Current weather state (start from last known data)
        current_weather = {
            'temperature_2m_max': last_record['temperature_2m_max'],
            'temperature_2m_min': last_record['temperature_2m_min'],
            'apparent_temperature_max': last_record['apparent_temperature_max'],
            'apparent_temperature_min': last_record['apparent_temperature_min'],
            'precipitation_sum': last_record['precipitation_sum'],
            'wind_speed_10m_max': last_record['wind_speed_10m_max'],
            'wind_gusts_10m_max': last_record['wind_gusts_10m_max'],
            'rain_today': int(last_record['rain_sum'] > 0)
        }
        
        # Encode city
        city_encoded = self.city_encoder.transform([city])[0]
        
        for day in range(7):
            # Prepare features for prediction
            features = np.array([[
                city_encoded,
                current_weather['temperature_2m_max'],
                current_weather['temperature_2m_min'],
                current_weather['apparent_temperature_max'],
                current_weather['apparent_temperature_min'],
                current_weather['precipitation_sum'],
                current_weather['wind_speed_10m_max'],
                current_weather['wind_gusts_10m_max'],
                current_weather['rain_today']
            ]])
            
            # Predict rain tomorrow
            rain_tomorrow_prob = self.model.predict_proba(features)[0]
            rain_tomorrow = self.model.predict(features)[0]
            rain_tomorrow_str = 'Yes' if rain_tomorrow == 1 else 'No'
            
            # Calculate probability percentage
            rain_probability = rain_tomorrow_prob[1] * 100  # Probability of rain
            
            # Determine status based on probability
            if rain_probability < 20:
                status = "No Rain"
            elif rain_probability < 50:
                status = "Light Rain"
            elif rain_probability < 75:
                status = "Moderate Rain"
            else:
                status = "Heavy Rain"
            
            # Store prediction
            predictions.append({
                'Date': current_date.strftime('%a, %b %d'),
                'FullDate': current_date.strftime('%Y-%m-%d'),
                'City': city,
                'Temperature': f"{current_weather['temperature_2m_min']:.1f}°C - {current_weather['temperature_2m_max']:.1f}°C",
                'Humidity': f"N/A",  # Not in this dataset
                'Pressure': f"N/A",  # Not in this dataset
                'WindSpeed': f"{current_weather['wind_speed_10m_max']:.1f} km/h",
                'RainProbability': f"{rain_probability:.0f}",
                'RainTomorrow': rain_tomorrow_str,
                'Status': status
            })
            
            # Update for next iteration with realistic variations
            current_weather['temperature_2m_max'] += np.random.uniform(-2, 2)
            current_weather['temperature_2m_min'] += np.random.uniform(-2, 2)
            current_weather['apparent_temperature_max'] += np.random.uniform(-2, 2)
            current_weather['apparent_temperature_min'] += np.random.uniform(-2, 2)
            current_weather['precipitation_sum'] = max(0, current_weather['precipitation_sum'] + np.random.uniform(-2, 2))
            current_weather['wind_speed_10m_max'] += np.random.uniform(-3, 3)
            current_weather['wind_gusts_10m_max'] += np.random.uniform(-3, 3)
            
            # Keep values in realistic ranges
            current_weather['temperature_2m_max'] = max(10, min(50, current_weather['temperature_2m_max']))
            current_weather['temperature_2m_min'] = max(0, min(40, current_weather['temperature_2m_min']))
            current_weather['apparent_temperature_max'] = max(5, min(55, current_weather['apparent_temperature_max']))
            current_weather['apparent_temperature_min'] = max(-5, min(45, current_weather['apparent_temperature_min']))
            current_weather['wind_speed_10m_max'] = max(0, min(50, current_weather['wind_speed_10m_max']))
            current_weather['wind_gusts_10m_max'] = max(0, min(80, current_weather['wind_gusts_10m_max']))
            
            # Today's rain becomes tomorrow's "rain today"
            current_weather['rain_today'] = rain_tomorrow
            
            # Move to next day
            current_date += timedelta(days=1)
        
        return predictions
    
    def save_model(self, filepath='model/rainfall_model.pkl'):
        """Save the trained model"""
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'city_encoder': self.city_encoder,
            'feature_columns': self.feature_columns
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"\nModel saved to {filepath}")
    
    def load_model(self, filepath='model/rainfall_model.pkl'):
        """Load a trained model"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.city_encoder = model_data['city_encoder']
        self.feature_columns = model_data['feature_columns']
        
        print(f"Model loaded from {filepath}")


def main():
    """Main function to train and test the model"""
    print("="*60)
    print("RAINFALL PREDICTION MODEL - TRAINING")
    print("Using India 2000-2024 Daily Weather Data")
    print("="*60)
    
    # Initialize predictor
    predictor = RainfallPredictor()
    
    # Load and preprocess data
    predictor.load_and_preprocess_data()
    
    # Train model
    accuracy = predictor.train_model()
    
    # Save model
    predictor.save_model()
    
    # Test predictions
    print("\n" + "="*60)
    print("TESTING PREDICTIONS")
    print("="*60)
    
    cities = predictor.df['city'].unique()[:3]  # Test with first 3 cities
    
    for city in cities:
        print(f"\n{city} - Next 7 Days Forecast:")
        print("-" * 60)
        predictions = predictor.predict_next_7_days(city)
        
        for pred in predictions:
            print(f"{pred['Date']}: {pred['Status']} ({pred['RainProbability']}% probability)")
    
    print("\n" + "="*60)
    print("Training Complete!")
    print("="*60)


if __name__ == "__main__":
    main()
