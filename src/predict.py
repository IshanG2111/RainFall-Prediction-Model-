import pandas as pd
from joblib import load

def predict_next_7_days(input_dict):
    df = pd.DataFrame([input_dict])

    models = [load(f"models/model_day_{i}.joblib") for i in range(1, 8)]

    preds = []
    for m in models:
        preds.append(m.predict(df)[0])

    return preds
