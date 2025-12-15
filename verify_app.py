import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_predictions():
    print(f"Testing API at {BASE_URL}")
    
    # 1. Test City
    print("\n--- Testing Prediction Endpoint (City) ---")
    data_city = {
        "city": "Bhubaneswar",
        "date": "2025-07-15"
    }
    try:
        response = requests.post(f"{BASE_URL}/predict", json=data_city)
        if response.status_code == 200:
            result = response.json()
            print("✅ Prediction Successful")
            print(f"   Tomorrows Rain: {result['predictions'][0]['Predicted_Rainfall']}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")

    # 2. Test Coordinates - REMOVED (Not supported by current API)
    # The current app.py implementation solely relies on City Name to derive coordinates.
    # Passing raw coordinates is not currently implemented in the /predict endpoint.

if __name__ == "__main__":
    test_predictions()
