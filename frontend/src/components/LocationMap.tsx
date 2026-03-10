import { MapContainer, TileLayer, Circle, useMap } from 'react-leaflet';
import { useEffect } from 'react';

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

export default function LocationMap({ coordinates, locationName }: Props) {
  const center: [number, number] = coordinates
    ? [coordinates.lat, coordinates.lon]
    : [22.802, 86.203]; // Default: Jamshedpur

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
              url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
              subdomains="abcd"
              maxZoom={20}
            />

            {coordinates && <RecenterMap lat={coordinates.lat} lon={coordinates.lon} />}

            <Circle
              center={center}
              radius={8000}
              pathOptions={{
                color: '#111827',
                fillColor: 'transparent',
                weight: 2,
                dashArray: '8 8'
              }}
            />
            <Circle
              center={center}
              radius={150}
              pathOptions={{
                color: '#111827',
                fillColor: '#111827',
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
