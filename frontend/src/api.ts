import type { Location, ForecastResponse, HealthResponse } from './types';

const API_BASE = '/api/v1';

export async function searchLocations(query: string): Promise<Location[]> {
    if (query.length < 3) return [];
    const res = await fetch(`${API_BASE}/locations?q=${encodeURIComponent(query)}`);
    if (!res.ok) throw new Error(`Location search failed: ${res.status}`);
    return res.json();
}

export async function getForecast(
    location: string,
    lat: number,
    lon: number,
    date: string
): Promise<ForecastResponse> {
    const res = await fetch(`${API_BASE}/forecast`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ location, lat, lon, date }),
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Forecast request failed: ${res.status}`);
    }
    return res.json();
}

export async function checkHealth(): Promise<HealthResponse> {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
    return res.json();
}
