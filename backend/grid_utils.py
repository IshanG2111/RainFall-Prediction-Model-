import numpy as np
import pandas as pd
import os

def generate_india_grid(lat_min=6.0, lat_max=38.0, lon_min=68.0, lon_max=98.0, step=0.25):
    """
    Generates a grid of 0.25x0.25 degree cells covering the specified region (India).
    """
    lats = np.arange(lat_min, lat_max + step, step)
    lons = np.arange(lon_min, lon_max + step, step)
    
    grid_cells = []
    grid_id_counter = 0
    
    for lat in lats:
        for lon in lons:
            # Simple bounding box check could be added here if we had a shapefile for India
            # For now, we take the rectangular bounding box
            cell = {
                'grid_id': grid_id_counter,
                'lat_center': round(lat + step/2, 4),
                'lon_center': round(lon + step/2, 4),
                'lat_min': round(lat, 4),
                'lat_max': round(lat + step, 4),
                'lon_min': round(lon, 4),
                'lon_max': round(lon + step, 4)
            }
            grid_cells.append(cell)
            grid_id_counter += 1
            
    return pd.DataFrame(grid_cells)

if __name__ == "__main__":
    output_dir = "data_processed"
    os.makedirs(output_dir, exist_ok=True)
    
    print("Generating grid for India region...")
    grid_df = generate_india_grid()
    print(f"Generated {len(grid_df)} grid cells.")
    
    output_path = os.path.join(output_dir, "india_grid.csv")
    grid_df.to_csv(output_path, index=False)
    print(f"Grid saved to {output_path}")
