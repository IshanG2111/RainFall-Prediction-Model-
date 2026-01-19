import numpy as np
import pandas as pd
import os

LAT_MIN, LAT_MAX = 6.0, 38.0
LON_MIN, LON_MAX = 68.0, 98.0
GRID_STEP = 0.25

NUM_ROWS = int((LAT_MAX - LAT_MIN) / GRID_STEP)   # 128
NUM_COLS = int((LON_MAX - LON_MIN) / GRID_STEP)   # 120

def build_latlon_from_attrs(h, H, W):
    upper_lat = h.attrs["upper_latitude"][0]
    lower_lat = h.attrs["lower_latitude"][0]
    left_lon = h.attrs["left_longitude"][0]
    right_lon = h.attrs["right_longitude"][0]

    lat_vals = np.linspace(upper_lat, lower_lat, H)
    lon_vals = np.linspace(left_lon, right_lon, W)

    lat2d = np.repeat(lat_vals[:, None], W, axis=1)
    lon2d = np.repeat(lon_vals[None, :], H, axis=0)

    return lat2d, lon2d


def clip_to_india(lat2d, lon2d, data):
    mask = ((lat2d >= LAT_MIN) & (lat2d <= LAT_MAX) & (lon2d >= LON_MIN) & (lon2d <= LON_MAX))
    return lat2d[mask], lon2d[mask], data[mask]


def map_to_grid(lat_i, lon_i):
    row = np.clip(((lat_i - LAT_MIN) / GRID_STEP).astype(int), 0, NUM_ROWS - 1)
    col = np.clip(((lon_i - LON_MIN) / GRID_STEP).astype(int), 0, NUM_COLS - 1)
    return row * NUM_COLS + col + 1

def aggregate_and_fix_missing(grid_id, values, date, grid_df):
    df = pd.DataFrame({"grid_id": grid_id,"value": values})

    out = df.groupby("grid_id")["value"].mean().reset_index()

    full_grid = grid_df[["grid_id", "lat_center", "lon_center"]].copy()
    full_grid["date"] = date

    out = full_grid.merge(out, on="grid_id", how="left")
    return out

def save_daily(out_df, prefix, date, processed_base_dir):
    save_dir = os.path.join(processed_base_dir, f"{prefix}_daily")
    os.makedirs(save_dir, exist_ok=True)

    outpath = os.path.join(save_dir, f"{prefix}_{date}.parquet")
    out_df.to_parquet(outpath, index=False)

    print(f"Saved {prefix.upper()} → {outpath}")
    return out_df