import numpy as np
import pandas as pd
from datetime import datetime
from backend.core.dependencies import (get_model,get_scaler,get_feature_columns,get_master_df,)
from src.model import PhysicsConstraints

def _get_realistic_features(grid_id: int, date_target: datetime) -> dict:
    master_df = get_master_df()

    default_features = {"hem": 0,"wind_speed": 10,"uth": 40,"olr": 250,"lst_k": 300,"cer": 10,"cot": 10,}

    seed = int(grid_id) + date_target.year * 10000 + \
           date_target.month * 100 + date_target.day
    seed = seed % (2**32 - 1)

    if master_df is None or master_df.empty:
        rng = np.random.default_rng(seed)
        for k in default_features:
            default_features[k] *= rng.uniform(0.95, 1.05)
        return default_features

    grid_data = master_df[master_df["grid_id"] == grid_id]

    if grid_data.empty:
        sample = master_df.sample(1, random_state=seed).iloc[0]
    else:
        sample = grid_data.sample(1, random_state=seed).iloc[0]

    features = {
        "hem": sample.get("hem", 0),
        "wind_speed": sample.get("wind_speed", 10),
        "uth": sample.get("uth", 40),
        "olr": sample.get("olr", 250),
        "lst_k": sample.get("lst_k", 300),
        "cer": sample.get("cer", 10),
        "cot": sample.get("cot", 10),
    }

    rng = np.random.default_rng(seed)
    for k in features:
        features[k] *= rng.uniform(0.95, 1.05)

    return features

def predict_single_day(grid_id: int,center_lat: float,center_lon: float,date_target: datetime,) -> float:

    model = get_model()
    scaler = get_scaler()
    feature_columns = get_feature_columns()

    if model is None:
        raise ValueError("Model not loaded.")

    # Base Features
    features_dict = _get_realistic_features(grid_id, date_target)

    # Cyclic Time Features
    day_of_year = date_target.timetuple().tm_yday
    week_of_year = date_target.isocalendar()[1]

    features_dict["day_sin"] = np.sin(2 * np.pi * day_of_year / 366)
    features_dict["day_cos"] = np.cos(2 * np.pi * day_of_year / 366)
    features_dict["week_sin"] = np.sin(2 * np.pi * week_of_year / 53)
    features_dict["week_cos"] = np.cos(2 * np.pi * week_of_year / 53)

    # Arrange Features EXACT order from training
    input_data = [features_dict.get(col, 0) for col in feature_columns]
    input_df = pd.DataFrame([input_data], columns=feature_columns)

    # Scale
    if scaler:
        input_df = scaler.transform(input_df)

    # Predict (log scale)
    pred_log = model.predict(input_df)[0]

    # Inverse transform
    pred_rainfall = np.expm1(pred_log)
    pred_rainfall = max(0, pred_rainfall)

    # Physics Adjustment
    constraint_features = {
        "latitude": center_lat,
        "longitude": center_lon,
        "month": date_target.month,
        "olr": features_dict.get("olr", 250),
        "uth": features_dict.get("uth", 50),
        "elevation": 0,
    }

    final_rain, _ = PhysicsConstraints.apply_post_inference_adjustments(pred_rainfall, constraint_features)

    return round(float(final_rain), 2)