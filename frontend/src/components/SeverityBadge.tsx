import React from 'react';

interface Props {
  status: string;
  className?: string; // Allow layout overrides
}

export default function SeverityBadge({ status, className = '' }: Props) {
  const s = status.toLowerCase();
  
  // Sketch-styled base: thick solid ink borders, paper-like background colors, hand-drawn font
  let base = "inline-flex items-center justify-center font-hand font-bold uppercase tracking-widest border-2 border-gray-900 ";
  
  let colorAnim = "";

  if (s.includes('extreme') || s.includes('hail')) {
    colorAnim = "bg-red-300 text-gray-900 animate-[sketch-pop-frantic_0.6s_ease-in-out_infinite]";
  } else if (s.includes('very heavy')) {
    colorAnim = "bg-yellow-300 text-gray-900 animate-[sketch-pop-fast_1s_ease-in-out_infinite]";
  } else if (s.includes('heavy')) {
    colorAnim = "bg-green-300 text-gray-900 animate-[sketch-pop-med_1.5s_ease-in-out_infinite]";
  } else if (s.includes('moderate')) {
    colorAnim = "bg-blue-300 text-gray-900 animate-[sketch-pop-slow_2s_ease-in-out_infinite]";
  } else if (s.includes('light')) {
    colorAnim = "bg-sky-200 text-gray-900 animate-[sketch-pop-slow_3s_ease-in-out_infinite]";
  } else {
    // Default/Clear/No Rain
    colorAnim = "bg-gray-100 text-gray-500 shadow-[2px_2px_0px_0px_#111827]";
  }
  
  return (
    <div className={`${base} ${colorAnim} ${className}`}>
      {status || 'No Data'}
    </div>
  );
}
