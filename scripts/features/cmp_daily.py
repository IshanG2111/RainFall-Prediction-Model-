import glob
import h5py
from datetime import datetime
from multiprocessing import Pool, cpu_count
import pandas as pd
from scripts.helper.aggregation_helper import (build_latlon_from_attrs,clip_to_india,map_to_grid,save_daily)

def _cmp_worker(args):
    idx, fp = args

    with h5py.File(fp, "r") as h:
        cer = h["CER"][0].astype(float)
        cer *= h["CER"].attrs.get("scale_factor", [1])[0]

        cot = h["COT"][0].astype(float)
        cot *= h["COT"].attrs.get("scale_factor", [1])[0]

    return idx, cer, cot

def process_cmp_daily(date_str, cfg, grid_df, file_map):
    raw_dir = cfg["raw_base_dir"]
    processed_dir = cfg["processed_base_dir"]

    files = sorted(file_map.get(date_str, []))

    if not files:
        return None

    with h5py.File(files[0], "r") as h:
        H, W = h["CER"][0].shape
        lat2d, lon2d = build_latlon_from_attrs(h, H, W)

    indexed_files = list(enumerate(files))

    with Pool(min(8, cpu_count())) as pool:
        results = pool.map(_cmp_worker, indexed_files)

    results.sort(key=lambda x: x[0])

    acc_cer = None
    acc_cot = None
    n = 0

    for _, cer, cot in results:
        acc_cer = cer if acc_cer is None else acc_cer + cer
        acc_cot = cot if acc_cot is None else acc_cot + cot
        n += 1

    cer_daily = acc_cer / n
    cot_daily = acc_cot / n

    lat_i, lon_i, cer_i = clip_to_india(lat2d, lon2d, cer_daily)
    _, _, cot_i = clip_to_india(lat2d, lon2d, cot_daily)

    grid_id = map_to_grid(lat_i, lon_i)

    df = pd.DataFrame({"grid_id": grid_id, "cer": cer_i, "cot": cot_i})
    out = df.groupby("grid_id").mean().reset_index()

    full = grid_df[["grid_id", "lat_center", "lon_center"]].copy()
    date = datetime.strptime(date_str, "%d%b%Y").date()
    full["date"] = date

    out = full.merge(out, on="grid_id", how="left")

    return save_daily(out, "cmp", date, processed_dir)