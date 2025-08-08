import asyncio
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import logging

# Import local modules
from .monitor import ProcessMonitor
from .api import router as api_router
from .logger import setup_logger, ProcessLogger

# Setup logging
logger = logging.getLogger("memory_monitor")

# Create FastAPI app
app = FastAPI(
    title="Memory Intensive Monitor",
    description="A real-time process memory monitoring application",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify the actual origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")

# Process monitor instance
process_monitor = ProcessMonitor()

# Optional process logger
process_logger: Optional[ProcessLogger] = None

# Connected WebSocket clients
active_connections: List[WebSocket] = []


@app.on_event("startup")
async def startup_event():
    """Initialize components on application startup"""
    global process_logger
    
    # Setup application logger
    setup_logger()
    
    # Initialize process monitor
    await process_monitor.initialize()
    
    # Start the background monitoring task
    asyncio.create_task(background_monitor_task())
    
    # Initialize logger if enabled
    if os.getenv("ENABLE_LOGGING", "false").lower() == "true":
        from .logger import ProcessLogger
        process_logger = ProcessLogger()
        await process_logger.initialize()
        logger.info("Process logging enabled")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on application shutdown"""
    await process_monitor.shutdown()
    
    if process_logger:
        await process_logger.shutdown()


async def background_monitor_task():
    """Background task to update process information periodically"""
    while True:
        try:
            # Update process information
            await process_monitor.update()
            
            # Log data if enabled
            if process_logger:
                await process_logger.log_snapshot(process_monitor.get_snapshot())
            
            # Broadcast to WebSocket clients
            if active_connections:
                snapshot = process_monitor.get_snapshot()
                for connection in active_connections.copy():
                    try:
                        await connection.send_json(snapshot)
                    except Exception as e:
                        logger.error(f"Error sending data to WebSocket: {e}")
                        active_connections.remove(connection)
            
            # Sleep interval (configurable)
            interval = float(os.getenv("MONITOR_INTERVAL_SECONDS", "1.0"))
            await asyncio.sleep(interval)
            
        except Exception as e:
            logger.error(f"Error in background monitor task: {e}")
            await asyncio.sleep(5)  # Longer sleep on error


@app.websocket("/ws/processes")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time process updates"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Send initial data
        snapshot = process_monitor.get_snapshot()
        await websocket.send_json(snapshot)
        
        # Keep connection alive and handle client messages
        while True:
            # Wait for any client messages (like filter requests)
            data = await websocket.receive_text()
            # Process client messages if needed
            
    except WebSocketDisconnect:
        logger.debug("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "app": "Memory Intensive Monitor",
        "version": "0.1.0",
        "api_docs": "/docs",
        "endpoints": {
            "processes": "/api/processes",
            "websocket": "/ws/processes"
        }
    }