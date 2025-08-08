@echo off
echo Memory Intensive Monitor - Production Mode
echo =======================================
echo.

:: Check if Docker is installed
docker --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Docker is not installed or not in PATH.
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

:: Check if Docker Compose is installed
docker-compose --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Docker Compose is not installed or not in PATH.
    echo Docker Compose should be included with Docker Desktop.
    echo.
    pause
    exit /b 1
)

echo Building and starting containers...
echo This may take a few minutes for the first run.
echo.

:: Build and start the containers
docker-compose up --build -d

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error: Failed to build and start containers.
    echo Please check the error messages above.
    echo.
    pause
    exit /b 1
)

echo.
echo Memory Intensive Monitor is now running in production mode!
echo.
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo To stop the application, run: docker-compose down
echo.

pause