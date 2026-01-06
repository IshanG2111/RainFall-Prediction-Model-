import glob
import h5py
import numpy as np
import pandas as pd
from datetime import datetime
import os

grid = pd.read_parquet("../../data_processed/grid/grid_definition.parquet")

LAT_MIN, LAT_MAX = 6.0, 38.0
LON_MIN, LON_MAX = 68.0, 98.0
GRID_STEP = 0.25

NUM_ROWS = int((LAT_MAX - LAT_MIN) / GRID_STEP)      # 128
NUM_COLS = int((LON_MAX - LON_MIN) / GRID_STEP)      # 120

# HELPER FUNCTIONS — USED BY ALL PRODUCTS
def build_latlon_from_attrs(h, H, W):
    """Reconstruct correct INSAT geolocation grid."""
    upper_lat = h.attrs["upper_latitude"][0]
    lower_lat = h.attrs["lower_latitude"][0]
    left_lon  = h.attrs["left_longitude"][0]
    right_lon = h.attrs["right_longitude"][0]

    # INSAT orientation:
    # Row 0 = upper_lat (north)
    # Row H = lower_lat (south)
    lat_vals = np.linspace(upper_lat, lower_lat, H)
    lon_vals = np.linspace(left_lon, right_lon, W)

    lat2d = np.repeat(lat_vals[:, None], W, axis=1)
    lon2d = np.repeat(lon_vals[None, :], H, axis=0)

    return lat2d, lon2d

def clip_to_india(lat2d, lon2d, data):
    """Return flattened arrays clipped to India bounding box."""
    mask = ((lat2d >= LAT_MIN) & (lat2d <= LAT_MAX) & (lon2d >= LON_MIN) & (lon2d <= LON_MAX))
    return lat2d[mask], lon2d[mask], data[mask]


def map_to_grid(lat_i, lon_i):
    """Convert clipped lat/lon → grid_id."""
    row = np.clip(((lat_i - LAT_MIN) / GRID_STEP).astype(int), 0, NUM_ROWS - 1)
    col = np.clip(((lon_i - LON_MIN) / GRID_STEP).astype(int), 0, NUM_COLS - 1)
    return row * NUM_COLS + col + 1


def aggregate_and_fix_missing(grid_id, values, date):
    """Aggregate by grid_id and pad missing grid rows."""
    df = pd.DataFrame({"grid_id": grid_id, "value": values})
    out = df.groupby("grid_id")["value"].mean().reset_index()

    # Insert missing grid rows
    full_grid = grid[["grid_id", "lat_center", "lon_center"]].copy()
    full_grid["date"] = date

    out = full_grid.merge(out, on="grid_id", how="left")
    out["value"] = out["value"]

    return out


def save_daily(out_df, prefix, date):
    """Save to parquet with consistent folder structure."""
    save_dir = f"../../data_processed/8_days/{prefix}_daily"
    os.makedirs(save_dir, exist_ok=True)

    outpath = f"{save_dir}/{prefix}_{date}.parquet"
    out_df.to_parquet(outpath, index=False)
    print(f"Saved {prefix} → {outpath}")

    return out_df

# 3.1 — IMC (Rainfall)
def process_imc_daily(date_str):

    pattern = f"../../data_raw/8_days/imc/3RIMG_{date_str}_*_L2B_IMC_*.h5"
    files = sorted(glob.glob(pattern))

    if len(files) == 0:
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

            rain_mm = imc * 0.5   # convert rate → 30-min rainfall

            rainfall_accum = rain_mm if rainfall_accum is None else rainfall_accum + rain_mm

    lat_i, lon_i, rain_i = clip_to_india(lat2d, lon2d, rainfall_accum)
    grid_id = map_to_grid(lat_i, lon_i)

    out = aggregate_and_fix_missing(grid_id, rain_i, datetime.strptime(date_str, "%d%b%Y").date())
    out = out.rename(columns={"value": "rain_mm"})

    return save_daily(out, "imc", out["date"].iloc[0])

# 3.2 — WDP (Wind → Wind Speed)
def process_wdp_daily(date_str):
    pattern = f"../../data_raw/8_days/wdp/*{date_str}*_L2G_WDP_*.h5"
    files = sorted(glob.glob(pattern))

    if not files:
        print(f"No WDP files for {date_str}")
        return None

    acc_speed = None
    lat2d = lon2d = None
    n = 0

    for fp in files:
        with h5py.File(fp, "r") as h:

            # Use only the FIRST pressure level (index 0)
            u = h["UCOMP"][0, 0]    # shape (201, 201)
            v = h["VCOMP"][0, 0]

            speed = np.sqrt(u**2 + v**2)
            H, W = speed.shape

            # Build lat/lon from datasets (not attributes!)
            if lat2d is None:
                lat_vals = h["latitude"][:]     # 201
                lon_vals = h["longitude"][:]    # 201
                lat2d = np.repeat(lat_vals[:, None], W, axis=1)
                lon2d = np.repeat(lon_vals[None, :], H, axis=0)

            acc_speed = speed if acc_speed is None else acc_speed + speed
            n += 1

    daily_speed = acc_speed / max(1, n)
    lat_i, lon_i, val_i = clip_to_india(lat2d, lon2d, daily_speed)
    grid_id = map_to_grid(lat_i, lon_i)

    out = aggregate_and_fix_missing(grid_id, val_i, datetime.strptime(date_str, "%d%b%Y").date())
    out = out.rename(columns={"value": "wind_speed"})

    return save_daily(out, "wdp", out["date"].iloc[0])

# 3.3 — LST (Kelvin)
def aggregate_lst(grid_id, values, date):
    df = pd.DataFrame({"grid_id": grid_id, "lst_k": values})
    out = df.groupby("grid_id")["lst_k"].mean().reset_index()

    # Insert missing grid rows (keep NaN)
    full_grid = grid[["grid_id", "lat_center", "lon_center"]].copy()
    full_grid["date"] = date

    out = full_grid.merge(out, on="grid_id", how="left")
    return out

def process_lst_daily(date_str):

    pattern = f"../../data_raw/8_days/lst/*{date_str}*_L2B_LST_*.h5"
    files = sorted(glob.glob(pattern))

    if not files:
        print(f"No LST files for {date_str}")
        return None

    sum_acc = None
    count_acc = None
    lat2d = lon2d = None

    for fp in files:
        with h5py.File(fp, "r") as h:

            # Read raw LST
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

            # Valid mask
            valid_mask = ~np.isnan(arr)

            # Accumulate
            sum_acc[valid_mask] += arr[valid_mask]
            count_acc[valid_mask] += 1

    # If nothing valid found
    if sum_acc is None:
        print(f"No valid LST for {date_str}")
        return None

    # Compute daily mean (pixel-wise)
    daily_lst = np.full_like(sum_acc, np.nan, dtype=float)
    valid_pixels = count_acc > 0
    daily_lst[valid_pixels] = sum_acc[valid_pixels] / count_acc[valid_pixels]

    # Clip to India
    lat_i, lon_i, lst_i = clip_to_india(lat2d, lon2d, daily_lst)
    grid_id = map_to_grid(lat_i, lon_i)

    # Aggregate to grid (do NOT fill NaN)
    date = datetime.strptime(date_str, "%d%b%Y").date()
    out = aggregate_lst(grid_id, lst_i, date)

    return save_daily(out, "lst", date)

# 3.4 — CMP (CER + COT)
def process_cmp_daily(date_str):

    pattern = f"../../data_raw/8_days/cmp/*{date_str}*_L2C_CMP_*.h5"
    files = sorted(glob.glob(pattern))

    if not files:
        print(f"No CMP files for {date_str}")
        return None

    acc_cer = None
    acc_cot = None
    lat2d = lon2d = None
    n = 0

    for fp in files:
        with h5py.File(fp, "r") as h:

            # CER effective radius (µm) with scale_factor
            cer = h["CER"][0].astype(float)
            cer = cer * h["CER"].attrs.get("scale_factor", [1])[0]

            # COT optical thickness
            cot = h["COT"][0].astype(float)
            cot = cot * h["COT"].attrs.get("scale_factor", [1])[0]

            H, W = cer.shape

            # Build lat/lon from attributes
            if lat2d is None:
                lat2d, lon2d = build_latlon_from_attrs(h, H, W)

            acc_cer = cer if acc_cer is None else acc_cer + cer
            acc_cot = cot if acc_cot is None else acc_cot + cot
            n += 1

    cer_daily = acc_cer / n
    cot_daily = acc_cot / n

    lat_i, lon_i, cer_i = clip_to_india(lat2d, lon2d, cer_daily)
    _, _, cot_i = clip_to_india(lat2d, lon2d, cot_daily)
    grid_id = map_to_grid(lat_i, lon_i)

    # Create DF for CER + COT
    df = pd.DataFrame({"grid_id": grid_id, "cer": cer_i, "cot": cot_i})
    out = df.groupby("grid_id").mean().reset_index()

    # Fix missing rows
    full_grid = grid[["grid_id", "lat_center", "lon_center"]].copy()
    full_grid["date"] = datetime.strptime(date_str, "%d%b%Y").date()

    out = full_grid.merge(out, on="grid_id", how="left")
    # out["cer"] = out["cer"].fillna(0)
    # out["cot"] = out["cot"].fillna(0)

    return save_daily(out, "cmp", out["date"].iloc[0])

# 3.5 — UTH (already daily)
def process_uth_daily(date_str):

    fp = f"../../data_raw/8_days/uth/3RIMG_{date_str}_*_L3B_UTH_DLY_*.h5"
    files = sorted(glob.glob(fp))

    if not files:
        print(f"No UTH files for {date_str}")
        return None

    with h5py.File(files[0], "r") as h:
        uth = h["UTH_DLY"][0]
        H, W = uth.shape
        lat2d, lon2d = build_latlon_from_attrs(h, H, W)

    lat_i, lon_i, val_i = clip_to_india(lat2d, lon2d, uth)
    grid_id = map_to_grid(lat_i, lon_i)

    out = aggregate_and_fix_missing(grid_id, val_i, datetime.strptime(date_str, "%d%b%Y").date())
    out = out.rename(columns={"value": "uth"})

    return save_daily(out, "uth", out["date"].iloc[0])

# 3.6 — OLR (already daily)
def process_olr_daily(date_str):

    fp = f"../../data_raw/8_days/olr/3RIMG_{date_str}_*_L3B_OLR_DLY_*.h5"
    files = sorted(glob.glob(fp))

    if not files:
        print(f"No OLR files for {date_str}")
        return None

    with h5py.File(files[0], "r") as h:
        olr = h["OLR_DLY"][0]
        H, W = olr.shape
        lat2d, lon2d = build_latlon_from_attrs(h, H, W)

    lat_i, lon_i, val_i = clip_to_india(lat2d, lon2d, olr)
    grid_id = map_to_grid(lat_i, lon_i)

    out = aggregate_and_fix_missing(grid_id, val_i, datetime.strptime(date_str, "%d%b%Y").date())
    out = out.rename(columns={"value": "olr"})

    return save_daily(out, "olr", out["date"].iloc[0])

# 3.7 — HEM (mm/day already)
def process_hem_daily(date_str):

    fp = f"../../data_raw/8_days/hem/3RIMG_{date_str}_*_L3B_HEM_DLY_*.h5"
    files = sorted(glob.glob(fp))

    if not files:
        print(f"No HEM files for {date_str}")
        return None

    with h5py.File(files[0], "r") as h:
        hem = h["HEM_DLY"][0]
        H, W = hem.shape
        lat2d, lon2d = build_latlon_from_attrs(h, H, W)

    lat_i, lon_i, val_i = clip_to_india(lat2d, lon2d, hem)
    grid_id = map_to_grid(lat_i, lon_i)

    out = aggregate_and_fix_missing(grid_id, val_i, datetime.strptime(date_str, "%d%b%Y").date())
    out = out.rename(columns={"value": "hem"})

    return save_daily(out, "hem", out["date"].iloc[0])

if __name__ == "__main__":

    dates = ["15JAN2025", "21MAY2025", "10JUN2025", "20JUL2025", "25JUL2025", "15AUG2025", "20SEP2025", "10NOV2025"]

    for d in dates:
        print("\n======================")
        print("Processing IMC for", d)
        process_imc_daily(d)

        print("\nProcessing WDP for", d)
        process_wdp_daily(d)

        print("\nProcessing LST for", d)
        process_lst_daily(d)

        print("\nProcessing CMP for", d)
        process_cmp_daily(d)

        print("\nProcessing UTH for", d)
        process_uth_daily(d)

        print("\nProcessing OLR for", d)
        process_olr_daily(d)

        print("\nProcessing HEM for", d)
        process_hem_daily(d)

    print("\nAll datasets processed successfully!")