import { useState } from 'react';

export default function LeftSidebar() {
  const [activeCategory, setActiveCategory] = useState('Rainfall');

  const categories = [
    'Temperature',
    'Wind Speed',
    'Rainfall',
    'Humidity',
    'Pressure',
    'Cloud Cover',
    'Visibility',
    'UV Index'
  ];

  return (
    <div className="absolute left-0 top-1/2 -translate-y-1/2 z-[1000] flex h-[60vh] pointer-events-none">
      
      {/* Vertical Navigation */}
      <div className="flex flex-col items-center justify-center w-16 border-r border-white/5 pointer-events-auto">
        <div className="flex flex-col items-center gap-16">
          <div className="relative group cursor-pointer">
            <span className="[writing-mode:vertical-rl] rotate-180 text-[10px] tracking-[0.2em] uppercase text-gray-500 group-hover:text-gray-300 transition-colors">
              Forecast
            </span>
          </div>
          <div className="relative group cursor-pointer flex flex-col items-center gap-3">
            <div className="w-1.5 h-1.5 rounded-full bg-[#F27D26]"></div>
            <span className="[writing-mode:vertical-rl] rotate-180 text-[10px] tracking-[0.2em] uppercase text-white font-medium">
              Live Data
            </span>
          </div>
        </div>
      </div>

      {/* Categories List */}
      <div className="w-48 pl-8 py-8 flex flex-col justify-center gap-6 pointer-events-auto">
        {categories.map((category) => {
          const isActive = category === activeCategory;
          return (
            <button
              key={category}
              onClick={() => setActiveCategory(category)}
              className={`text-left transition-all duration-300 cursor-pointer ${
                isActive 
                  ? 'font-serif text-3xl text-white' 
                  : 'text-sm text-gray-400 hover:text-gray-200'
              }`}
            >
              {category} {isActive && <span className="text-lg text-gray-500 font-sans font-light ml-1">(3)</span>}
            </button>
          );
        })}
      </div>
    </div>
  );
}
