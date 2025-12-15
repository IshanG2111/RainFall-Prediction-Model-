import pickle
import os

filepath = 'models/model_frame_1.pkl'
if os.path.exists(filepath):
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
    metrics = data['metrics']
    with open('metrics.txt', 'w') as out:
        out.write(f"RMSE: {metrics['RMSE']:.4f}\n")
        out.write(f"MAE: {metrics['MAE']:.4f}\n")
        out.write(f"R2: {metrics['R2']:.4f}\n")
        out.write(f"Features: {data['feature_columns']}\n")
    print("Metrics written cleaned.")
else:
    print("Model file not found.")
