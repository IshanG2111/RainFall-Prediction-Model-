import { useState, useCallback } from 'react';
import Header from './components/Header';
import PredictionForm from './components/PredictionForm';
import TomorrowOutlook from './components/TomorrowOutlook';
import PrecipitationTrend from './components/PrecipitationTrend';
import SevenDayForecast from './components/SevenDayForecast';
import LocationMap from './components/LocationMap';
import { searchLocations, getForecast } from './api';
import type { Location, ForecastResponse } from './types';

export default function App() {
  const [locations, setLocations] = useState<Location[]>([]);
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = useCallback(async (query: string) => {
    try {
      const results = await searchLocations(query);
      setLocations(results);
    } catch {
      setLocations([]);
    }
  }, []);

  const handleSelectLocation = useCallback((location: Location) => {
    setSelectedLocation(location);
    setLocations([]);
  }, []);

  const handlePredict = useCallback(async (date: string) => {
    if (!selectedLocation) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await getForecast(
        selectedLocation.place,
        selectedLocation.lat,
        selectedLocation.lon,
        date
      );
      setForecast(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Prediction failed');
      setForecast(null);
    } finally {
      setIsLoading(false);
    }
  }, [selectedLocation]);

  return (
    <div className="min-h-screen p-4 md:p-8 lg:p-12">
      <div className="max-w-7xl mx-auto">
        <Header />

        {error && (
          <div className="sketch-border mb-6 p-4 bg-red-50 border-red-900 text-red-900 text-sm font-bold">
            ⚠ {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 md:gap-8">
          {/* Top Row */}
          <div className="md:col-span-5 lg:col-span-4">
            <PredictionForm
              onSearch={handleSearch}
              onSelectLocation={handleSelectLocation}
              onPredict={handlePredict}
              locations={locations}
              selectedLocation={selectedLocation}
              isLoading={isLoading}
            />
          </div>
          <div className="md:col-span-7 lg:col-span-8">
            <TomorrowOutlook forecast={forecast} isLoading={isLoading} />
          </div>

          {/* Middle Row */}
          <div className="md:col-span-12">
            <PrecipitationTrend forecast={forecast} />
          </div>

          {/* Bottom Row */}
          <div className="md:col-span-12 lg:col-span-7">
            <SevenDayForecast forecast={forecast} />
          </div>
          <div className="md:col-span-12 lg:col-span-5">
            <LocationMap coordinates={forecast?.coordinates ?? null} locationName={forecast?.location ?? null} />
          </div>
        </div>

        <div className="mt-16 text-center text-xs font-bold text-gray-500 uppercase tracking-widest">
          // Powered by Rainfall AI //
        </div>
      </div>
    </div>
  );
}
