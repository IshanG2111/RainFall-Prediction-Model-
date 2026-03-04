import { Shield, Search, Menu } from 'lucide-react';

export default function TopNav() {
  return (
    <div className="absolute top-0 left-0 w-full z-[1000] flex items-center justify-between px-10 py-8 pointer-events-none">
      {/* Logo Area */}
      <div className="flex items-center gap-3 pointer-events-auto cursor-pointer">
        <div className="text-[#F27D26]">
          <Shield className="w-8 h-8" strokeWidth={2.5} />
        </div>
        <div className="flex flex-col">
          <span className="font-serif text-xl font-bold leading-tight tracking-wide text-white">Precipitate</span>
          <span className="text-xs text-gray-400 tracking-wider">Weather</span>
        </div>
      </div>

      {/* Navigation Links */}
      <div className="hidden md:flex items-center gap-12 pointer-events-auto">
        {['TODAY', 'TOMORROW', 'RADAR', 'ALERTS'].map((item) => (
          <button 
            key={item} 
            className="text-[11px] font-bold tracking-[0.15em] text-gray-300 hover:text-white uppercase transition-colors"
          >
            {item}
          </button>
        ))}
      </div>

      {/* Right Icons */}
      <div className="flex items-center gap-6 pointer-events-auto">
        <button className="text-gray-300 hover:text-white transition-colors">
          <Search className="w-5 h-5" strokeWidth={2} />
        </button>
        <button className="text-gray-300 hover:text-white transition-colors">
          <Menu className="w-6 h-6" strokeWidth={2} />
        </button>
      </div>
    </div>
  );
}
