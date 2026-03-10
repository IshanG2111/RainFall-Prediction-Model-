import { CloudRain, Droplets, Wind, Navigation, Search, Menu } from 'lucide-react';

export default function WeatherSidebar() {
  return (
    <div className="absolute top-0 left-0 h-full w-80 bg-slate-900/80 backdrop-blur-xl border-r border-slate-800 z-10 flex flex-col shadow-2xl">
      {/* Header */}
      <div className="p-6 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2 text-sky-400">
          <CloudRain className="w-6 h-6" />
          <span className="font-bold text-lg tracking-wide text-white">Precipitate</span>
        </div>
        <button className="p-2 hover:bg-slate-800 rounded-full transition-colors">
          <Menu className="w-5 h-5 text-slate-400" />
        </button>
      </div>

      {/* Search */}
      <div className="p-6 pb-2">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input 
            type="text" 
            placeholder="Search location..." 
            className="w-full bg-slate-800/50 border border-slate-700 rounded-xl py-2.5 pl-10 pr-4 text-sm text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-sky-500/50 focus:ring-1 focus:ring-sky-500/50 transition-all"
          />
        </div>
      </div>

      {/* Current Location Weather */}
      <div className="p-6 flex-1 overflow-y-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-2xl font-light text-white">London</h2>
            <p className="text-slate-400 text-sm flex items-center gap-1 mt-1">
              <Navigation className="w-3 h-3" /> Current Location
            </p>
          </div>
          <div className="text-4xl font-light text-white">
            14°
          </div>
        </div>

        {/* Rain Stats */}
        <div className="bg-slate-800/40 rounded-2xl p-5 border border-slate-700/50 mb-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-full bg-sky-500/20 flex items-center justify-center">
              <CloudRain className="w-5 h-5 text-sky-400" />
            </div>
            <div>
              <div className="text-sm text-slate-400">Precipitation</div>
              <div className="text-lg font-medium text-white">Heavy Rain</div>
            </div>
          </div>
          
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs mb-1.5">
                <span className="text-slate-400">Intensity</span>
                <span className="text-sky-400 font-medium">8.4 mm/h</span>
              </div>
              <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-sky-500 to-indigo-500 w-[75%] rounded-full"></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs mb-1.5">
                <span className="text-slate-400">Probability</span>
                <span className="text-white font-medium">95%</span>
              </div>
              <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-sky-400 w-[95%] rounded-full"></div>
              </div>
            </div>
          </div>
        </div>

        {/* Other Stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-slate-800/40 rounded-2xl p-4 border border-slate-700/50">
            <Droplets className="w-5 h-5 text-blue-400 mb-2" />
            <div className="text-xs text-slate-400 mb-1">Humidity</div>
            <div className="text-lg font-medium text-white">87%</div>
          </div>
          <div className="bg-slate-800/40 rounded-2xl p-4 border border-slate-700/50">
            <Wind className="w-5 h-5 text-teal-400 mb-2" />
            <div className="text-xs text-slate-400 mb-1">Wind</div>
            <div className="text-lg font-medium text-white">12 km/h</div>
          </div>
        </div>
      </div>
    </div>
  );
}
