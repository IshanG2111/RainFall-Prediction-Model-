import { Cloud, CloudRain, CloudDrizzle, Sun } from 'lucide-react';
import type { ForecastResponse } from '../types';
import SeverityBadge from './SeverityBadge';

interface Props {
  forecast: ForecastResponse | null;
}

function getIcon(status: string) {
  const s = status.toLowerCase();
  if (s.includes('heavy')) return CloudRain;
  if (s.includes('moderate')) return CloudDrizzle;
  if (s.includes('light')) return CloudDrizzle;
  if (s.includes('no rain') || s.includes('clear')) return Sun;
  return Cloud;
}

export default function SevenDayForecast({ forecast }: Props) {
  if (!forecast) {
    return (
      <div className="sketch-border p-6 h-full">
        <h3 className="font-hand text-3xl font-bold mb-6 border-b-2 border-dashed border-gray-300 pb-2">7-Day Forecast</h3>
        <div className="flex items-center justify-center h-48 text-gray-400">
          <span className="text-sm font-bold uppercase tracking-widest">Awaiting prediction...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="sketch-border p-6 h-full">
      <h3 className="font-hand text-3xl font-bold mb-6 border-b-2 border-dashed border-gray-300 pb-2">7-Day Forecast</h3>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 lg:gap-6 mt-4">
        {forecast.forecast.slice(1).map((day, idx) => {
          const d = new Date(day.date + 'T00:00:00');
          const dayName = d.toLocaleDateString('en-US', { weekday: 'short' }).toUpperCase();
          const dateLabel = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
          const Icon = getIcon(day.status);

          return (
            <div
              key={day.date}
              className="border-2 border-gray-900 p-4 flex flex-col items-center text-center relative bg-white hover:-translate-y-1 hover:shadow-[4px_4px_0px_0px_#111827] transition-all cursor-pointer"
              id={`forecast-day-${idx}`}
            >
              <div className="absolute -top-3 -left-2 bg-gray-900 text-white text-[10px] font-bold px-2 py-1 rotate-[-5deg]">
                {dateLabel}
              </div>
              <div className="text-gray-900 font-bold tracking-widest mt-4 mb-3 text-lg">{dayName}</div>
              <Icon className="w-10 h-10 mb-3 text-gray-800" strokeWidth={1.5} />
              <SeverityBadge status={day.status} className="mb-2 !text-[10px] sm:!text-xs" />
              <div className="text-sm font-bold border-b-2 border-gray-900 mb-3 pb-1 w-full">{day.rainfall_mm.toFixed(1)} mm</div>
              <div className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">
                {day.rainfall_mm > 0 ? `${day.rainfall_mm.toFixed(2)} mm` : 'Dry'}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
