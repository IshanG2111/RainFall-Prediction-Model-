import numpy as np
import joblib
from sklearn.metrics import mean_squared_error, r2_score
from src.data_loader import load_final_dataset
FEATURES = [
    "lat_center","lon_center",
    "wind_speed","lst_k",
    "cer","cot","uth",
    "olr","hem","monsoon_flag"
]

TARGET = "rain_mm"

df = load_final_dataset()
df = df.sort_values("date")

dates = df["date"].unique()
train_df = df[df["date"] == dates[0]]
test_df  = df[df["date"] == dates[1]]

X_test = test_df[FEATURES]
y_true = test_df[TARGET]

models = {
    "Random Forest": joblib.load("models/random_forest.pkl"),
    "Gradient Boosting": joblib.load("models/gradient_boosting.pkl")
}

print("MODEL COMPARISON (Time-based split)")
print("----------------------------------")

for name, model in models.items():
    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)

    print(f"{name}")
    print(f"  RMSE: {rmse:.2f}")
    print(f"  R²  : {r2:.3f}")
