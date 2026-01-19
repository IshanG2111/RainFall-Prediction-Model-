from pathlib import Path
import pandas as pd

def load_grid_definition():
    project_root = Path(__file__).resolve().parents[2]
    grid_path = project_root/"grid"/"grid_definition.parquet"

    if not grid_path.exists():
        raise FileNotFoundError(f"Grid file not found at: {grid_path}")

    return pd.read_parquet(grid_path)