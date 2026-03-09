# Frontend Architecture

This document outlines the architecture, setup, and technologies used in the frontend of the Rainfall Prediction Model application.

## 🛠️ Tech Stack

- **Vanilla HTML5/CSS3/JavaScript**: Core UI elements.
- **Custom CSS / Glassmorphism**: For styling and layout.
- **Chart.js**: Render predictive data charts.
- **Leaflet**: Interactive map components.
- **Framer Motion**: (via CDN) For smooth UI animations and transitions.

## 🏗️ Structure

The frontend is a lightweight, single-page application served directly from the backend.

```text
Project Root/
├── templates/
│   └── index.html          # Main HTML entry point containing UI and Logic
├── static/                 # Static assets (CSS, JS, images, if any)
```

## 🚀 Setup & Installation

There is no separate build step for the frontend. It is served concurrently by the FastAPI backend using standard HTML responses.

## 💻 Running Locally

Start the FastAPI backend application. The frontend will be served at the root URL:

```bash
python src/app.py
```

The app will be available on `http://localhost:5000`.

## 🔌 API Integration

The `templates/index.html` file utilizes Vanilla JavaScript `fetch` calls to asynchronously interact with the local `/api/v1/forecast` and `/api/v1/locations` endpoints to retrieve and display live prediction data.
