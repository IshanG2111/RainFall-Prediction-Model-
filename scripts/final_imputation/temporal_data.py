import pandas as pd

def add_temporal_metadata(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Ensure datetime
    df["date"] = pd.to_datetime(df["date"])

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day
    df["day_of_year"] = df["date"].dt.dayofyear
    df["week_of_year"] = df["date"].dt.isocalendar().week.astype(int)

    # Indian monsoon: June (6) to September (9)
    df["monsoon_flag"] = df["month"].between(6, 9).astype(int)

    return df