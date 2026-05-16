import glob
import h5py
from datetime import datetime
from multiprocessing import Pool, cpu_count
from scripts.helper.aggregation_helper import (build_latlon_from_attrs,clip_to_india,map_to_grid,aggregate_and_fix_missing,save_daily)

def _imc_worker(args):
    idx, fp = args

    with h5py.File(fp, "r") as h:
        imc = h["IMC"][0]
        rain_mm = imc * 0.5

    return idx, rain_mm

def process_imc_daily(date_str, cfg, grid_df, file_map):
    raw_dir = cfg["raw_base_dir"]
    processed_dir = cfg["processed_base_dir"]

    files = sorted(file_map.get(date_str, []))

    if not files:
        print(f"No IMC files found for {date_str}")
        return None

    with h5py.File(files[0], "r") as h:
        H, W = h["IMC"][0].shape
        lat2d, lon2d = build_latlon_from_attrs(h, H, W)

    indexed_files = list(enumerate(files))

    with Pool(processes=min(8, cpu_count())) as pool:
        results = pool.map(_imc_worker, indexed_files)

    results.sort(key=lambda x: x[0])

    rainfall_accum = None

    for _, rain_mm in results:
        if rainfall_accum is None:
            rainfall_accum = rain_mm
        else:
            rainfall_accum += rain_mm

    lat_i, lon_i, rain_i = clip_to_india(lat2d, lon2d, rainfall_accum)
    grid_id = map_to_grid(lat_i, lon_i)

    date = datetime.strptime(date_str, "%d%b%Y").date()

    out = aggregate_and_fix_missing(grid_id, rain_i, date, grid_df)
    out = out.rename(columns={"value": "rain_mm"})

    return save_daily(out, "imc", date, processed_dir)