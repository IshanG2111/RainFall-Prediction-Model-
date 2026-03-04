import { useState, useEffect, useRef } from 'react';
import { Calendar, MapPin, Loader2 } from 'lucide-react';
import type { Location } from '../types';

interface Props {
  onSearch: (query: string) => void;
  onSelectLocation: (location: Location) => void;
  onPredict: (date: string) => void;
  locations: Location[];
  selectedLocation: Location | null;
  isLoading: boolean;
}

export default function PredictionForm({ onSearch, onSelectLocation, onPredict, locations, selectedLocation, isLoading }: Props) {
  const [locationQuery, setLocationQuery] = useState('');
  const [date, setDate] = useState(() => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split('T')[0];
  });
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Debounced search
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (locationQuery.length >= 3) {
      debounceRef.current = setTimeout(() => {
        onSearch(locationQuery);
        setShowDropdown(true);
      }, 300);
    } else {
      setShowDropdown(false);
    }
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
  }, [locationQuery, onSearch]);

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const handleSelect = (loc: Location) => {
    onSelectLocation(loc);
    setLocationQuery(loc.place);
    setShowDropdown(false);
  };

  const formatDateDisplay = (isoDate: string) => {
    const d = new Date(isoDate + 'T00:00:00');
    return d.toLocaleDateString('en-IN', { day: '2-digit', month: '2-digit', year: 'numeric' }).replace(/\//g, '-');
  };

  return (
    <div className="sketch-border p-6 h-full flex flex-col justify-between">
      <h3 className="font-hand text-3xl font-bold mb-6 border-b-2 border-dashed border-gray-300 pb-2">Query Parameters</h3>

      <div className="flex flex-col gap-8 flex-1 justify-center">
        {/* Location Input with Autocomplete */}
        <div className="relative" ref={dropdownRef}>
          <label className="block text-gray-500 text-xs font-bold mb-2 uppercase tracking-widest">Location</label>
          <div className="flex items-center border-b-2 border-gray-900 pb-2">
            <MapPin className="w-5 h-5 mr-3 text-gray-700" strokeWidth={1.5} />
            <input
              type="text"
              value={locationQuery}
              onChange={(e) => setLocationQuery(e.target.value)}
              placeholder="Search for a city..."
              className="w-full bg-transparent text-gray-900 font-bold focus:outline-none text-lg"
              id="location-input"
            />
          </div>

          {/* Autocomplete Dropdown */}
          {showDropdown && locations.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-2 bg-white border-2 border-gray-900 shadow-[4px_4px_0px_0px_#111827] z-50 max-h-60 overflow-y-auto">
              {locations.map((loc, idx) => (
                <button
                  key={`${loc.place}-${idx}`}
                  onClick={() => handleSelect(loc)}
                  className="w-full text-left px-4 py-3 hover:bg-gray-100 border-b border-gray-200 last:border-b-0 transition-colors flex items-center gap-3"
                  id={`location-option-${idx}`}
                >
                  <MapPin className="w-4 h-4 text-gray-400 flex-shrink-0" strokeWidth={1.5} />
                  <div>
                    <div className="font-bold text-sm text-gray-900">{loc.place}</div>
                    <div className="text-[10px] text-gray-500 font-mono">{loc.lat.toFixed(4)}°, {loc.lon.toFixed(4)}°</div>
                  </div>
                </button>
              ))}
            </div>
          )}

          {selectedLocation && (
            <div className="mt-2 text-[10px] text-gray-500 font-mono">
              ✓ {selectedLocation.lat.toFixed(4)}°N, {selectedLocation.lon.toFixed(4)}°E
            </div>
          )}
        </div>

        {/* Date Input */}
        <div className="relative">
          <label className="block text-gray-500 text-xs font-bold mb-2 uppercase tracking-widest">Date</label>
          <div className="flex items-center border-b-2 border-gray-900 pb-2">
            <Calendar className="w-5 h-5 mr-3 text-gray-700" strokeWidth={1.5} />
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="w-full bg-transparent text-gray-900 font-bold focus:outline-none text-lg"
              id="date-input"
            />
          </div>
          <div className="mt-2 text-[10px] text-gray-500 font-mono">
            Display: {formatDateDisplay(date)}
          </div>
        </div>

        <button
          onClick={() => onPredict(date)}
          disabled={!selectedLocation || isLoading}
          className={`sketch-border sketch-button w-full py-4 mt-4 font-bold uppercase tracking-widest text-sm transition-all ${!selectedLocation
              ? '!bg-gray-200 text-gray-500 cursor-not-allowed'
              : isLoading
                ? '!bg-gray-900 text-white opacity-80 cursor-wait'
                : '!bg-gray-900 text-white'
            }`}
          id="predict-button"
        >
          {isLoading ? (
            <span className="flex items-center justify-center gap-2">
              <Loader2 className="w-5 h-5 animate-spin text-white" />
              Predicting...
            </span>
          ) : (
            'Predict Forecast'
          )}
        </button>
      </div>
    </div>
  );
}
