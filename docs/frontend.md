# Frontend Architecture

This document outlines the architecture, setup, and technologies used in the frontend of the Rainfall Prediction Model application.

## 🛠️ Tech Stack

- **React 19**: Core UI library.
- **Vite 6**: Fast build tool and development server.
- **Tailwind CSS 4**: Utility-first CSS framework for styling.
- **Framer Motion**: For smooth UI animations and transitions.
- **Leaflet & React-Leaflet**: Interactive map components for location and data mapping.
- **Recharts**: Render beautiful predictive data charts.

## 🏗️ Structure

The frontend represents a modern, enhanced user interface built with React, located within the `frontend/` directory. 

```text
frontend/
├── src/                # React components, routing, and hooks
├── package.json        # Node dependencies and scripts
├── vite.config.ts      # Vite build configuration
└── .env.local          # Environment variables (API integration)
```

## 🚀 Setup & Installation

**Prerequisites:** Node.js environment

1. **Navigate to the frontend directory**
    ```bash
    cd frontend
    ```
2. **Install dependencies**
    ```bash
    npm install
    ```

## 💻 Running Locally

To run the development server:

```bash
npm run dev
```

The app will typically be available on port 3000 (`http://localhost:3000`).

## 🔌 API Integration

Ensure that the FastAPI backend server is also running simultaneously so that the React application can interact with the necessary API endpoints to fetch live forecasts.
