import glob
import h5py
import numpy as np
from datetime import datetime
from multiprocessing import Pool, cpu_count
from scripts.helper.aggregation_helper import (clip_to_india,map_to_grid,aggregate_and_fix_missing,save_daily)

def _wdp_worker(args):
    idx, fp = args

    with h5py.File(fp, "r") as h:
        u = h["UCOMP"][0, 0]
        v = h["VCOMP"][0, 0]
        speed = np.sqrt(u**2 + v**2)

    return idx, speed

def process_wdp_daily(date_str, cfg, grid_df, file_map):
    raw_dir = cfg["raw_base_dir"]
    processed_dir = cfg["processed_base_dir"]

    files = sorted(file_map.get(date_str, []))

    if not files:
        print(f"No WDP files found for {date_str}")
        return None

    # lat/lon once
    with h5py.File(files[0], "r") as h:
        lat_vals = h["latitude"][:]
        lon_vals = h["longitude"][:]
        H, W = len(lat_vals), len(lon_vals)
        lat2d = np.repeat(lat_vals[:, None], W, axis=1)
        lon2d = np.repeat(lon_vals[None, :], H, axis=0)

    indexed_files = list(enumerate(files))

    with Pool(min(8, cpu_count())) as pool:
        results = pool.map(_wdp_worker, indexed_files)

    results.sort(key=lambda x: x[0])

    acc = None
    n = 0

    for _, speed in results:
        acc = speed if acc is None else acc + speed
        n += 1

    daily_speed = acc / max(1, n)

    lat_i, lon_i, val_i = clip_to_india(lat2d, lon2d, daily_speed)
    grid_id = map_to_grid(lat_i, lon_i)

    date = datetime.strptime(date_str, "%d%b%Y").date()
    out = aggregate_and_fix_missing(grid_id, val_i, date, grid_df)
    out = out.rename(columns={"value": "wind_speed"})

    return save_daily(out, "wdp", date, processed_dir)