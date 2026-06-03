import glob
import h5py
import numpy as np
from datetime import datetime
from multiprocessing import Pool, cpu_count
from scripts.helper.aggregation_helper import (build_latlon_from_attrs,clip_to_india,map_to_grid,save_daily)

def _lst_worker(args):
    idx, fp = args

    with h5py.File(fp, "r") as h:
        arr = h["LST"][0].astype(float)
        arr[arr == -999] = np.nan

    return idx, arr

def process_lst_daily(date_str, cfg, grid_df, file_map):
    raw_dir = cfg["raw_base_dir"]
    processed_dir = cfg["processed_base_dir"]

    files = sorted(file_map.get(date_str, []))

    if not files:
        print(f"No LST files found for {date_str}")
        return None

    with h5py.File(files[0], "r") as h:
        H, W = h["LST"][0].shape
        lat2d, lon2d = build_latlon_from_attrs(h, H, W)

    indexed_files = list(enumerate(files))

    with Pool(min(8, cpu_count())) as pool:
        results = pool.map(_lst_worker, indexed_files)

    results.sort(key=lambda x: x[0])

    sum_acc = None
    count_acc = None

    for _, arr in results:
        if np.all(np.isnan(arr)):
            continue

        if sum_acc is None:
            sum_acc = np.zeros_like(arr)
            count_acc = np.zeros_like(arr, dtype=np.int32)

        mask = ~np.isnan(arr)
        sum_acc[mask] += arr[mask]
        count_acc[mask] += 1

    if sum_acc is None:
        return None

    daily_lst = np.full_like(sum_acc, np.nan)
    valid = count_acc > 0
    daily_lst[valid] = sum_acc[valid] / count_acc[valid]

    lat_i, lon_i, lst_i = clip_to_india(lat2d, lon2d, daily_lst)
    grid_id = map_to_grid(lat_i, lon_i)

    import pandas as pd
    df = pd.DataFrame({"grid_id": grid_id, "lst_k": lst_i})
    out = df.groupby("grid_id").mean().reset_index()

    full = grid_df[["grid_id", "lat_center", "lon_center"]].copy()
    date = datetime.strptime(date_str, "%d%b%Y").date()
    full["date"] = date

    out = full.merge(out, on="grid_id", how="left")

    return save_daily(out, "lst", date, processed_dir)