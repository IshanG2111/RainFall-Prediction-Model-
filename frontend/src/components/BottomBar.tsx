import { CloudRain, Navigation, Plus, Minus, Crosshair } from 'lucide-react';

export default function BottomBar() {
  return (
    <div className="absolute bottom-0 left-0 w-full z-[1000] pointer-events-none flex items-end justify-between p-10">
      
      {/* Left: Weather Info */}
      <div className="flex flex-col gap-2 pointer-events-auto">
        <div className="flex items-end gap-4">
          <CloudRain className="w-8 h-8 text-[#F27D26] mb-1" />
          <div className="text-4xl font-bold tracking-tighter text-white">28°</div>
          <div className="flex flex-col pb-1">
            <span className="text-[10px] font-bold tracking-wider text-white">NNW <Navigation className="inline w-3 h-3 -rotate-45" /></span>
            <span className="text-[10px] text-gray-400">13 km/h</span>
          </div>
        </div>
        <div className="text-[11px] font-medium text-gray-400 tracking-wide">
          Mon, 05 Aug, 2024 / 02:21 pm
        </div>
      </div>

      {/* Center: Selected Stations */}
      <div className="flex items-center gap-8 pointer-events-auto border-l border-white/10 pl-8">
        <div className="[writing-mode:vertical-rl] rotate-180 text-[10px] tracking-[0.2em] uppercase text-gray-500 font-bold">
          STATIONS <span className="text-white ml-2">3/3</span>
        </div>
        
        <div className="flex items-center gap-6">
          {/* Station 1 */}
          <div className="flex items-center gap-3">
            <div className="relative">
              <img src="https://picsum.photos/seed/station1/40/40" alt="Station" className="w-10 h-10 rounded-full border border-white/20 object-cover" />
              <div className="absolute -bottom-1 -right-1 w-4 h-4 rounded-full bg-[#10B981] border-2 border-[#1a1814] flex items-center justify-center text-[8px] font-bold text-white">
                01
              </div>
            </div>
            <div className="flex flex-col">
              <span className="text-xs font-bold text-white">London Central</span>
              <span className="text-[10px] text-gray-400">62, Via 84 A, Portum</span>
              <span className="text-[10px] text-gray-500">Villa Fortuna / Pergamum</span>
            </div>
          </div>

          {/* Station 2 */}
          <div className="flex items-center gap-3 opacity-60 hover:opacity-100 transition-opacity cursor-pointer">
            <div className="relative">
              <img src="https://picsum.photos/seed/station2/40/40" alt="Station" className="w-10 h-10 rounded-full border border-white/20 object-cover" />
              <div className="absolute -bottom-1 -right-1 w-4 h-4 rounded-full bg-[#10B981] border-2 border-[#1a1814] flex items-center justify-center text-[8px] font-bold text-white">
                02
              </div>
            </div>
            <div className="flex flex-col">
              <span className="text-xs font-bold text-white">Westminster Hub</span>
              <span className="text-[10px] text-gray-400">D685, Viridi Bellator</span>
              <span className="text-[10px] text-gray-500">Albus Aqua / Pergamum</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right: Detailed Card */}
      <div className="pointer-events-auto flex items-end gap-6">
        <div className="bg-[#1e1c18]/95 backdrop-blur-md border border-white/5 w-80 shadow-2xl">
          <img src="https://picsum.photos/seed/station3/320/120" alt="Station Cover" className="w-full h-24 object-cover opacity-80" />
          <div className="p-5">
            <h3 className="font-serif text-lg text-white mb-2">Southwark Station</h3>
            <p className="text-[10px] text-gray-400 leading-relaxed mb-4">
              52 Initium Pontis Via, 07506<br/>
              Frigus / Pergamum<br/>
              <span className="text-[#F27D26]">⚲ 110 m</span> &nbsp;&nbsp; 📞 (800) 367 5437
            </p>
            <button className="w-full py-3 bg-[#f5e6d3] hover:bg-white text-black text-[10px] font-bold tracking-wider uppercase transition-colors">
              Get More Information
            </button>
          </div>
        </div>

        {/* Map Controls */}
        <div className="flex flex-col gap-2 mb-4">
          <button className="w-10 h-10 bg-[#F27D26] hover:bg-[#e06b15] text-white flex items-center justify-center transition-colors shadow-lg">
            <Crosshair className="w-5 h-5" />
          </button>
          <div className="flex flex-col bg-white text-black shadow-lg">
            <button className="w-10 h-10 flex items-center justify-center hover:bg-gray-100 transition-colors border-b border-gray-200">
              <Plus className="w-5 h-5" />
            </button>
            <button className="w-10 h-10 flex items-center justify-center hover:bg-gray-100 transition-colors">
              <Minus className="w-5 h-5" />
            </button>
          </div>
          <div className="flex flex-col items-end gap-1 mt-4 text-[10px] text-gray-500 font-mono">
            <span>1,000 ft</span>
            <div className="w-full h-[1px] bg-gray-600"></div>
            <span>100 m</span>
          </div>
        </div>
      </div>

    </div>
  );
}
