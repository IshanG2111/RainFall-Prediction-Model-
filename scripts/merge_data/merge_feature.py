import pandas as pd
from pathlib import Path
from scripts.merge_data.load_daily import load_daily
from datetime import datetime

def merge_all_daily(date_str: str,processed_base_dir: Path,save: bool = True):
    # Load all daily datasets
    iso_date = datetime.strptime(date_str, "%d%b%Y").date().isoformat()

    imc = load_daily("imc", iso_date, processed_base_dir)
    if imc is None:
        print(f"IMC missing for {iso_date}. Skipping merge.")
        return None

    datasets = {
        "wdp": load_daily("wdp", iso_date, processed_base_dir),
        "lst": load_daily("lst", iso_date, processed_base_dir),
        "cmp": load_daily("cmp", iso_date, processed_base_dir),
        "uth": load_daily("uth", iso_date, processed_base_dir),
        "olr": load_daily("olr", iso_date, processed_base_dir),
        "hem": load_daily("hem", iso_date, processed_base_dir),
    }

    # Start with IMC as base
    master = imc.copy()

    # Merge remaining datasets
    for name, df in datasets.items():
        if df is not None:
            print(f"Merging {name.upper()} for {date_str}")
            master = master.merge(df.drop(columns=["lat_center", "lon_center"], errors="ignore"),on=["grid_id", "date"],how="left")
        else:
            print(f"Skipping {name.upper()} (missing file)")

    master = master.sort_values(["date", "grid_id"]).reset_index(drop=True)

    # Save if requested
    if save:
        save_dir = processed_base_dir / "master_daily"
        save_dir.mkdir(parents=True, exist_ok=True)

        outpath = save_dir / f"master_raw_{iso_date}.parquet"
        master.to_parquet(outpath, index=False)
        print(f"Saved master daily file → {outpath}")

    return master