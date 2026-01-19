import numpy as np
import pandas as pd
import os

def generate_grid(lat_start=6.0, lat_end=38.0, lon_start=68.0, lon_end=98.0, step=0.25):

    lat_edges = np.arange(lat_start, lat_end + step, step)
    lon_edges = np.arange(lon_start, lon_end + step, step)

    grid_cells = []
    grid_id = 1

    for i in range(len(lat_edges) - 1):
        for j in range(len(lon_edges) - 1):

            lat_min = lat_edges[i]
            lat_max = lat_edges[i + 1]
            lon_min = lon_edges[j]
            lon_max = lon_edges[j + 1]

            grid_cells.append([grid_id,lat_min, lat_max,lon_min, lon_max,(lat_min + lat_max) / 2,(lon_min + lon_max) / 2,])

            grid_id += 1

    df = pd.DataFrame(grid_cells, columns=["grid_id", "lat_min", "lat_max", "lon_min", "lon_max", "lat_center", "lon_center"])

    out_dir = "../../grid"
    os.makedirs(out_dir, exist_ok=True)
    out_path = f"{out_dir}/grid_definition.parquet"

    df.to_parquet(out_path)
    print(f"Grid generated with {len(df)} cells --> {out_path}")

if __name__ == "__main__":
    generate_grid()