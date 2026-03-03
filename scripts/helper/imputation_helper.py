import numpy as np
import pandas as pd
from scripts.helper.grid_neighbor import get_neighbors

def spatial_impute(df: pd.DataFrame,column: str,n_cols: int = 120) -> pd.DataFrame:
    df = df.copy()

    missing_mask = df[column].isna()
    if not missing_mask.any():
        return df

    for idx, row in df[missing_mask].iterrows():
        neighbors = get_neighbors(row["grid_id"], n_cols)
        vals = df.loc[df["grid_id"].isin(neighbors), column].dropna()
        if not vals.empty:
            df.at[idx, column] = vals.median()

    return df

def daily_mean_impute(df: pd.DataFrame,column: str,min_val=None,max_val=None) -> pd.DataFrame:
    df = df.copy()

    daily_mean = df.groupby("date")[column].transform("mean")
    df[column] = df[column].fillna(daily_mean)

    if min_val is not None:
        df[column] = df[column].clip(lower=min_val)
    if max_val is not None:
        df[column] = df[column].clip(upper=max_val)

    return df

def impute_cmp(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = spatial_impute(df, "cer")
    df = spatial_impute(df, "cot")

    return df