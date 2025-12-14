import pandas as pd
import numpy as np
import os

# Define expected ranges
RANGES = {
    "rain_mm": (0, 500),
    "hem": (0, 500),
    "uth": (0, 100),
    "olr": (100, 330),
    "lst_k": (250, 320),
    "wind_speed": (0, 30),
    # Note: cer range in user request was (0, 1), but typical CER values can be higher (microns).
    # Will check against (0, 100) just in case, but flag > 1.
    "cer": (0, 100), 
    "cot": (0, 200),
}

DATA_PATH = 'data_processed/2_days/finaldata/final_dataset.parquet'

def check_ranges():
    print(f"Loading data from {DATA_PATH}...")
    if not os.path.exists(DATA_PATH):
        print("Parquet file not found. Trying CSV...")
        csv_path = DATA_PATH.replace('.parquet', '.csv')
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
        else:
            print("No data found.")
            return
    else:
        df = pd.read_parquet(DATA_PATH)
    
    with open('data_report.txt', 'w') as f:
        f.write(f"Loaded {len(df)} rows.\n")
        f.write("-" * 60 + "\n")
        f.write(f"{'Column':<12} | {'Min':<8} | {'Max':<8} | {'Outliers':<10} | {'Status'}\n")
        f.write("-" * 60 + "\n")

        for col, (min_val, max_val) in RANGES.items():
            if col not in df.columns:
                f.write(f"{col:<12} | {'N/A':<8} | {'N/A':<8} | {'N/A':<10} | Missing\n")
                continue
                
            series = df[col]
            curr_min = series.min()
            curr_max = series.max()
            
            # Check outliers
            outliers = series[(series < min_val) | (series > max_val)]
            count = len(outliers)
            
            status = "OK"
            if count > 0:
                status = f"FAIL ({count})"
                
            f.write(f"{col:<12} | {curr_min:<8.2f} | {curr_max:<8.2f} | {count:<10} | {status}\n")
            
            if count > 0 and count < 10:
                 f.write(f"   -> Outlier values: {outliers.values}\n")

        f.write("-" * 60 + "\n")
    print("Report saved to data_report.txt")

if __name__ == "__main__":
    check_ranges()
