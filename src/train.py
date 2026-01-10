import numpy as np
import joblib

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

from src.data_loader import load_final_dataset
from src.preprocess import preprocess_data

FEATURES = [
    "lat_center","lon_center",
    "wind_speed","lst_k",
    "cer","cot","uth",
    "olr","hem","monsoon_flag"
]

TARGET = "rain_mm"

df = load_final_dataset()
df = preprocess_data(df)

# Remove extreme outliers
upper = df[TARGET].quantile(0.99)
df = df[df[TARGET] <= upper]

X = df[FEATURES]
y = df[TARGET]

# ------------------
# Random Forest
# ------------------
rf = RandomForestRegressor(
    n_estimators=200,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)
rf.fit(X, y)
joblib.dump(rf, "models/random_forest.pkl")

# ------------------
# Gradient Boosting
# ------------------
gbr = GradientBoostingRegressor(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=5,
    random_state=42
)
gbr.fit(X, y)
joblib.dump(gbr, "models/gradient_boosting.pkl")

print("✅ Random Forest & Gradient Boosting models trained")
