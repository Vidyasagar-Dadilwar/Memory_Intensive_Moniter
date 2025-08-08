import os
import logging
import json
import time
from datetime import datetime
import asyncio
from typing import List, Dict, Any, Optional, Union
import aiosqlite
import csv
from pathlib import Path

# Setup application logger
def setup_logger():
    """Configure the application logger"""
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format
    )
    
    # Create logger
    logger = logging.getLogger("memory_monitor")
    logger.setLevel(getattr(logging, log_level))
    
    # Add file handler if LOG_FILE is specified
    log_file = os.getenv("LOG_FILE")
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(file_handler)
    
    return logger


class ProcessLogger:
    """Handles logging of process data to SQLite or CSV"""
    
    def __init__(self):
        self.logger = logging.getLogger("memory_monitor")
        self.storage_type = os.getenv("STORAGE_TYPE", "sqlite").lower()  # "sqlite" or "csv"
        self.db_path = os.getenv("DB_PATH", "process_logs.db")
        self.csv_dir = os.getenv("CSV_DIR", "logs")
        self.retention_days = int(os.getenv("RETENTION_DAYS", "7"))
        self.max_rows = int(os.getenv("MAX_LOG_ROWS", "10000"))
        self.db_connection = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize the logger based on storage type"""
        if self.initialized:
            return
        
        if self.storage_type == "sqlite":
            await self._init_sqlite()
        elif self.storage_type == "csv":
            await self._init_csv()
        else:
            self.logger.error(f"Unsupported storage type: {self.storage_type}")
            raise ValueError(f"Unsupported storage type: {self.storage_type}")
        
        self.initialized = True
        self.logger.info(f"Process logger initialized with {self.storage_type} storage")
        
        # Start retention task
        asyncio.create_task(self._retention_task())
    
    async def _init_sqlite(self):
        """Initialize SQLite database"""
        # Create database connection
        self.db_connection = await aiosqlite.connect(self.db_path)
        
        # Create tables if they don't exist
        await self.db_connection.execute("""
            CREATE TABLE IF NOT EXISTS process_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                datetime TEXT NOT NULL,
                pid INTEGER NOT NULL,
                name TEXT NOT NULL,
                username TEXT,
                status TEXT,
                memory_rss INTEGER,
                memory_percent REAL,
                cpu_percent REAL
            )
        """)
        
        await self.db_connection.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                datetime TEXT NOT NULL,
                event_type TEXT NOT NULL,
                data TEXT NOT NULL
            )
        """)
        
        await self.db_connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_process_snapshots_pid 
            ON process_snapshots(pid)
        """)
        
        await self.db_connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_process_snapshots_timestamp 
            ON process_snapshots(timestamp)
        """)
        
        await self.db_connection.commit()
    
    async def _init_csv(self):
        """Initialize CSV storage"""
        # Create directory if it doesn't exist
        csv_path = Path(self.csv_dir)
        csv_path.mkdir(parents=True, exist_ok=True)
        
        # Create snapshots file if it doesn't exist
        snapshots_file = csv_path / "process_snapshots.csv"
        if not snapshots_file.exists():
            with open(snapshots_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'datetime', 'pid', 'name', 'username',
                    'status', 'memory_rss', 'memory_percent', 'cpu_percent'
                ])
        
        # Create events file if it doesn't exist
        events_file = csv_path / "events.csv"
        if not events_file.exists():
            with open(events_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'datetime', 'event_type', 'data'])
    
    async def shutdown(self):
        """Clean up resources"""
        if self.storage_type == "sqlite" and self.db_connection:
            await self.db_connection.close()
            self.db_connection = None
        
        self.initialized = False
        self.logger.info("Process logger shut down")
    
    async def log_snapshot(self, snapshot: Dict[str, Any]):
        """Log a process snapshot"""
        if not self.initialized:
            await self.initialize()
        
        timestamp = snapshot.get('timestamp', time.time())
        datetime_str = snapshot.get('datetime', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        try:
            if self.storage_type == "sqlite":
                await self._log_snapshot_sqlite(snapshot, timestamp, datetime_str)
            elif self.storage_type == "csv":
                await self._log_snapshot_csv(snapshot, timestamp, datetime_str)
        except Exception as e:
            self.logger.error(f"Error logging snapshot: {e}")
    
    async def _log_snapshot_sqlite(self, snapshot: Dict[str, Any], timestamp: float, datetime_str: str):
        """Log snapshot to SQLite"""
        if not self.db_connection:
            return
        
        # Insert each process as a separate row
        for process in snapshot.get('processes', []):
            await self.db_connection.execute("""
                INSERT INTO process_snapshots (
                    timestamp, datetime, pid, name, username, status,
                    memory_rss, memory_percent, cpu_percent
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp,
                datetime_str,
                process.get('pid'),
                process.get('name'),
                process.get('username'),
                process.get('status'),
                process.get('memory_rss'),
                process.get('memory_percent'),
                process.get('cpu_percent')
            ))
        
        await self.db_connection.commit()
    
    async def _log_snapshot_csv(self, snapshot: Dict[str, Any], timestamp: float, datetime_str: str):
        """Log snapshot to CSV"""
        csv_path = Path(self.csv_dir) / "process_snapshots.csv"
        
        # Use asyncio to run file operations in a thread pool
        def write_to_csv():
            with open(csv_path, 'a', newline='') as f:
                writer = csv.writer(f)
                for process in snapshot.get('processes', []):
                    writer.writerow([
                        timestamp,
                        datetime_str,
                        process.get('pid'),
                        process.get('name'),
                        process.get('username'),
                        process.get('status'),
                        process.get('memory_rss'),
                        process.get('memory_percent'),
                        process.get('cpu_percent')
                    ])
        
        await asyncio.to_thread(write_to_csv)
    
    async def log_event(self, event_type: str, data: Dict[str, Any]):
        """Log an event"""
        if not self.initialized:
            await self.initialize()
        
        timestamp = time.time()
        datetime_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data_json = json.dumps(data)
        
        try:
            if self.storage_type == "sqlite":
                await self._log_event_sqlite(event_type, data_json, timestamp, datetime_str)
            elif self.storage_type == "csv":
                await self._log_event_csv(event_type, data_json, timestamp, datetime_str)
        except Exception as e:
            self.logger.error(f"Error logging event: {e}")
    
    async def _log_event_sqlite(self, event_type: str, data_json: str, timestamp: float, datetime_str: str):
        """Log event to SQLite"""
        if not self.db_connection:
            return
        
        await self.db_connection.execute("""
            INSERT INTO events (timestamp, datetime, event_type, data)
            VALUES (?, ?, ?, ?)
        """, (timestamp, datetime_str, event_type, data_json))
        
        await self.db_connection.commit()
    
    async def _log_event_csv(self, event_type: str, data_json: str, timestamp: float, datetime_str: str):
        """Log event to CSV"""
        csv_path = Path(self.csv_dir) / "events.csv"
        
        # Use asyncio to run file operations in a thread pool
        def write_to_csv():
            with open(csv_path, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, datetime_str, event_type, data_json])
        
        await asyncio.to_thread(write_to_csv)
    
    async def get_process_history(self, pid: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Get historical data for a specific process"""
        if not self.initialized:
            await self.initialize()
        
        if self.storage_type == "sqlite":
            return await self._get_process_history_sqlite(pid, limit)
        elif self.storage_type == "csv":
            return await self._get_process_history_csv(pid, limit)
        
        return []
    
    async def _get_process_history_sqlite(self, pid: int, limit: int) -> List[Dict[str, Any]]:
        """Get process history from SQLite"""
        if not self.db_connection:
            return []
        
        async with self.db_connection.execute("""
            SELECT timestamp, datetime, pid, name, username, status,
                   memory_rss, memory_percent, cpu_percent
            FROM process_snapshots
            WHERE pid = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (pid, limit)) as cursor:
            rows = await cursor.fetchall()
        
        result = []
        for row in rows:
            result.append({
                'timestamp': row[0],
                'datetime': row[1],
                'pid': row[2],
                'name': row[3],
                'username': row[4],
                'status': row[5],
                'memory_rss': row[6],
                'memory_rss_mb': round(row[6] / (1024 * 1024), 2) if row[6] else None,
                'memory_percent': row[7],
                'cpu_percent': row[8]
            })
        
        return result
    
    async def _get_process_history_csv(self, pid: int, limit: int) -> List[Dict[str, Any]]:
        """Get process history from CSV"""
        csv_path = Path(self.csv_dir) / "process_snapshots.csv"
        if not csv_path.exists():
            return []
        
        # Use asyncio to run file operations in a thread pool
        def read_from_csv():
            result = []
            with open(csv_path, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if int(row['pid']) == pid:
                        result.append({
                            'timestamp': float(row['timestamp']),
                            'datetime': row['datetime'],
                            'pid': int(row['pid']),
                            'name': row['name'],
                            'username': row['username'],
                            'status': row['status'],
                            'memory_rss': int(row['memory_rss']) if row['memory_rss'] else None,
                            'memory_rss_mb': round(int(row['memory_rss']) / (1024 * 1024), 2) if row['memory_rss'] else None,
                            'memory_percent': float(row['memory_percent']) if row['memory_percent'] else None,
                            'cpu_percent': float(row['cpu_percent']) if row['cpu_percent'] else None
                        })
                        if len(result) >= limit:
                            break
            
            # Sort by timestamp in descending order
            result.sort(key=lambda x: x['timestamp'], reverse=True)
            return result[:limit]
        
        return await asyncio.to_thread(read_from_csv)
    
    async def _retention_task(self):
        """Background task to enforce data retention policy"""
        while True:
            try:
                if self.storage_type == "sqlite":
                    await self._enforce_sqlite_retention()
                elif self.storage_type == "csv":
                    await self._enforce_csv_retention()
            except Exception as e:
                self.logger.error(f"Error in retention task: {e}")
            
            # Run once a day
            await asyncio.sleep(24 * 60 * 60)
    
    async def _enforce_sqlite_retention(self):
        """Enforce retention policy for SQLite storage"""
        if not self.db_connection:
            return
        
        # Delete old data based on retention days
        retention_timestamp = time.time() - (self.retention_days * 24 * 60 * 60)
        
        await self.db_connection.execute("""
            DELETE FROM process_snapshots
            WHERE timestamp < ?
        """, (retention_timestamp,))
        
        await self.db_connection.execute("""
            DELETE FROM events
            WHERE timestamp < ?
        """, (retention_timestamp,))
        
        # Enforce maximum row count
        await self.db_connection.execute("""
            DELETE FROM process_snapshots
            WHERE id NOT IN (
                SELECT id FROM process_snapshots
                ORDER BY timestamp DESC
                LIMIT ?
            )
        """, (self.max_rows,))
        
        await self.db_connection.commit()
        
        # Vacuum database to reclaim space
        await self.db_connection.execute("VACUUM")
        await self.db_connection.commit()
    
    async def _enforce_csv_retention(self):
        """Enforce retention policy for CSV storage"""
        # This is more complex for CSV as we need to read, filter, and rewrite
        # For simplicity, we'll implement a basic version that creates a new file
        
        snapshots_path = Path(self.csv_dir) / "process_snapshots.csv"
        events_path = Path(self.csv_dir) / "events.csv"
        
        retention_timestamp = time.time() - (self.retention_days * 24 * 60 * 60)
        
        # Process snapshots file
        if snapshots_path.exists():
            await self._filter_csv_file(snapshots_path, 'timestamp', retention_timestamp)
        
        # Process events file
        if events_path.exists():
            await self._filter_csv_file(events_path, 'timestamp', retention_timestamp)
    
    async def _filter_csv_file(self, file_path: Path, timestamp_field: str, min_timestamp: float):
        """Filter a CSV file to remove old records"""
        temp_path = file_path.with_suffix('.tmp')
        
        def filter_file():
            rows = []
            header = None
            
            # Read all rows that meet retention criteria
            with open(file_path, 'r', newline='') as f:
                reader = csv.reader(f)
                header = next(reader)  # Get header row
                timestamp_index = header.index(timestamp_field)
                
                for row in reader:
                    if float(row[timestamp_index]) >= min_timestamp:
                        rows.append(row)
            
            # Keep only the most recent max_rows
            rows.sort(key=lambda x: float(x[timestamp_index]), reverse=True)
            rows = rows[:self.max_rows]
            
            # Write filtered data back
            with open(temp_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(rows)
            
            # Replace original file
            temp_path.replace(file_path)
        
        await asyncio.to_thread(filter_file)