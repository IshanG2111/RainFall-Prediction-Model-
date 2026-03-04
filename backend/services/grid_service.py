import numpy as np
from backend.core.dependencies import get_grid_df

def get_nearest_grid(lat: float, lon: float) -> dict:
    grid_df = get_grid_df()

    if grid_df is None or grid_df.empty:
        raise ValueError("Grid data not loaded.")

    # Cleaner vector distance
    distances = np.hypot(
        grid_df["lat_center"] - lat,
        grid_df["lon_center"] - lon
    )

    nearest_idx = distances.idxmin()
    row = grid_df.loc[nearest_idx]

    return {
        "grid_id": int(row["grid_id"]),
        "center_lat": float(row["lat_center"]),
        "center_lon": float(row["lon_center"]),
    }