# Backend Architecture and Plan
Backend is implemented using **FastAPI**, a modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints. The backend serves as the interface between the trained machine learning model and the frontend application, providing endpoints for data retrieval and prediction.

## Key Components of the Backend:
1. **Model Loading**: The backend loads the trained machine learning model (e.g., `model_frame_1.pkl`) at startup, ensuring that predictions can be made without delay.
2. **API Endpoints**:
   - **/api/locations**: This endpoint allows users to query available locations for which predictions can be made. It retrieves location data from the dataset and returns it in a structured format.
   - **/api/forecast**: This endpoint accepts user input (location and date range) and returns rainfall predictions based on the loaded model. It processes the input, makes predictions, and formats the output for the frontend.
   - **/api/health**: A simple health check endpoint to verify that the backend is running properly.
3. **Data Handling**: The backend is responsible for handling data preprocessing and ensuring that the input data is in the correct format for the model to make accurate predictions.
4. **Error Handling**: The backend includes error handling mechanisms to manage invalid inputs, model prediction errors, and other potential issues gracefully.
5. **Performance Optimization**: The backend is designed to be efficient, ensuring that predictions are returned quickly to provide a smooth user experience on the frontend.
6. **Security**: Implementing security measures to protect the API endpoints from unauthorized access and potential threats.
7. **Rate Limiting**: Implementing rate limiting to prevent abuse of the API and ensure fair usage.

## Implementation Plan:
1. **Set Up FastAPI**: Initialize a FastAPI application and set up the necessary dependencies.
2. **Model Integration**: Load the trained machine learning model at startup and ensure it is ready for making predictions.
3. **Define API Endpoints**: Implement the `/api/locations`, `/api/forecast`, and `/api/health` endpoints with appropriate request handling and response formatting.
4. **Data Preprocessing**: Implement any necessary data preprocessing steps to ensure that the input data is compatible with the model's requirements.
5. **Testing**: Thoroughly test each endpoint using tools like Postman or Swagger UI to ensure that they are functioning correctly and returning the expected results.
6. **Deployment**: Deploy the backend to a suitable hosting environment (e.g., AWS, Heroku) to make it accessible to the frontend application.

## Routes and Endpoints:
1. **/api/locations**: Retrieve a list of available locations for predictions.
    - Method: GET
    - Query Parameters: `query` - A string to filter locations based on user input.
        - Example: `/api/locations?query=New`
    - Response: JSON array of location names and identifiers.
        - Example Response:
        ```json
        [
            {
              "place": "New Delhi, India",
              "lat": 28.6138954,
              "lon": 77.2090057
            },
            {
              "place": "New Delhi Railway Station, Delhi, India",
              "lat": 28.6402816,
              "lon": 77.22041029249536
            },
            {
              "place": "New Barrackpore, WB, India",
              "lat": 22.6860681,
              "lon": 88.4446406
            },
            {
              "place": "New Friends Colony, Delhi, India",
              "lat": 28.5671008,
              "lon": 77.2697643
            },
            {
              "place": "New Town, WB, India",
              "lat": 22.5882834,
              "lon": 88.4734476
            }
        ]
        ```
    - Rate Limiting: 15 requests per minute per IP address to prevent abuse and ensure fair usage.
2. **/api/forecast**: Get rainfall predictions for a specific location and date range.
    - Method: POST
    - Request Body: JSON object containing `location`, `latitude`, `longitude`, `date`.
        - Example Request Body:
        ```json
        {
            "location": "New Delhi, India",
            "lat": 28.6138954,
            "lon": 77.2090057,
            "date": "2026-03-04"
        }
        ```
    - Response: JSON object containing the predicted rainfall and uncertainty.
        - Example Response:
        ```json
        {
            "location": "New Delhi, India",
            "coordinates": 
            {
                "lat": 28.6138954,
                "lon": 77.2090057
            },
            "forecast": 
            [
                {
                    "date": "2026-03-04",
                    "rainfall_mm": 0.33,
                    "status": "Light Rain"
                },
                {
                    "date": "2026-03-05",
                    "rainfall_mm": 0.0,
                    "status": "No Rain"
                },
                {
                    "date": "2026-03-06",
                    "rainfall_mm": 0.19,
                    "status": "Light Rain"
                },
                {
                    "date": "2026-03-07",
                    "rainfall_mm": 1.19,
                    "status": "Light Rain"
                },
                {
                    "date": "2026-03-08",
                    "rainfall_mm": 0.43,
                    "status": "Light Rain"
                },
                {
                    "date": "2026-03-09",
                    "rainfall_mm": 5.08,
                    "status": "Moderate Rain"
                },
                {
                    "date": "2026-03-10",
                    "rainfall_mm": 8.39,
                    "status": "Moderate Rain"
                }
            ]
        }
        ```
    - Rate Limiting: 5 requests per minute per IP address to prevent abuse and ensure fair usage.
3. **/api/health**: Check if the backend is running properly.
    - Method: GET
    - Response: JSON object indicating the health status of the backend.
        - Example Response:
        ```json
        {
          "status": "ok",
          "model_loaded": true,
          "grid_loaded": true
        }
        ```
   
## Backend File Structure:
```backend/
├── core/
│   ├── config.py                 # Centralized application settings, environment variables, and model/data file paths
│   ├── dependencies.py           # Singleton resource loader for model, scaler, grid data, master dataset, and cache
│   ├── rate_limiter.py           # Centralized shared rate limiter instance for global API traffic control and abuse protection
├── routes/
│   ├── locations.py              # GET /api/locations endpoint for location autocomplete with caching
│   ├── forecast.py               # POST /api/forecast endpoint that triggers 7-day ML rainfall prediction
│   ├── health.py                 # GET /api/health endpoint to verify backend, model, and grid readiness
├── schemas/
│   ├── location_schema.py        # Pydantic response models for location autocomplete results
│   ├── forecast_schema.py        # Pydantic response models defining structured 7-day forecast output
│   ├── request_schema.py         # Pydantic request model for validating forecast input payload
├── services/
│   ├── date_service.py           # Generates sequential 7-day forecast date array
│   ├── forecast_service.py       # Orchestrates full forecast pipeline (date → grid → model → response)
│   ├── geocoding_service.py      # Handles external geocoding API calls and result formatting
│   ├── grid_service.py           # Maps latitude/longitude to nearest grid cell using grid parquet
│   ├── model_service.py          # ML inference wrapper: feature engineering, scaling, prediction, and physics adjustment
├── utils/
│   ├── cache.py                  # In-memory TTL cache implementation for geocoding optimization
├── app.py                        # FastAPI application factory with CORS setup, router registration, and startup initialization
```

## How to Run the Backend:
1. **Install Dependencies**:
    - Navigate to the backend directory and install the required Python packages using pip:
    ```bash
    pip install -r requirements.txt
    ```
2. **Train the Model**:
    - Run the training script to train the machine learning model and save it for use by the backend:
    ```bash
    python training.py
    ```
    - This will save the trained model to `models/model_frame_1.pkl` and prepare it for loading by the backend.
3. **Set Up Environment Variables** (if required):
    - Ensure that any necessary environment variables for paths or API keys (e.g., for geocoding services) are set up according to the `config.py` specifications.
4. **Start the FastAPI Server**:
    - Run the following command to start the backend server:
    ```bash
    uvicorn backend.app:app --reload
    ```
5. **Access the API**:
    - API Documentation: `http://127.0.0.1:8000/docs`
    - Postman or Swagger UI can be used to test the endpoints:
        - GET `/api/locations?query=New`
        - POST `/api/forecast` with JSON body containing location, lat, lon, and date.
        - GET `/api/health` to check backend status.
    - The backend will return structured JSON responses based on the input and the predictions made by the loaded machine learning model.
6. **Monitor Logs**:
    - Keep an eye on the terminal logs for any errors or issues during API calls, model loading, or data processing to ensure smooth operation.

# Conclusion:
The backend architecture is designed to efficiently serve machine learning predictions while providing a robust API for the frontend to interact with. By following the outlined structure and implementation plan, the backend can be developed and deployed effectively to support the overall application functionality.

---
*Developed for Rainfall Prediction Project - 6th Sem*