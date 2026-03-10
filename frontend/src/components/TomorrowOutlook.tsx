import { CloudDrizzle, CloudRain, Cloud, Sun, Loader2 } from 'lucide-react';
import type { ForecastResponse } from '../types';

interface Props {
  forecast: ForecastResponse | null;
  isLoading: boolean;
}

function getWeatherIcon(status: string) {
  const s = status.toLowerCase();
  if (s.includes('heavy')) return CloudRain;
  if (s.includes('moderate')) return CloudDrizzle;
  if (s.includes('light')) return CloudDrizzle;
  if (s.includes('no rain') || s.includes('clear')) return Sun;
  return Cloud;
}

export default function TomorrowOutlook({ forecast, isLoading }: Props) {
  const tomorrow = forecast?.forecast?.[0];
  const Icon = tomorrow ? getWeatherIcon(tomorrow.status) : CloudDrizzle;

  // Calculate 7-day stats
  const peak = forecast?.forecast?.reduce((max, d) => Math.max(max, d.rainfall_mm), 0) ?? 0;
  const total = forecast?.forecast?.reduce((sum, d) => sum + d.rainfall_mm, 0) ?? 0;

  if (isLoading) {
    return (
      <div className="sketch-border p-6 h-full flex items-center justify-center">
        <div className="flex flex-col items-center gap-4 text-gray-400">
          <Loader2 className="w-12 h-12 animate-spin" />
          <span className="text-sm font-bold uppercase tracking-widest">Generating forecast...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="sketch-border p-6 h-full flex flex-col">
      <h3 className="font-hand text-3xl font-bold mb-6 border-b-2 border-dashed border-gray-300 pb-2">
        {tomorrow ? "Tomorrow's Outlook" : "Forecast Preview"}
      </h3>

      <div className="flex-1 flex flex-col md:flex-row items-center gap-8 lg:gap-12 p-4">

        {/* Left: Big Icon & Main Stat */}
        <div className="flex flex-col items-center justify-center border-4 border-gray-900 rounded-full w-56 h-56 p-6 relative bg-white shadow-[8px_8px_0px_0px_#111827]">
          {tomorrow && (
            <div className="absolute -top-4 -right-2 bg-white px-3 py-1 font-bold border-2 border-gray-900 rotate-12 shadow-[2px_2px_0px_0px_#111827]">
              {new Date(tomorrow.date + 'T00:00:00').toLocaleDateString('en-US', { weekday: 'short', day: 'numeric' }).toUpperCase()}
            </div>
          )}
          <Icon className="w-20 h-20 mb-2 text-gray-900" strokeWidth={1.5} />
          <div className="flex items-baseline gap-1 text-gray-900">
            <span className="text-6xl font-bold tracking-tighter">
              {tomorrow ? tomorrow.rainfall_mm.toFixed(1) : '—'}
            </span>
            <span className="text-xl font-bold">mm</span>
          </div>
          <div className="text-xs font-bold mt-2 bg-gray-900 text-white px-3 py-1 uppercase tracking-widest">
            {tomorrow?.status ?? 'No Data'}
          </div>
        </div>

        {/* Right: Detailed Stats */}
        <div className="flex-1 w-full flex flex-col gap-6 justify-center">
          <div className="border-b-2 border-gray-900 pb-2 flex justify-between items-end">
            <span className="text-gray-500 text-xs font-bold uppercase tracking-widest">Status</span>
            <span className="font-bold text-2xl text-gray-900">{tomorrow?.status ?? '—'}</span>
          </div>
          <div className="border-b-2 border-gray-900 pb-2 flex justify-between items-end">
            <span className="text-gray-500 text-xs font-bold uppercase tracking-widest">Coordinates</span>
            <span className="font-bold text-lg text-gray-900">
              {forecast ? `${forecast.coordinates.lat.toFixed(3)}°, ${forecast.coordinates.lon.toFixed(3)}°` : '—'}
            </span>
          </div>
          <div className="border-b-2 border-gray-900 pb-2 flex justify-between items-end">
            <span className="text-gray-500 text-xs font-bold uppercase tracking-widest">7-Day Peak</span>
            <span className="font-bold text-lg text-gray-900">{forecast ? `${peak.toFixed(1)} mm` : '—'}</span>
          </div>
          <div className="border-b-2 border-gray-900 pb-2 flex justify-between items-end">
            <span className="text-gray-500 text-xs font-bold uppercase tracking-widest">7-Day Total</span>
            <span className="font-bold text-lg text-gray-900">{forecast ? `${total.toFixed(1)} mm` : '—'}</span>
          </div>
        </div>

      </div>
    </div>
  );
}
