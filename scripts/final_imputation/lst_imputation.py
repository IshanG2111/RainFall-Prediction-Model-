import numpy as np
import pandas as pd
from scripts.helper.grid_neighbor import get_neighbors

def impute_lst(df: pd.DataFrame,lst_col: str = "lst_k",lat_col: str = "lat_center",grid_col: str = "grid_id",date_col: str = "date",n_cols: int = 120) -> pd.DataFrame:
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])

    missing_idx = df[df[lst_col].isna()].index

    for idx in missing_idx:
        grid_id = df.at[idx, grid_col]
        neighbors = get_neighbors(grid_id, n_cols)
        vals = df.loc[df[grid_col].isin(neighbors), lst_col].dropna()

        if not vals.empty:
            df.at[idx, lst_col] = vals.median()

    still_missing = df[lst_col].isna()
    if still_missing.any():
        lat_bins = pd.cut(df[lat_col], bins=10)

        for bin_cat in lat_bins[still_missing].unique():
            mask = (lat_bins == bin_cat)
            median_val = df.loc[mask, lst_col].median()
            df.loc[mask & df[lst_col].isna(), lst_col] = median_val

    df["month"] = df[date_col].dt.month

    monthly_median = (df.groupby("month")[lst_col].median())

    df[lst_col] = df[lst_col].fillna(df["month"].map(monthly_median))

    # Cleanup
    df.drop(columns=["month"], inplace=True)

    return df