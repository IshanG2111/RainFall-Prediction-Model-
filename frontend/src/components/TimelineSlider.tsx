import { Play, Pause, SkipForward, SkipBack } from 'lucide-react';
import { useState } from 'react';

function TimelineSlider(){
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress] = useState(30);

  const times = ['12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00'];

  return (
    <div className="absolute bottom-8 left-1/2 -translate-x-1/2 w-150 max-w-[90vw] z-10">
      <div className="bg-slate-900/80 backdrop-blur-xl border border-slate-800 rounded-2xl p-4 shadow-2xl flex flex-col gap-4">

        {/* Controls and Current Time */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button className="p-2 hover:bg-slate-800 rounded-full text-slate-400 hover:text-white transition-colors">
              <SkipBack className="w-4 h-4" />
            </button>
            <button
              className="p-3 bg-sky-500 hover:bg-sky-400 text-white rounded-full transition-colors shadow-lg shadow-sky-500/20"
              onClick={() => setIsPlaying(!isPlaying)}
            >
              {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 ml-0.5" />}
            </button>
            <button className="p-2 hover:bg-slate-800 rounded-full text-slate-400 hover:text-white transition-colors">
              <SkipForward className="w-4 h-4" />
            </button>
          </div>

          <div className="text-center">
            <div className="text-sm font-medium text-white">Today, 14:30</div>
            <div className="text-xs text-slate-400">Live Radar</div>
          </div>

          <div className="flex items-center gap-2 text-xs font-medium">
            <span className="px-2 py-1 rounded bg-slate-800 text-slate-300">Past</span>
            <span className="px-2 py-1 rounded bg-sky-500/20 text-sky-400 border border-sky-500/30">Live</span>
            <span className="px-2 py-1 rounded bg-slate-800 text-slate-300">Future</span>
          </div>
        </div>

        {/* Slider */}
        <div className="relative pt-2 pb-6">
          <div className="h-1.5 w-full bg-slate-800 rounded-full relative">
            <div
              className="absolute top-0 left-0 h-full bg-linear-to-r from-sky-600 to-sky-400 rounded-full"
              style={{ width: `${progress}%` }}
            ></div>
            <div
              className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full shadow-lg border-2 border-sky-500 cursor-pointer"
              style={{ left: `calc(${progress}% - 8px)` }}
            ></div>
          </div>

          {/* Time markers */}
          <div className="absolute w-full flex justify-between top-6 px-1">
            {times.map((time, i) => (
              <div key={time} className="flex flex-col items-center">
                <div className="w-0.5 h-1.5 bg-slate-700 mb-1"></div>
                <span className={`text-[10px] ${i === 2 ? 'text-sky-400 font-medium' : 'text-slate-500'}`}>
                  {time}
                </span>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}