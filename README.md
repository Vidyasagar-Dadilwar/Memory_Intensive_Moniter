# Memory Intensive Monitor

A real-time process memory monitoring application with visualization capabilities.

## Features

- Real-time process monitoring (CPU, memory usage)
- Sortable and filterable process table
- Process termination capabilities (with confirmation)
- Threshold-based alerting
- Optional logging for historical data
- Optional notifications

## Architecture

```
[OS processes]  <--psutil--  Backend (FastAPI)  <--HTTP/WS-->  Frontend (React)
                                    |
                                    +--> Optional Logger (SQLite or CSV)
                                    +--> Optional Notification module (desktop / email)
```

## Components

1. **Process Monitor**: Uses psutil to collect process information
2. **Backend API**: FastAPI server exposing process data
3. **Frontend UI**: React application for visualization
4. **Alerting System**: Configurable thresholds with notifications
5. **Logger**: Optional historical data storage

## Project Structure

```
memory-monitor/
├─ backend/
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ monitor.py   # psutil wrapper
│  │  ├─ api.py       # endpoints
│  │  └─ logger.py    # optional sqlite/csv logger
│  ├─ requirements.txt
│  └─ Dockerfile
├─ frontend/
│  ├─ public/
│  ├─ src/
│  │  ├─ App.jsx
│  │  ├─ ProcessTable.jsx
│  │  └─ thresholds.js
│  └─ package.json
├─ docs/
├─ tests/
└─ README.md
```

## Setup and Installation

### Backend

1. Navigate to the backend directory
2. Install dependencies: `pip install -r requirements.txt`
3. Run the server: `uvicorn app.main:app --reload`

### Frontend

1. Navigate to the frontend directory
2. Install dependencies: `npm install`
3. Run the development server: `npm start`

## Development Phases

1. Phase 1 — Core monitor script (CLI) — collect & display data
2. Phase 2 — Backend API exposing JSON + kill endpoint
3. Phase 3 — Frontend UI (MVP): polling table, threshold highlight
4. Phase 4 — Advanced: WebSocket, logging, charts, notifications, packaging
5. Final — Documentation, tests, presentation slides