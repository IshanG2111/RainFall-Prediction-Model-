// Backend API response types matching FastAPI schemas

export interface Location {
    place: string;
    lat: number;
    lon: number;
}

export interface ForecastDay {
    date: string;
    rainfall_mm: number;
    status: string;
}

export interface ForecastResponse {
    location: string;
    coordinates: {
        lat: number;
        lon: number;
    };
    forecast: ForecastDay[];
}

export interface HealthResponse {
    status: string;
    model_loaded: boolean;
    grid_loaded: boolean;
}
