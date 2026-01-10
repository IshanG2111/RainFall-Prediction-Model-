def preprocess_data(df):
    df = df.dropna(subset=["rain_mm"])
    df = df.sort_values("date")
    return df
