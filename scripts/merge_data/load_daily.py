import glob
import pandas as pd
from pathlib import Path

def load_daily(prefix: str, date_str: str, processed_base_dir: Path):
    daily_dir = processed_base_dir / f"{prefix}_daily"
    pattern = daily_dir / f"{prefix}_{date_str}.parquet"

    files = glob.glob(str(pattern))

    if not files:
        print(f"Missing {prefix.upper()} daily file for {date_str}")
        return None

    return pd.read_parquet(files[0])