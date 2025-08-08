import psutil
import time
import logging
import asyncio
from typing import List, Dict, Any, Optional
import os
from datetime import datetime

logger = logging.getLogger("memory_monitor")

class ProcessMonitor:
    """Handles monitoring of system processes using psutil"""
    
    def __init__(self):
        self.processes: List[Dict[str, Any]] = []
        self.last_update: float = 0
        self.update_interval: float = float(os.getenv("MONITOR_INTERVAL_SECONDS", "1.0"))
        self.sort_by: str = os.getenv("DEFAULT_SORT", "memory_percent")
        self.sort_desc: bool = True
        self.initialized: bool = False
    
    async def initialize(self):
        """Initialize the process monitor"""
        if not self.initialized:
            logger.info("Initializing process monitor")
            # Initial update to populate process list
            await self.update()
            self.initialized = True
    
    async def shutdown(self):
        """Clean up resources"""
        logger.info("Shutting down process monitor")
        # No specific cleanup needed for psutil
        pass
    
    async def update(self) -> None:
        """Update the process list with current information"""
        try:
            current_time = time.time()
            
            # Skip if not enough time has passed since last update
            if current_time - self.last_update < self.update_interval and self.processes:
                return
            
            self.last_update = current_time
            processes = []
            
            # Iterate through all processes
            for proc in psutil.process_iter(['pid', 'name', 'username', 'status']):
                try:
                    # Get process info
                    proc_info = proc.info
                    
                    # Get memory info
                    with proc.oneshot():
                        memory_info = proc.memory_info()
                        memory_percent = proc.memory_percent()
                        cpu_percent = proc.cpu_percent(interval=None)  # Non-blocking
                        create_time = proc.create_time()
                    
                    # Format process data
                    process_data = {
                        'pid': proc_info['pid'],
                        'name': proc_info['name'],
                        'username': proc_info['username'] or 'unknown',
                        'status': proc_info['status'],
                        'memory_rss': memory_info.rss,  # In bytes
                        'memory_rss_mb': round(memory_info.rss / (1024 * 1024), 2),  # In MB
                        'memory_percent': round(memory_percent, 2),
                        'cpu_percent': round(cpu_percent, 2),
                        'create_time': create_time,
                        'start_time': datetime.fromtimestamp(create_time).strftime('%Y-%m-%d %H:%M:%S'),
                    }
                    
                    processes.append(process_data)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                    # Skip processes we can't access
                    continue
                except Exception as e:
                    logger.error(f"Error processing PID {proc.pid}: {str(e)}")
                    continue
            
            # Sort processes by the specified field
            processes.sort(
                key=lambda x: x.get(self.sort_by, 0), 
                reverse=self.sort_desc
            )
            
            self.processes = processes
            logger.debug(f"Updated process list: {len(processes)} processes")
            
        except Exception as e:
            logger.error(f"Error updating process list: {str(e)}")
    
    def get_snapshot(self, top: Optional[int] = None, 
                    sort_by: Optional[str] = None, 
                    min_mem_percent: Optional[float] = None) -> Dict[str, Any]:
        """Get a snapshot of current processes with optional filtering"""
        # Apply sorting if requested
        processes = self.processes
        
        if sort_by and sort_by != self.sort_by:
            processes = sorted(
                processes,
                key=lambda x: x.get(sort_by, 0),
                reverse=self.sort_desc
            )
        
        # Apply memory threshold filter if requested
        if min_mem_percent is not None:
            processes = [p for p in processes if p.get('memory_percent', 0) >= min_mem_percent]
        
        # Apply top N limit if requested
        if top is not None and top > 0:
            processes = processes[:top]
        
        # Create snapshot with metadata
        snapshot = {
            'timestamp': time.time(),
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_processes': len(self.processes),
            'filtered_processes': len(processes),
            'system_memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent,
            },
            'processes': processes
        }
        
        return snapshot
    
    async def kill_process(self, pid: int) -> Dict[str, Any]:
        """Attempt to terminate a process by PID"""
        try:
            process = psutil.Process(pid)
            process_name = process.name()
            
            # Terminate the process
            process.terminate()
            
            # Wait briefly to see if it terminates
            gone, alive = psutil.wait_procs([process], timeout=3)
            
            if process in alive:
                # Force kill if still alive
                process.kill()
                return {
                    'success': True,
                    'message': f"Process {pid} ({process_name}) forcefully killed"
                }
            else:
                return {
                    'success': True,
                    'message': f"Process {pid} ({process_name}) terminated successfully"
                }
                
        except psutil.NoSuchProcess:
            return {
                'success': False,
                'message': f"Process {pid} not found"
            }
        except psutil.AccessDenied:
            return {
                'success': False,
                'message': f"Access denied when trying to terminate process {pid}"
            }
        except Exception as e:
            logger.error(f"Error killing process {pid}: {str(e)}")
            return {
                'success': False,
                'message': f"Error: {str(e)}"
            }
    
    def set_sort_options(self, sort_by: str, desc: bool = True) -> None:
        """Set sorting options for process list"""
        valid_sort_fields = [
            'pid', 'name', 'username', 'memory_rss', 
            'memory_percent', 'cpu_percent', 'create_time'
        ]
        
        if sort_by in valid_sort_fields:
            self.sort_by = sort_by
            self.sort_desc = desc
        else:
            logger.warning(f"Invalid sort field: {sort_by}. Using default.")