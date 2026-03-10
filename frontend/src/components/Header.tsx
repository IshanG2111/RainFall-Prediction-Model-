import { CloudRain } from 'lucide-react';

export default function Header() {
  return (
    <div className="flex flex-col items-start justify-center pb-4 border-b-4 border-gray-900 mb-8">
      <div className="flex items-center gap-4 mb-2">
        <CloudRain className="w-12 h-12 text-gray-900" strokeWidth={1.5} />
        <h1 className="text-6xl font-hand font-bold tracking-tight text-gray-900">
          Rainfall AI
        </h1>
      </div>
      <p className="text-gray-600 text-sm font-bold tracking-widest uppercase">
        // Machine Learning based Rainfall Prediction
      </p>
    </div>
  );
}
