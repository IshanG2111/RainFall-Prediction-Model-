<div align="center">

# Frontend — वृष्टि AI

![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-6-B73BFE?style=flat-square&logo=vite&logoColor=FFD62E)
![Tailwind](https://img.shields.io/badge/Tailwind_CSS-4-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)

</div>

> Interactive React dashboard for the वृष्टि AI 7-day forecast system.

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| **React 19** | Component-based UI framework |
| **Vite 6** | Fast build tool and HMR dev server |
| **Tailwind CSS 4** | Utility-first styling |
| **TypeScript** | Type-safe component development |
| **Recharts** | Precipitation trend charts |
| **Leaflet + React-Leaflet** | Interactive location map |
| **Lucide React** | Icon system |

---

## Quick Start

**Prerequisites:** Node.js 18+

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The dev server runs at **`http://localhost:5173`** with hot module replacement.

### Production Build

```bash
npm run build
```

Output is written to `frontend/dist/` and is served by the FastAPI backend in production.

---

## Proxy Configuration

The Vite dev server proxies all `/api` requests to the FastAPI backend:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:5000',
      changeOrigin: true
    }
  }
}
```

> **Important:** The FastAPI backend must be running on port `5000` for API calls to work during development.

---

## Project Structure

```
frontend/
├── src/
│   ├── App.tsx                # Root component — state management and layout
│   ├── api.ts                 # API client (searchLocations, getForecast)
│   ├── types.ts               # TypeScript interfaces (Location, ForecastResponse)
│   └── components/
│       ├── Header.tsx          # Application header / branding
│       ├── PredictionForm.tsx  # Location search + date picker + predict button
│       ├── TomorrowOutlook.tsx # Tomorrow's forecast highlight card
│       ├── SevenDayForecast.tsx # 7-day forecast card grid
│       ├── SeverityBadge.tsx   # Dynamic animated sketch severity tags
│       ├── PrecipitationTrend.tsx # Recharts rainfall trend chart
│       ├── LocationMap.tsx     # Leaflet map with location radar and CSS filters
│       └── WeatherSidebar.tsx  # Weather details sidebar
├── index.html                 # HTML entry point
├── package.json               # Dependencies and scripts
├── tsconfig.json              # TypeScript configuration
└── vite.config.ts             # Vite + proxy configuration
```

---

> For detailed architecture documentation, see [`docs/frontend.md`](../docs/frontend.md).
