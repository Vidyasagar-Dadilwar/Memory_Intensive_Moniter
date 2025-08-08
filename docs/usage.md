# Memory Intensive Monitor - Usage Guide

## Overview

Memory Intensive Monitor is a real-time process monitoring application that allows you to track memory and CPU usage of all processes running on your system. It provides a web-based interface for easy visualization and interaction.

## Features

- Real-time monitoring of all system processes
- Detailed memory and CPU usage statistics
- Process filtering and sorting
- Process termination capabilities
- Threshold-based highlighting and alerts
- Optional historical data logging
- WebSocket for real-time updates

## Installation

### Prerequisites

- Python 3.9 or higher
- Node.js 14 or higher (for frontend development)

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Run the server:
   ```
   uvicorn app.main:app --reload --port 8000
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```

### Quick Start

For convenience, you can use the provided `run_dev.bat` script (Windows) to start both the backend and frontend in development mode:

```
run_dev.bat
```

## Using the Application

### Main Interface

The main interface displays a table of all running processes, sorted by memory usage by default. Each process shows:

- PID (Process ID)
- Name
- Username
- Memory usage (MB and percentage)
- CPU usage (percentage)
- Start time
- Action buttons

### Filtering and Sorting

- Use the filter box to search for specific processes by name, PID, or username
- Click on column headers to sort by that column
- Use the dropdown to limit the view to top N processes

### Process Details

Click on any process row to view detailed information and, if logging is enabled, a historical chart of memory and CPU usage.

### Terminating Processes

To terminate a process:

1. Click the "Kill" button next to the process
2. Confirm the action in the dialog

**Note:** Terminating processes requires appropriate system permissions. Some system processes cannot be terminated.

### Settings

Click the "Settings" link in the navigation bar to configure:

- Refresh interval
- Memory and CPU thresholds for highlighting
- Alert settings

## API Documentation

The backend provides a RESTful API that can be used independently of the frontend. API documentation is available at:

```
http://localhost:8000/docs
```

### Key Endpoints

- `GET /api/processes` - Get current process list
- `POST /api/processes/kill` - Terminate a process
- `GET /api/processes/{pid}/history` - Get historical data for a process
- `GET /api/system/memory` - Get system memory information
- `GET /api/system/info` - Get system information
- `WebSocket /ws/processes` - Real-time process updates

## Logging

To enable process logging (for historical data):

1. Set the environment variable `ENABLE_LOGGING=true`
2. Configure storage type with `STORAGE_TYPE` (sqlite or csv)
3. Set retention policy with `RETENTION_DAYS` and `MAX_LOG_ROWS`

## Troubleshooting

### Common Issues

1. **Permission errors when killing processes**
   - Ensure you're running the application with sufficient privileges
   - Some system processes cannot be terminated

2. **High CPU usage by the monitor itself**
   - Increase the refresh interval in settings
   - Reduce the number of processes shown (use top N filter)

3. **WebSocket connection issues**
   - The application will automatically fall back to HTTP polling
   - Check for firewall or proxy issues

### Logs

Application logs can be found in the location specified by the `LOG_FILE` environment variable, or in the console output if not specified.