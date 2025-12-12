import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_predictions():
    print(f"Testing API at {BASE_URL}")
    
    # 1. Test City
    print("\n--- Testing Prediction Endpoint (City) ---")
    data_city = {
        "city": "Mumbai",
        "date": "2024-07-20"
    }
    try:
        response = requests.post(f"{BASE_URL}/predict", json=data_city)
        if response.status_code == 200:
            result = response.json()
            print("✅ Prediction Successful (City)")
            print(f"   Tomorrows Rain: {result['predictions'][0]['Predicted_Rainfall']}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")

    # 2. Test Coordinates
    print("\n--- Testing Prediction Endpoint (Coordinates) ---")
    data_coords = {
        "latitude": 20.5937,
        "longitude": 78.9629,
        "date": "2024-07-20"
    }
    try:
        response = requests.post(f"{BASE_URL}/predict", json=data_coords)
        if response.status_code == 200:
            result = response.json()
            print("✅ Prediction Successful (Coordinates)")
            print(f"   Tomorrows Rain: {result['predictions'][0]['Predicted_Rainfall']}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_predictions()
