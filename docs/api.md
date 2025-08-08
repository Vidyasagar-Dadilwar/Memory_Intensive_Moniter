# Memory Intensive Monitor - API Documentation

## Overview

The Memory Intensive Monitor provides a RESTful API built with FastAPI. This document details all available endpoints, their parameters, and response formats.

## Base URL

By default, the API is available at: `http://localhost:8000`

## Authentication

Currently, the API does not require authentication when running locally. For remote access, consider implementing token-based authentication by setting the `API_TOKEN` environment variable.

## API Endpoints

### Root Endpoint

```
GET /
```

Returns basic information about the application.

**Response:**

```json
{
  "app": "Memory Intensive Monitor",
  "version": "1.0.0",
  "api_docs": "/docs"
}
```

### Process Management

#### Get Process List

```
GET /api/processes
```

Returns a list of running processes with their details.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| top | integer | Limit results to top N processes by memory usage |
| sort_by | string | Field to sort by (memory_percent, cpu_percent, pid, name) |
| min_mem_percent | float | Filter processes with memory usage above threshold |

**Response:**

```json
{
  "processes": [
    {
      "pid": 1234,
      "name": "chrome.exe",
      "username": "user",
      "status": "running",
      "memory_rss": 102400000,
      "memory_percent": 5.2,
      "cpu_percent": 2.1,
      "create_time": 1620000000.0
    },
    // More processes...
  ],
  "timestamp": 1620100000.0,
  "system_memory": {
    "total": 16000000000,
    "available": 8000000000,
    "percent": 50.0
  }
}
```

#### Kill Process

```
POST /api/processes/kill
```

Attempts to terminate a process by its PID.

**Request Body:**

```json
{
  "pid": 1234
}
```

**Response:**

```json
{
  "success": true,
  "message": "Process terminated successfully"
}
```

or if unsuccessful:

```json
{
  "success": false,
  "message": "Failed to terminate process: Permission denied"
}
```

#### Get Process History

```
GET /api/processes/{pid}/history
```

Returns historical data for a specific process if logging is enabled.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| pid | integer | Process ID |

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| limit | integer | Maximum number of records to return |
| hours | float | Get records from the last N hours |

**Response:**

```json
{
  "pid": 1234,
  "name": "chrome.exe",
  "history": [
    {
      "timestamp": 1620000000.0,
      "memory_rss": 102400000,
      "memory_percent": 5.2,
      "cpu_percent": 2.1
    },
    // More history points...
  ]
}
```

### System Information

#### Get System Memory

```
GET /api/system/memory
```

Returns detailed information about system memory usage.

**Response:**

```json
{
  "memory": {
    "total": 16000000000,
    "available": 8000000000,
    "used": 8000000000,
    "percent": 50.0
  },
  "swap": {
    "total": 8000000000,
    "used": 1000000000,
    "free": 7000000000,
    "percent": 12.5
  }
}
```

#### Get System Information

```
GET /api/system/info
```

Returns general system information.

**Response:**

```json
{
  "system": "Windows-10-10.0.19041-SP0",
  "processor": "Intel64 Family 6 Model 142 Stepping 10, GenuineIntel",
  "cpu_count": 8,
  "boot_time": 1620000000.0
}
```

### WebSocket

#### Real-time Process Updates

```
WebSocket /ws/processes
```

Provides real-time updates of process information.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| top | integer | Limit results to top N processes by memory usage |
| sort_by | string | Field to sort by (memory_percent, cpu_percent, pid, name) |
| min_mem_percent | float | Filter processes with memory usage above threshold |

**WebSocket Messages:**

The server sends JSON messages with the same format as the `GET /api/processes` endpoint.

## Error Handling

The API uses standard HTTP status codes to indicate success or failure:

- 200: Success
- 400: Bad Request (invalid parameters)
- 404: Not Found (resource not found)
- 422: Validation Error (invalid request body)
- 500: Internal Server Error

Error responses include a JSON body with details:

```json
{
  "detail": "Error message describing the issue"
}
```

## Rate Limiting

To prevent abuse, the API implements rate limiting. By default, clients are limited to 60 requests per minute. Exceeding this limit will result in a 429 Too Many Requests response.

## Environment Variables

The API behavior can be configured using the following environment variables:

| Variable | Description | Default |
|----------|-------------|--------|
| ENABLE_LOGGING | Enable process history logging | false |
| STORAGE_TYPE | Storage type for logging (sqlite or csv) | sqlite |
| STORAGE_PATH | Path to storage file | ./data |
| RETENTION_DAYS | Number of days to keep logs | 7 |
| MAX_LOG_ROWS | Maximum number of log rows to keep | 10000 |
| MONITOR_INTERVAL | Process monitoring interval in seconds | 2 |
| API_TOKEN | Token for API authentication (if enabled) | None |
| LOG_LEVEL | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |
| LOG_FILE | Path to log file | None (console) |