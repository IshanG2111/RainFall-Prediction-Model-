import os
import glob
import pandas as pd
import numpy as np

# PATHS
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER_DIR = os.path.join(BASE_DIR, "data_processed", "2_days", "master_daily")
FINAL_DIR  = os.path.join(BASE_DIR, "data_processed", "2_days", "finaldata")
os.makedirs(FINAL_DIR, exist_ok=True)

# 4.1 LOAD ALL MASTER FILES
def load_master_daily_files():
    pattern = os.path.join(MASTER_DIR, "master_raw_*.parquet")
    files = sorted(glob.glob(pattern))

    if not files:
        raise FileNotFoundError("No master_raw daily files found in Step 3.8 output.")

    dfs = [pd.read_parquet(f) for f in files]
    print(f"Loaded {len(dfs)} master daily files.")
    return dfs

# 4.3 ADD TEMPORAL FEATURES
def add_temporal_metadata(df):
    df["date"] = pd.to_datetime(df["date"])
    df["day"] = df["date"].dt.day
    df["month"] = df["date"].dt.month
    df["year"] = df["date"].dt.year
    df["day_of_year"] = df["date"].dt.dayofyear
    df["week_of_year"] = df["date"].dt.isocalendar().week.astype(int)

    # Monsoon flag: June–September
    df["monsoon_flag"] = df["month"].isin([6, 7, 8, 9]).astype(int)

    return df

# 4.6 IMPUTATION HELPERS
def get_neighbors(grid_id, num_cols=120):
    """Return 4-neighbor grid_ids around a given cell."""
    neighbors = []

    # North (grid_id + num_cols)
    if grid_id + num_cols < 15360:
        neighbors.append(grid_id + num_cols)

    # South
    if grid_id - num_cols >= 0:
        neighbors.append(grid_id - num_cols)

    # East
    if (grid_id + 1) % num_cols != 0:
        neighbors.append(grid_id + 1)

    # West
    if grid_id % num_cols != 0:
        neighbors.append(grid_id - 1)

    return neighbors

def spatial_impute(df, col):
    """Spatial median imputation for LST, WDP, CER, COT."""
    print(f"Spatial imputing {col}...")

    df_copy = df.copy()

    for idx, row in df_copy[df_copy[col].isna()].iterrows():
        gid = row["grid_id"]
        date = row["date"]

        neighbors = get_neighbors(gid)
        neighbor_vals = df_copy[(df_copy["grid_id"].isin(neighbors)) & (df_copy["date"] == date)][col].dropna()

        if len(neighbor_vals) > 0:
            df_copy.at[idx, col] = neighbor_vals.median()
        else:
            # fallback → same latitude band median
            same_row_ids = df_copy[(df_copy["date"] == date) &
                                   (df_copy["grid_id"] // 120 == gid // 120)][col].dropna()

            if len(same_row_ids) > 0:
                df_copy.at[idx, col] = same_row_ids.median()

    return df_copy


def daily_mean_impute(df, col, min_val=None, max_val=None):
    """Mean imputation for UTH, OLR, HEM with physical constraints."""
    print(f"Daily-mean imputing {col}...")

    df_copy = df.copy()

    for d in df["date"].unique():
        mask = df_copy["date"] == d
        mean_val = df_copy.loc[mask, col].mean()

        df_copy.loc[mask & df_copy[col].isna(), col] = mean_val

    # Apply physical clipping
    if min_val is not None:
        df_copy[col] = df_copy[col].clip(lower=min_val)
    if max_val is not None:
        df_copy[col] = df_copy[col].clip(upper=max_val)

    return df_copy

# ADVANCED LST (Land Surface Temperature) IMPUTATION
def impute_lst(df):
    """
    Three-stage hierarchical imputation for LST:
    1. Spatial neighbor median
    2. Latitude-band median
    3. Monthly climatological median
    """

    print("Applying advanced LST imputation...")

    df = df.copy()

    # 1) PRECOMPUTE MONTHLY CLIMATOLOGY
    df["month"] = df["date"].dt.month

    monthly_clim = (
        df.groupby("month")["lst_k"]
        .median()  # <-- FIXED (no skipna)
        .to_dict()
    )

    # 2) LOOP THROUGH MISSING LST VALUES
    for idx, row in df[df["lst_k"].isna()].iterrows():
        gid = row["grid_id"]
        date = row["date"]
        month = row["month"]

        # ---- STEP 1: SPATIAL NEIGHBOR MEDIAN ----
        neighbors = get_neighbors(gid)
        neighbor_vals = df[
            (df["grid_id"].isin(neighbors)) &
            (df["date"] == date)
        ]["lst_k"].dropna()

        if len(neighbor_vals) > 0:
            df.at[idx, "lst_k"] = neighbor_vals.median()
            continue  # done for this cell

        # ---- STEP 2: LATITUDE BAND MEDIAN ----
        lat_band = gid // 120  # compute row (0–127)
        band_vals = df[
            (df["grid_id"] // 120 == lat_band) &
            (df["date"] == date)
        ]["lst_k"].dropna()

        if len(band_vals) > 0:
            df.at[idx, "lst_k"] = band_vals.median()
            continue  # done

        # ---- STEP 3: MONTHLY CLIMATOLOGY ----
        if month in monthly_clim and not np.isnan(monthly_clim[month]):
            df.at[idx, "lst_k"] = monthly_clim[month]
        else:
            # emergency fallback
            df.at[idx, "lst_k"] = df["lst_k"].median()

    # 3) PHYSICAL BOUNDS FOR LST
    df["lst_k"] = df["lst_k"].clip(lower=200, upper=330)

    print("LST imputation complete.")
    return df

# MAIN IMPUTATION LOGIC (4.6)
def apply_imputation(df):

    # (A) TARGET IMC → Drop missing
    # df = df.dropna(subset=["rain_mm"])
    print("Dropped rows with missing IMC.")

    # (B) Spatial imputation for derived variables
    df = impute_lst(df)  # NEW FUNCTION FOR LST

    df.loc[df["cer"] < 0, "cer"] = np.nan
    df.loc[df["cot"] < 0, "cot"] = np.nan

    # Wind, CER, COT keep spatial impute
    for col in ["wind_speed", "cer", "cot"]:
        df = spatial_impute(df, col)

    df["cer"] = df["cer"].clip(lower=0, upper=60)
    df["cot"] = df["cot"].clip(lower=0, upper=200)

    # (C) Daily mean imputation for daily variables
    df = daily_mean_impute(df, "uth", min_val=0, max_val=100)
    df = daily_mean_impute(df, "olr", min_val=100, max_val=300)
    df = daily_mean_impute(df, "hem", min_val=0)

    return df

# COMPLETE PIPELINE (4.1 → 4.8)
def build_final_dataset():

    # 4.1 load master raw files
    dfs = load_master_daily_files()

    # 4.2 Combine all days
    df = pd.concat(dfs, ignore_index=True)
    print("Combined shape:", df.shape)

    # 4.3 Add metadata
    df = add_temporal_metadata(df)

    # 4.4 Validate IMC + drop missing
    df = df.dropna(subset=["rain_mm"])

    # 4.6 Apply imputation rules
    df = apply_imputation(df)

    # 4.7 Final clean
    df = df.sort_values(["date", "grid_id"]).reset_index(drop=True)

    # 4.8 Save final dataset
    outpath = os.path.join(FINAL_DIR, "final_dataset.parquet")
    df.to_parquet(outpath, index=False)

    print(f"Final dataset saved → {outpath}")
    print("FINAL SHAPE:", df.shape)

    return df

if __name__ == "__main__":
    build_final_dataset()