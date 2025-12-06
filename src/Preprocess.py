import pandas as pd
import numpy as np

def preprocess(input_path, output_path):
    df = pd.read_csv(input_path)

    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    df['day_of_year'] = df['date'].dt.dayofyear
    df['day_sin'] = np.sin(2*np.pi*df['day_of_year']/365)
    df['day_cos'] = np.cos(2*np.pi*df['day_of_year']/365)

    for lag in range(1, 8):
        df[f'rain_mm_lag{lag}'] = df['rain_mm'].shift(lag)

    df['rain_mm_roll7'] = df['rain_mm'].shift().rolling(7).mean()

    df = df.dropna()

    df.to_csv(output_path, index=False)
    print("Processed file saved to:", output_path)


if __name__ == "__main__":
    preprocess("data/raw/weather_data.csv", 
            "data/processed/processed_data.csv")
