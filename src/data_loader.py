import pandas as pd

FINAL_DATA_PATH = "data/final_dataset.parquet"
GRID_DATA_PATH = "data/grid_definition.parquet"

def load_final_dataset():
    return pd.read_parquet(FINAL_DATA_PATH)

def load_grid_dataset():
    return pd.read_parquet(GRID_DATA_PATH)
