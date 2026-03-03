import glob
import h5py
from datetime import datetime
from scripts.helper.aggregation_helper import (build_latlon_from_attrs,clip_to_india,map_to_grid,aggregate_and_fix_missing,save_daily)


def process_hem_daily(date_str, cfg, grid_df):
    raw_dir = cfg["raw_base_dir"]
    processed_dir = cfg["processed_base_dir"]

    pattern = f"{raw_dir}/hem/3RIMG_{date_str}_*_L3B_HEM_DLY_*.h5"
    files = sorted(glob.glob(pattern))

    if not files:
        print(f"No HEM files found for {date_str}")
        return None

    # HEM is already daily → take the first file
    with h5py.File(files[0], "r") as h:
        hem = h["HEM_DLY"][0]
        H, W = hem.shape
        lat2d, lon2d = build_latlon_from_attrs(h, H, W)

    lat_i, lon_i, val_i = clip_to_india(lat2d, lon2d, hem)
    grid_id = map_to_grid(lat_i, lon_i)

    date = datetime.strptime(date_str, "%d%b%Y").date()
    out = aggregate_and_fix_missing(grid_id, val_i, date, grid_df)
    out = out.rename(columns={"value": "hem"})

    return save_daily(out, "hem", date, processed_dir)