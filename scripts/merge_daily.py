import os
import glob
import pandas as pd
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC_DIR = os.path.join(BASE_DIR, "data_processed", "2_days")

def load_daily(prefix, date):
    """Load daily parquet for one parameter."""
    folder = os.path.join(PROC_DIR, f"{prefix}_daily")
    pattern = os.path.join(folder, f"{prefix}_{date}.parquet")
    files = glob.glob(pattern)

    if not files:
        print(f"Missing daily file for {prefix} on {date}")
        return None

    return pd.read_parquet(files[0])


def merge_all_daily(date_str):
    """
    Step 3.8 → Merge IMC, WDP, LST, CMP, UTH, OLR, HEM
    into one master raw daily dataset.
    """

    # Load all daily datasets (None if missing)
    imc = load_daily("imc", date_str)
    wdp = load_daily("wdp", date_str)
    lst = load_daily("lst", date_str)
    cmp = load_daily("cmp", date_str)
    uth = load_daily("uth", date_str)
    olr = load_daily("olr", date_str)
    hem = load_daily("hem", date_str)

    # Start with IMC (we always expect rainfall IMC)
    master = imc.copy()

    # Merge all remaining datasets
    datasets = {
        "wdp": wdp,
        "lst": lst,
        "cmp": cmp,
        "uth": uth,
        "olr": olr,
        "hem": hem
    }

    for name, df in datasets.items():
        if df is not None:
            print(f"🔗 Merging {name.upper()}...")
            master = master.merge(
                df.drop(columns=["lat_center", "lon_center"]),
                on=["grid_id", "date"],
                how="left"
            )
        else:
            print(f"Skipping {name.upper()} (file missing)")

    # Ensure lat/lon remain only from IMC (already merged)
    master = master.sort_values(["date", "grid_id"]).reset_index(drop=True)

    # Save master output
    save_dir = os.path.join(PROC_DIR, "master_daily")
    os.makedirs(save_dir, exist_ok=True)

    outpath = os.path.join(save_dir, f"master_raw_{date_str}.parquet")
    master.to_parquet(outpath, index=False)

    print(f"Saved master raw file → {outpath}")
    return master


if __name__ == "__main__":
    dates = ["2025-07-15", "2025-07-16"]

    for d in dates:
        print("\n=================================")
        print("Merging Daily Files for", d)
        merge_all_daily(d)

    print("\nStep 3.8 Completed Successfully!")