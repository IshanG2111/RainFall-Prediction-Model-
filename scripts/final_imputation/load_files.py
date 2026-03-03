import glob
import pandas as pd
from pathlib import Path

def load_master_daily_files(processed_base_dir: Path):
    master_dir = processed_base_dir / "master_daily"
    pattern = master_dir / "master_raw_*.parquet"

    files = sorted(glob.glob(str(pattern)))

    if not files:
        raise FileNotFoundError(f"No master_raw daily files found in {master_dir}")

    dfs = [pd.read_parquet(f) for f in files]
    print(f"Loaded {len(dfs)} master daily files.")

    return dfs