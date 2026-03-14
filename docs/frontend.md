# Frontend Architecture — Rainfall AI

> Complete reference for the React + Vite frontend application that powers the Rainfall AI dashboard.

---

## Table of Contents

1. [Tech Stack](#1-tech-stack)
2. [Project Structure](#2-project-structure)
3. [Component Reference](#3-component-reference)
4. [State Management](#4-state-management)
5. [API Integration](#5-api-integration)
6. [Setup & Development](#6-setup--development)
7. [Build & Deployment](#7-build--deployment)

---

## 1. Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 19 | Component-based UI framework |
| Vite | 6 | Build tool with HMR dev server |
| Tailwind CSS | 4 | Utility-first CSS framework |
| TypeScript | 5 | Static type checking |
| Recharts | 2 | Data visualisation (bar/line charts) |
| Leaflet + React-Leaflet | 4 | Interactive map rendering |
| Lucide React | — | SVG icon library |

---

## 2. Project Structure

```
frontend/
├── src/
│   ├── App.tsx                    # Root component (state, layout, data flow)
│   ├── api.ts                     # API client functions
│   ├── types.ts                   # TypeScript type definitions
│   └── components/
│       ├── Header.tsx             # App branding and title
│       ├── PredictionForm.tsx     # Location autocomplete + date picker + predict button
│       ├── TomorrowOutlook.tsx    # Highlighted forecast card for Day 1
│       ├── SevenDayForecast.tsx   # 7-day forecast grid (cards)
│       ├── PrecipitationTrend.tsx # Recharts bar/line chart for rainfall trends
│       ├── LocationMap.tsx        # Leaflet map with dynamic marker
│       ├── WeatherSidebar.tsx     # Detailed weather sidebar panel
│       ├── TopNav.tsx             # Top navigation bar
│       ├── LeftSidebar.tsx        # Left category navigation
│       ├── BottomBar.tsx          # Bottom status / info bar
│       └── TimelineSlider.tsx     # Timeline playback slider
├── index.html                     # HTML entry point
├── package.json                   # Dependencies and scripts
├── tsconfig.json                  # TypeScript compiler configuration
└── vite.config.ts                 # Vite bundler + dev proxy configuration
```

---

## 3. Component Reference

### `App.tsx` — Root Component

The top-level component manages all application state and orchestrates data flow between child components.

**State variables:**
| Variable | Type | Purpose |
|----------|------|---------|
| `locations` | `Location[]` | Autocomplete search results |
| `selectedLocation` | `Location \| null` | User's chosen location |
| `forecast` | `ForecastResponse \| null` | 7-day forecast data from API |
| `isLoading` | `boolean` | Forecast prediction loading state |
| `isSearchingLocation` | `boolean` | Location search loading state |
| `error` | `string \| null` | Error message for display |

### `PredictionForm.tsx`
- **Location search** with debounced autocomplete (300ms delay, ≥ 3 characters).
- **Skeleton loaders** displayed during location search.
- **Date picker** defaulting to tomorrow's date.
- **Predict button** with loading spinner animation and cursor state changes.

### `TomorrowOutlook.tsx`
- Displays the first day of the forecast with a large rainfall value and status badge.
- Supports loading state skeleton.

### `SevenDayForecast.tsx`
- Renders all 7 forecast days as interactive cards.
- Colour-coded by rainfall category (No Rain, Light, Moderate, Heavy).

### `PrecipitationTrend.tsx`
- Recharts bar chart showing daily rainfall trends.
- Interactive tooltips and responsive sizing.

### `LocationMap.tsx`
- Leaflet map that updates its marker based on the forecast coordinates.
- Zoom and pan enabled.

---

## 4. State Management

State is managed through React `useState` and `useCallback` hooks in `App.tsx`. There is no external state library — the application is simple enough for prop drilling:

```
App.tsx (state owner)
├── PredictionForm ← locations, selectedLocation, isLoading, isSearchingLocation
├── TomorrowOutlook ← forecast, isLoading
├── PrecipitationTrend ← forecast
├── SevenDayForecast ← forecast
└── LocationMap ← forecast.coordinates, forecast.location
```

---

## 5. API Integration

API calls are defined in `src/api.ts` and proxy through Vite to the FastAPI backend:

| Function | Endpoint | Trigger |
|----------|----------|---------|
| `searchLocations(query)` | `GET /api/v1/locations?q=…` | User types ≥ 3 chars (debounced) |
| `getForecast(location, lat, lon, date)` | `POST /api/v1/forecast` | User clicks "Predict Forecast" |

### Vite Proxy

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

> The FastAPI backend must be running on port **5000** for API requests to succeed during development.

---

## 6. Setup & Development

**Prerequisites:** Node.js 18+

```bash
cd frontend
npm install
npm run dev
```

The development server runs at **`http://localhost:5173`** with hot module replacement enabled.

---

## 7. Build & Deployment

```bash
npm run build
```

- Output: `frontend/dist/`
- The FastAPI backend serves the built assets via `StaticFiles` mount at `/assets` and a catch-all route that returns `index.html` for client-side routing.
- No separate frontend deployment is needed — the backend serves everything.

---

> For backend API reference, see [`docs/backend_architecture.md`](backend_architecture.md).
