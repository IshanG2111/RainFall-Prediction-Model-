import pandas as pd
import numpy as np
import os

def generate_correlated_data():
    print("Generating correlated synthetic data...")
    
    # Load grid structure
    if os.path.exists('data_processed/india_grid.csv'):
        grid_df = pd.read_csv('data_processed/india_grid.csv')
    else:
        # Fallback grid if file missing (shouldn't happen)
        print("Grid file missing, using simple grid.")
        lat = np.arange(8, 38, 0.25)
        lon = np.arange(68, 98, 0.25)
        grid_id = []
        for la in lat:
            for lo in lon:
                grid_id.append(f"{la}_{lo}")
        grid_df = pd.DataFrame({'grid_id': grid_id})

    # Generate data for 365 days to ensure seasonality
    dates = pd.date_range(start='2023-01-01', periods=365)
    
    records = []
    
    # We can't generate for all grids * all days (too big), so we sample
    # Let's generate for 100 random grids for 365 days -> 36,500 rows (similar to current size)
    sample_grids = grid_df['grid_id'].sample(n=min(100, len(grid_df)), random_state=42).tolist()
    
    for date in dates:
        month = date.month
        # Monsoon factor (June-Sept)
        is_monsoon = 6 <= month <= 9
        monsoon_boost = 2.0 if is_monsoon else 0.5
        
        for gid in sample_grids:
            # Random base weather patterns
            # OLR: Low means clouds/rain (150-300)
            # UTH: High means humid/rain (0-100)
            # HEM: Hydro-Estimator (already rainfall proxy)
            
            # 1. Generate OLR (Driver)
            # Monsoon -> Lower OLR
            base_olr = 240 - (30 if is_monsoon else 0)
            olr = np.random.normal(base_olr, 30)
            olr = np.clip(olr, 100, 320)
            
            # 2. UTH correlates negatively with OLR
            uth = 100 - (olr - 100)/2.2 + np.random.normal(0, 5)
            uth = np.clip(uth, 5, 95)
            
            # 3. Cloud Mean correlates with UTH
            cloud_mean = (uth / 100.0) * np.random.uniform(0.8, 1.2)
            cloud_mean = np.clip(cloud_mean, 0, 1)
            
            # 4. HEM correlates with Cloud/OLR
            # If OLR is low, HEM is high
            if olr < 220:
                hem = (220 - olr) * 0.5 * np.random.uniform(0.8, 1.5)
            else:
                hem = 0
            
            # 5. Other params
            lst_max = 45 - (cloud_mean * 15) + np.random.normal(0, 2) # Cooler when cloudy
            lst_mean = lst_max - 10
            wdp_wind = np.random.gamma(5, 2)
            wdp_vorticity = np.random.normal(0, 1e-5)
            wdp_shear = np.random.gamma(10, 1)

            # 6. TARGET: ICM_daily_total (Rainfall mm)
            # Strong correlation with HEM, UTH, Low OLR
            # Rain = HEM + Noise + Boost
            
            rain_prob = 1 / (1 + np.exp(0.05 * (olr - 230))) # Sigmoid based on OLR
            
            if np.random.random() < rain_prob:
                # It rains
                rain_amount = hem * 1.2 + (uth/20) + np.random.exponential(5)
                rain_amount *= monsoon_boost
            else:
                rain_amount = 0.0
                
            records.append({
                'date': date,
                'grid_id': gid,
                'HEM_daily': hem,
                'WDP_wind_mean': wdp_wind,
                'WDP_vorticity': wdp_vorticity,
                'WDP_shear': wdp_shear,
                'UTH_daily': uth,
                'OLR_daily': olr,
                'LST_mean': lst_mean,
                'LST_max': lst_max,
                'CMP_cloud_mean': cloud_mean,
                'IMC_daily_total': max(0, rain_amount),
                'month': month, # Add explicit columns
                'day_of_year': date.dayofyear
            })
            
    df = pd.DataFrame(records)
    
    # Save
    os.makedirs('data_processed', exist_ok=True)
    out_path = 'data_processed/master_dataset.parquet'
    df.to_parquet(out_path)
    print(f"Generated {len(df)} correlated records to {out_path}")
    print(df[['OLR_daily', 'IMC_daily_total']].corr())

if __name__ == "__main__":
    generate_correlated_data()
