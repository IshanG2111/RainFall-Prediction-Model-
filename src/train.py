import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from joblib import dump

def train_model():
    df = pd.read_csv("data/processed/processed_data.csv")

    target_columns = [f"rain_mm_lag{h}" for h in range(1, 8)]
    features = [col for col in df.columns if col not in ['date', 'rain_mm'] + target_columns]

    # Models for 7 days ahead
    for h in range(1, 8):
        df[f"target_h{h}"] = df['rain_mm'].shift(-h)

    df = df.dropna()

    X = df[features]

    for h in range(1, 8):
        y = df[f"target_h{h}"]

        split = int(len(df) * 0.8)
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]

        model = LinearRegression()
        model.fit(X_train, y_train)

        preds = model.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        print(f"Day {h} MAE:", mae)

        dump(model, f"models/model_day_{h}.joblib")
        print(f"Saved model_day_{h}.joblib")

if __name__ == "__main__":
    train_model()
