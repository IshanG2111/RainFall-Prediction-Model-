import pandas as pd
from scripts.helper.imputation_helper import (spatial_impute,daily_mean_impute,impute_cmp)
from scripts.final_imputation.lst_imputation import impute_lst

def apply_imputation(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "lst_k" in df.columns:
        df = impute_lst(df)

    if {"cer", "cot"}.issubset(df.columns):
        df = impute_cmp(df)

    daily_mean_columns = {"uth": (0, 100),"olr": (50, 400),"hem": (0, None),}

    for col, bounds in daily_mean_columns.items():
        if col in df.columns:
            min_val, max_val = bounds
            df = daily_mean_impute(df,column=col,min_val=min_val,max_val=max_val)

    return df