FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app ./app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LOG_LEVEL=INFO \
    MONITOR_INTERVAL_SECONDS=1.0 \
    DEFAULT_SORT=memory_percent \
    ENABLE_LOGGING=false \
    STORAGE_TYPE=sqlite \
    DB_PATH=/data/process_logs.db \
    CSV_DIR=/data/logs \
    RETENTION_DAYS=7 \
    MAX_LOG_ROWS=10000

# Create data directory for logs
RUN mkdir -p /data

# Expose the API port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]