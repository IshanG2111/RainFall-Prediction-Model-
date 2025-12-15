from app import load_resources, get_lat_lon, find_nearest_grid, predict
import json
from flask import Flask

# Mock flask app context
app = Flask(__name__)

def test_prediction():
    print("Loading resources...")
    load_resources()
    
    print("Testing prediction logic...")
    with app.test_request_context(
        path='/predict', 
        method='POST', 
        json={'city': 'Delhi', 'date': '2023-08-15'}
    ):
        try:
            # We need to call the predict function directly
            # Note: app.py predict() returns a flask Response object
            from app import predict
            response = predict()
            print("Response status:", response.status_code)
            if response.status_code == 200:
                print("Success! Data:", response.get_json().keys())
                print("Prediction sample:", response.get_json()['predictions'][0])
            else:
                print("Failed:", response.get_json())
        except Exception as e:
            print(f"CRITICAL ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_prediction()
