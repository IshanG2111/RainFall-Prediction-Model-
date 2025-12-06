import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_mock_data(grid_path, start_date, days=2):
    """
    Generates mock data for all products based on the grid.
    """
    print(f"Loading grid from {grid_path}...")
    grid_df = pd.read_csv(grid_path)
    grid_ids = grid_df['grid_id'].values
    
    # Generate dates
    start = datetime.strptime(start_date, "%Y-%m-%d")
    date_list = [(start + timedelta(days=x)).strftime("%Y-%m-%d") for x in range(days)]
    
    # Create a base DataFrame with grid_id and date
    # Cartesian product of grid_ids and dates
    print("Creating base index...")
    base_data = []
    for date in date_list:
        for gid in grid_ids:
            base_data.append({'date': date, 'grid_id': gid})
    
    base_df = pd.DataFrame(base_data)
    n_rows = len(base_df)
    print(f"Total rows to generate: {n_rows}")

    # 1. IMC (Target: Rainfall) - Gamma distribution for rain, many zeros
    print("Generating IMC (Rainfall)...")
    # Simulate 70% no rain, 30% rain
    rain_mask = np.random.rand(n_rows) > 0.7
    rain_amounts = np.random.gamma(shape=2, scale=10, size=n_rows)
    base_df['IMC_daily_total'] = np.where(rain_mask, rain_amounts, 0.0).round(2)

    # 2. HEM (High Energy) - Random
    print("Generating HEM...")
    base_df['HEM_daily'] = np.random.uniform(0, 100, n_rows).round(2)

    # 3. WDP (Wind parameters)
    print("Generating WDP...")
    base_df['WDP_wind_mean'] = np.random.uniform(0, 50, n_rows).round(2)
    base_df['WDP_vorticity'] = np.random.normal(0, 5, n_rows).round(4)
    base_df['WDP_shear'] = np.random.uniform(0, 30, n_rows).round(2)

    # 4. UTH (Humidity)
    print("Generating UTH...")
    base_df['UTH_daily'] = np.random.uniform(20, 100, n_rows).round(1)

    # 5. OLR (Outgoing Longwave Radiation)
    print("Generating OLR...")
    base_df['OLR_daily'] = np.random.uniform(150, 300, n_rows).round(1)

    # 6. LST (Land Surface Temp)
    print("Generating LST...")
    base_df['LST_mean'] = np.random.uniform(15, 45, n_rows).round(1)
    base_df['LST_max'] = base_df['LST_mean'] + np.random.uniform(5, 15, n_rows).round(1)

    # 7. CMP (Cloud Microphysics)
    print("Generating CMP...")
    base_df['CMP_cloud_mean'] = np.random.uniform(0, 1, n_rows).round(3)

    # Save individual files (simulating separate processing pipelines)
    output_dir = "data_processed"
    os.makedirs(output_dir, exist_ok=True)
    
    products = {
        'IMC': ['IMC_daily_total'],
        'HEM': ['HEM_daily'],
        'WDP': ['WDP_wind_mean', 'WDP_vorticity', 'WDP_shear'],
        'UTH': ['UTH_daily'],
        'OLR': ['OLR_daily'],
        'LST': ['LST_mean', 'LST_max'],
        'CMP': ['CMP_cloud_mean']
    }

    for prod_name, cols in products.items():
        prod_df = base_df[['date', 'grid_id'] + cols]
        path = os.path.join(output_dir, f"{prod_name}_mock.csv")
        prod_df.to_csv(path, index=False)
        print(f"Saved {prod_name} to {path}")

if __name__ == "__main__":
    grid_file = "data_processed/india_grid.csv"
    if not os.path.exists(grid_file):
        print("Grid file not found! Run grid_utils.py first.")
    else:
        generate_mock_data(grid_file, "2023-06-01", days=2)
