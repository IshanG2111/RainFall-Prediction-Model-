import glob
import h5py
import numpy as np
from datetime import datetime
from scripts.helper.aggregation_helper import (clip_to_india,map_to_grid,aggregate_and_fix_missing,save_daily)

def process_wdp_daily(date_str, cfg, grid_df):
    raw_dir = cfg["raw_base_dir"]
    processed_dir = cfg["processed_base_dir"]

    pattern = f"{raw_dir}/wdp/*{date_str}*_L2G_WDP_*.h5"
    files = sorted(glob.glob(pattern))

    if not files:
        print(f"No WDP files found for {date_str}")
        return None

    acc_speed = None
    lat2d = lon2d = None
    n = 0

    for fp in files:
        with h5py.File(fp, "r") as h:

            # Use only FIRST pressure level
            u = h["UCOMP"][0, 0]
            v = h["VCOMP"][0, 0]

            speed = np.sqrt(u ** 2 + v ** 2)
            H, W = speed.shape

            # Build lat/lon grid once (WDP uses datasets, not attrs)
            if lat2d is None:
                lat_vals = h["latitude"][:]
                lon_vals = h["longitude"][:]
                lat2d = np.repeat(lat_vals[:, None], W, axis=1)
                lon2d = np.repeat(lon_vals[None, :], H, axis=0)

            acc_speed = speed if acc_speed is None else acc_speed + speed
            n += 1

    # Daily mean wind speed
    daily_speed = acc_speed / max(1, n)

    lat_i, lon_i, val_i = clip_to_india(lat2d, lon2d, daily_speed)
    grid_id = map_to_grid(lat_i, lon_i)

    date = datetime.strptime(date_str, "%d%b%Y").date()
    out = aggregate_and_fix_missing(grid_id, val_i, date, grid_df)
    out = out.rename(columns={"value": "wind_speed"})

    return save_daily(out, "wdp", date, processed_dir)