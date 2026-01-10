import pandas as pd
import joblib

from src.data_loader import load_final_dataset, load_grid_dataset

FEATURES = [
    "lat_center","lon_center",
    "wind_speed","lst_k",
    "cer","cot","uth",
    "olr","hem","monsoon_flag"
]

def get_nearest_grid(lat, lon):
    grid_df = load_grid_dataset()
    grid_df["dist"] = (
        (grid_df["lat_center"] - lat)**2 +
        (grid_df["lon_center"] - lon)**2
    )
    return grid_df.loc[grid_df["dist"].idxmin()]

def predict_city(lat, lon, model_name="random_forest"):
    df = load_final_dataset()
    grid = get_nearest_grid(lat, lon)
    grid_df = df[df["grid_id"] == grid["grid_id"]]

    latest = grid_df.sort_values("date").iloc[-1]
    X = latest[FEATURES].to_frame().T

    model = joblib.load(f"models/{model_name}.pkl")
    rain = model.predict(X)[0]

    future_dates = pd.date_range(
        start=pd.Timestamp.today().normalize(),
        periods=7
    )

    return pd.DataFrame({
        "date": future_dates,
        "predicted_rain_mm": rain
    })


if __name__ == "__main__":
    # Kolkata
    print(predict_city(22.5726, 88.3639, model_name="gradient_boosting"))

