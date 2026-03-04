import glob
import h5py
from datetime import datetime
import pandas as pd
from scripts.helper.aggregation_helper import (build_latlon_from_attrs,clip_to_india,map_to_grid,save_daily)


def process_cmp_daily(date_str, cfg, grid_df):
    raw_dir = cfg["raw_base_dir"]
    processed_dir = cfg["processed_base_dir"]

    pattern = f"{raw_dir}/cmp/*{date_str}*_L2C_CMP_*.h5"
    files = sorted(glob.glob(pattern))

    if not files:
        print(f"No CMP files found for {date_str}")
        return None

    acc_cer = None
    acc_cot = None
    lat2d = lon2d = None
    n = 0

    for fp in files:
        with h5py.File(fp, "r") as h:

            # CER effective radius (µm) with scale factor
            cer = h["CER"][0].astype(float)
            cer *= h["CER"].attrs.get("scale_factor", [1])[0]

            # COT optical thickness with scale factor
            cot = h["COT"][0].astype(float)
            cot *= h["COT"].attrs.get("scale_factor", [1])[0]

            H, W = cer.shape

            # Build lat/lon grid once
            if lat2d is None:
                lat2d, lon2d = build_latlon_from_attrs(h, H, W)

            acc_cer = cer if acc_cer is None else acc_cer + cer
            acc_cot = cot if acc_cot is None else acc_cot + cot
            n += 1

    # Daily mean
    cer_daily = acc_cer / n
    cot_daily = acc_cot / n

    # Clip to India
    lat_i, lon_i, cer_i = clip_to_india(lat2d, lon2d, cer_daily)
    _, _, cot_i = clip_to_india(lat2d, lon2d, cot_daily)
    grid_id = map_to_grid(lat_i, lon_i)

    df = pd.DataFrame({"grid_id": grid_id,"cer": cer_i,"cot": cot_i})

    out = df.groupby("grid_id").mean().reset_index()

    full_grid = grid_df[["grid_id", "lat_center", "lon_center"]].copy()
    date = datetime.strptime(date_str, "%d%b%Y").date()
    full_grid["date"] = date

    out = full_grid.merge(out, on="grid_id", how="left")

    return save_daily(out, "cmp", date, processed_dir)