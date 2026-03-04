import glob
import h5py
import numpy as np
from datetime import datetime
import pandas as pd
from scripts.helper.aggregation_helper import (build_latlon_from_attrs,clip_to_india,map_to_grid,save_daily)

def aggregate_lst(grid_id, values, date, grid_df):
    df = pd.DataFrame({"grid_id": grid_id,"lst_k": values})

    out = df.groupby("grid_id")["lst_k"].mean().reset_index()

    full_grid = grid_df[["grid_id", "lat_center", "lon_center"]].copy()
    full_grid["date"] = date

    out = full_grid.merge(out, on="grid_id", how="left")
    return out


def process_lst_daily(date_str, cfg, grid_df):
    raw_dir = cfg["raw_base_dir"]
    processed_dir = cfg["processed_base_dir"]

    pattern = f"{raw_dir}/lst/*{date_str}*_L2B_LST_*.h5"
    files = sorted(glob.glob(pattern))

    if not files:
        print(f"No LST files found for {date_str}")
        return None

    sum_acc = None
    count_acc = None
    lat2d = lon2d = None

    for fp in files:
        with h5py.File(fp, "r") as h:

            arr = h["LST"][0].astype(float)

            # Replace fill values with NaN
            arr[arr == -999] = np.nan

            # Skip completely invalid frames
            if np.all(np.isnan(arr)):
                continue

            H, W = arr.shape

            # Build lat/lon grid once
            if lat2d is None:
                lat2d, lon2d = build_latlon_from_attrs(h, H, W)

            # Initialize accumulators
            if sum_acc is None:
                sum_acc = np.zeros_like(arr, dtype=float)
                count_acc = np.zeros_like(arr, dtype=np.int32)

            valid_mask = ~np.isnan(arr)
            sum_acc[valid_mask] += arr[valid_mask]
            count_acc[valid_mask] += 1

    if sum_acc is None:
        print(f"No valid LST data found for {date_str}")
        return None

    # Pixel-wise daily mean
    daily_lst = np.full_like(sum_acc, np.nan, dtype=float)
    valid_pixels = count_acc > 0
    daily_lst[valid_pixels] = sum_acc[valid_pixels] / count_acc[valid_pixels]

    # Clip to India
    lat_i, lon_i, lst_i = clip_to_india(lat2d, lon2d, daily_lst)
    grid_id = map_to_grid(lat_i, lon_i)

    date = datetime.strptime(date_str, "%d%b%Y").date()
    out = aggregate_lst(grid_id, lst_i, date, grid_df)

    return save_daily(out, "lst", date, processed_dir)