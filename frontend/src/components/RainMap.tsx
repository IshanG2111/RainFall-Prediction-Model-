import { MapContainer, TileLayer, Polyline, Marker, useMap } from 'react-leaflet';
import { useEffect } from 'react';
import L from 'leaflet';
import 'leaflet.heat';

// Custom Icons
const createGreenIcon = (num: string) => L.divIcon({
  className: 'custom-div-icon',
  html: `<div style="background-color: #10B981; color: white; border: 2px solid #1a1814; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">${num}</div>`,
  iconSize: [24, 24],
  iconAnchor: [12, 12]
});

const orangePinIcon = L.divIcon({
  className: 'custom-div-icon',
  html: `<div style="background-color: #F27D26; border: 2px solid white; border-radius: 50% 50% 50% 0; width: 24px; height: 24px; transform: rotate(-45deg); display: flex; align-items: center; justify-content: center; box-shadow: 2px 2px 6px rgba(0,0,0,0.4);"><div style="width: 8px; height: 8px; background: white; border-radius: 50%;"></div></div>`,
  iconSize: [24, 24],
  iconAnchor: [12, 24]
});

// Mock Heatmap Data (lat, lng, intensity)
const heatPoints: [number, number, number][] = [
  [51.505, -0.09, 0.8],
  [51.51, -0.1, 0.5],
  [51.49, -0.08, 0.9],
  [51.52, -0.12, 0.3],
  [51.48, -0.11, 0.6],
  [51.50, -0.05, 0.7],
  [51.515, -0.08, 0.4],
];

// Mock Route Data
const routeCoords: [number, number][] = [
  [51.49, -0.11], // Start (Orange Pin)
  [51.50, -0.105],
  [51.505, -0.12], // Point 02
  [51.515, -0.11],
  [51.52, -0.09], // Point 01
  [51.51, -0.08],
  [51.505, -0.07], // End (Orange Pin)
];

function HeatmapLayer({ points }: { points: [number, number, number][] }) {
  const map = useMap();
  useEffect(() => {
    // @ts-ignore - leaflet.heat adds heatLayer to L
    const heat = L.heatLayer(points, {
      radius: 40,
      blur: 30,
      maxZoom: 13,
      gradient: { 0.2: '#0ea5e9', 0.4: '#3b82f6', 0.6: '#eab308', 0.8: '#ef4444', 1.0: '#991b1b' }
    }).addTo(map);
    return () => {
      map.removeLayer(heat);
    };
  }, [map, points]);
  return null;
}

export default function RainMap() {
  const center: [number, number] = [51.505, -0.09];

  return (
    <div className="w-full h-full relative z-0">
      <MapContainer 
        center={center} 
        zoom={13} 
        className="w-full h-full"
        zoomControl={false}
        attributionControl={false}
      >
        {/* Dark themed map tiles with custom filter applied via CSS */}
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          subdomains="abcd"
          maxZoom={20}
        />
        
        {/* Fluid Heatmap Layer */}
        <HeatmapLayer points={heatPoints} />

        {/* Route Line */}
        <Polyline 
          positions={routeCoords} 
          pathOptions={{ color: '#F27D26', weight: 3, opacity: 0.8, dashArray: '5, 10' }} 
        />

        {/* Custom Markers */}
        <Marker position={routeCoords[0]} icon={orangePinIcon} />
        <Marker position={routeCoords[routeCoords.length - 1]} icon={orangePinIcon} />
        
        <Marker position={[51.52, -0.09]} icon={createGreenIcon('01')} />
        <Marker position={[51.505, -0.12]} icon={createGreenIcon('02')} />

      </MapContainer>
    </div>
  );
}

