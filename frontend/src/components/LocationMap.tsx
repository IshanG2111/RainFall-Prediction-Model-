import { MapContainer, TileLayer, Circle, useMap } from 'react-leaflet';
import { useEffect, useMemo } from 'react';
import L from 'leaflet';
import 'leaflet.heat';

interface Props {
  coordinates: { lat: number; lon: number } | null;
  locationName: string | null;
}

function RecenterMap({ lat, lon }: { lat: number; lon: number }) {
  const map = useMap();
  useEffect(() => {
    map.flyTo([lat, lon], 11, { duration: 1.5 });
  }, [map, lat, lon]);
  return null;
}

function RainHeatmapLayer({ centerLat, centerLon }: { centerLat: number; centerLon: number }) {
  const map = useMap();
  
  // Base points with random phase and speed for vivid animation
  const basePoints = useMemo(() => {
    const pts = [];
    for (let i = 0; i < 60; i++) {
      // Gaussian-ish distribution to keep the storm localized but natural
      const angle = Math.random() * Math.PI * 2;
      const radius = Math.random() * Math.random() * 0.25; 
      const latOffset = Math.sin(angle) * radius;
      const lonOffset = Math.cos(angle) * radius;
      
      const maxIntensity = Math.random() * 1.5; // Allow for deep red peaks 
      const phase = Math.random() * Math.PI * 2;
      const speed = 0.4 + Math.random() * 1.5;
      
      pts.push({ latOffset, lonOffset, maxIntensity, phase, speed });
    }
    return pts;
  }, [centerLat, centerLon]);

  useEffect(() => {
    // Initialize the heat layer with an empty array.
    // @ts-ignore - leaflet.heat adds heatLayer to L
    const heat = L.heatLayer([], {
      radius: 45,      // Expansive radius for smooth blending
      blur: 40  ,        // High blur simulates atmospheric scattering
      maxZoom: 13,
      minOpacity: 0.15, // Keep the edges visible
      // Professional Meteorological Radar Gradient 
      gradient: { 
        0.3: '#38bdf8', // Light Blue (Light Rain)
        0.5: '#2563eb', // Royal Blue (Moderate Rain)
        0.7: '#22c55e', // Green (Heavy Rain)
        0.85: '#eab308', // Yellow (Very Heavy/Thunderstorm)
        1.0: '#ef4444'  // Red (Extreme/Hail)
      }
    }).addTo(map);

    let animationFrameId: number;
    let startTime = Date.now();

    const animate = () => {
      const elapsed = (Date.now() - startTime) / 1000;

      // Calculate dynamic intensities and drifting
      const currentPoints = basePoints.map(p => {
        // Pulsate intensity slowly like an active storm cell
        const dynamicIntensity = p.maxIntensity * (0.6 + 0.4 * Math.sin(elapsed * p.speed + p.phase));
        
        // Very slow drifting of the storm cells to mimic wind
        const driftLat = Math.sin(elapsed * 0.1 + p.phase) * 0.02;
        const driftLon = Math.cos(elapsed * 0.1 + p.phase) * 0.02;

        return [
          centerLat + p.latOffset + driftLat, 
          centerLon + p.lonOffset + driftLon, 
          dynamicIntensity
        ];
      });

      // Update the heatmap layer
      // @ts-ignore
      heat.setLatLngs(currentPoints);
      animationFrameId = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      cancelAnimationFrame(animationFrameId);
      map.removeLayer(heat);
    };
  }, [map, basePoints, centerLat, centerLon]);

  return null;
}

export default function LocationMap({ coordinates, locationName }: Props) {
  const center: [number, number] = coordinates
    ? [coordinates.lat, coordinates.lon]
    : [20.2960, 85.8246]; // Default: Bhubaneswar

  return (
    <div className="sketch-border p-6 h-full flex flex-col">
      <h3 className="font-hand text-3xl font-bold mb-6 border-b-2 border-dashed border-gray-300 pb-2">
        {locationName ? ` ${locationName}` : 'Location Map'}
      </h3>

      <div className="flex-1 border-2 border-gray-900 relative min-h-[350px] bg-white p-2">
        <div className="w-full h-full relative border-2 border-gray-900">
          <MapContainer
            center={center}
            zoom={11}
            className="w-full h-full absolute inset-0"
            zoomControl={true}
            scrollWheelZoom={false}
          >
            <TileLayer
              url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
              subdomains="abcd"
              maxZoom={20}
            />

            {coordinates && <RecenterMap lat={coordinates.lat} lon={coordinates.lon} />}

            {/* Dynamic cyan/blue rainfall heatmap */}
            <RainHeatmapLayer centerLat={center[0]} centerLon={center[1]} />

            {/* Inner pinpoint circle */}
            <Circle
              center={center}
              radius={200}
              pathOptions={{
                color: '#ffffff97',
                fillColor: '#0000007b',
                fillOpacity: 1,
                weight: 2
              }}
            />
          </MapContainer>
        </div>
      </div>
    </div>
  );
}
