from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging

# Import the process monitor
from .monitor import ProcessMonitor

# Setup logger
logger = logging.getLogger("memory_monitor")

# Create router
router = APIRouter()

# Get process monitor instance
def get_process_monitor():
    from .main import process_monitor
    return process_monitor

# Get process logger instance (if enabled)
def get_process_logger():
    from .main import process_logger
    return process_logger


# Models
class ProcessKillRequest(BaseModel):
    pid: int = Field(..., description="Process ID to terminate")
    force: bool = Field(False, description="Force kill if termination fails")


class ProcessKillResponse(BaseModel):
    success: bool
    message: str


# Endpoints
@router.get("/processes", response_model=Dict[str, Any])
async def get_processes(
    top: Optional[int] = Query(None, description="Limit to top N processes"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    min_mem_percent: Optional[float] = Query(None, description="Minimum memory percentage"),
    monitor: ProcessMonitor = Depends(get_process_monitor)
):
    """Get current process snapshot with optional filtering"""
    # Ensure monitor is up to date
    await monitor.update()
    
    # Get filtered snapshot
    return monitor.get_snapshot(top, sort_by, min_mem_percent)


@router.post("/processes/kill", response_model=ProcessKillResponse)
async def kill_process(
    request: ProcessKillRequest,
    monitor: ProcessMonitor = Depends(get_process_monitor),
    background_tasks: BackgroundTasks = None
):
    """Terminate a process by PID"""
    logger.info(f"Request to kill process {request.pid}")
    
    # Attempt to kill the process
    result = await monitor.kill_process(request.pid)
    
    # Log the kill attempt
    if background_tasks and get_process_logger():
        background_tasks.add_task(
            get_process_logger().log_event,
            "process_kill",
            {"pid": request.pid, "success": result["success"], "message": result["message"]}
        )
    
    return result


@router.get("/processes/{pid}/history", response_model=List[Dict[str, Any]])
async def get_process_history(
    pid: int,
    limit: int = Query(100, description="Maximum number of history records to return"),
    logger = Depends(get_process_logger)
):
    """Get historical data for a specific process if logging is enabled"""
    if not logger:
        raise HTTPException(status_code=404, detail="Process logging is not enabled")
    
    history = await logger.get_process_history(pid, limit)
    return history


@router.get("/system/memory", response_model=Dict[str, Any])
async def get_system_memory(
    monitor: ProcessMonitor = Depends(get_process_monitor)
):
    """Get system memory information"""
    import psutil
    
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    return {
        "memory": {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "free": memory.free,
            "percent": memory.percent
        },
        "swap": {
            "total": swap.total,
            "used": swap.used,
            "free": swap.free,
            "percent": swap.percent
        }
    }


@router.get("/system/info", response_model=Dict[str, Any])
async def get_system_info():
    """Get general system information"""
    import psutil
    import platform
    import socket
    
    return {
        "system": platform.system(),
        "node": platform.node(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "hostname": socket.gethostname(),
        "ip_address": socket.gethostbyname(socket.gethostname()),
        "cpu_count": psutil.cpu_count(logical=True),
        "cpu_physical": psutil.cpu_count(logical=False),
        "boot_time": psutil.boot_time()
    }