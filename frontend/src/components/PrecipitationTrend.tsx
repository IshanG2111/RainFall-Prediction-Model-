import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { ForecastResponse } from '../types';

interface Props {
  forecast: ForecastResponse | null;
}

const defaultData = [
  { name: 'Day 1', rainfall: 0 },
  { name: 'Day 2', rainfall: 0 },
  { name: 'Day 3', rainfall: 0 },
  { name: 'Day 4', rainfall: 0 },
  { name: 'Day 5', rainfall: 0 },
  { name: 'Day 6', rainfall: 0 },
  { name: 'Day 7', rainfall: 0 },
];

export default function PrecipitationTrend({ forecast }: Props) {
  const data = forecast
    ? forecast.forecast.slice(1).map((day) => {
      const d = new Date(day.date + 'T00:00:00');
      return {
        name: d.toLocaleDateString('en-US', { weekday: 'short' }),
        rainfall: day.rainfall_mm,
        status: day.status,
      };
    })
    : defaultData;

  return (
    <div className="sketch-border p-6">
      <h3 className="font-hand text-3xl font-bold mb-6 border-b-2 border-dashed border-gray-300 pb-2">Precipitation Trend</h3>

      <div className="h-[350px] w-full mt-8">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="4 4" stroke="#d1d5db" vertical={false} />
            <XAxis
              dataKey="name"
              stroke="#111827"
              tick={{ fill: '#111827', fontFamily: 'Space Mono', fontWeight: 'bold' }}
              tickLine={false}
              axisLine={{ strokeWidth: 2 }}
              dy={10}
            />
            <YAxis
              stroke="#111827"
              tick={{ fill: '#111827', fontFamily: 'Space Mono', fontWeight: 'bold' }}
              tickLine={false}
              axisLine={{ strokeWidth: 2 }}
              dx={-10}
              label={{ value: 'Rainfall (mm)', angle: -90, position: 'insideLeft', fill: '#111827', fontFamily: 'Space Mono', fontWeight: 'bold' }}
            />
            <Tooltip
              cursor={{ fill: '#f3f4f6' }}
              contentStyle={{
                backgroundColor: '#fff',
                border: '2px solid #111827',
                borderRadius: '0px',
                boxShadow: '4px 4px 0px 0px #111827',
                fontFamily: 'Space Mono',
                fontWeight: 'bold'
              }}
              formatter={(value: number) => [`${value.toFixed(2)} mm`, 'Rainfall']}
            />
            <Legend wrapperStyle={{ paddingTop: '20px', fontFamily: 'Space Mono', fontWeight: 'bold' }} />
            <Bar
              dataKey="rainfall"
              name="Rainfall (mm)"
              fill="#111827"
              barSize={40}
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {!forecast && (
        <div className="text-center text-gray-400 text-xs font-bold uppercase tracking-widest mt-4">
          Search a location and predict to see real data
        </div>
      )}
    </div>
  );
}
