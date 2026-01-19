import glob
import h5py
from datetime import datetime
from scripts.helper.aggregation_helper import (build_latlon_from_attrs,clip_to_india,map_to_grid,aggregate_and_fix_missing,save_daily)

def process_imc_daily(date_str, cfg, grid_df):
    raw_dir = cfg["raw_base_dir"]
    processed_dir = cfg["processed_base_dir"]

    pattern = f"{raw_dir}/imc/3RIMG_{date_str}_*_L2B_IMC_*.h5"
    files = sorted(glob.glob(pattern))

    if not files:
        print(f"No IMC files found for {date_str}")
        return None

    rainfall_accum = None
    lat2d = lon2d = None

    for fp in files:
        with h5py.File(fp, "r") as h:
            imc = h["IMC"][0]  # mm/hr
            H, W = imc.shape

            if lat2d is None:
                lat2d, lon2d = build_latlon_from_attrs(h, H, W)

            rain_mm = imc * 0.5  # 30-min rainfall
            rainfall_accum = rain_mm if rainfall_accum is None else rainfall_accum + rain_mm

    lat_i, lon_i, rain_i = clip_to_india(lat2d, lon2d, rainfall_accum)
    grid_id = map_to_grid(lat_i, lon_i)

    date = datetime.strptime(date_str, "%d%b%Y").date()
    out = aggregate_and_fix_missing(grid_id, rain_i, date, grid_df)
    out = out.rename(columns={"value": "rain_mm"})

    return save_daily(out, "imc", date, processed_dir)