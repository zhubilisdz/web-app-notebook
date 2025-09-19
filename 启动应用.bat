@echo off
chcp 936
echo ========================================
echo    Stitch Notebook - Startup Script
echo ========================================
echo.
echo Starting application...
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Node.js not detected, please install Node.js first
    echo Download: https://nodejs.org/
    pause
    exit /b 1
)

REM Check if Python is installed
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not detected, please install Python first
    echo Download: https://www.python.org/
    pause
    exit /b 1
)

echo Environment check passed
echo.

REM Start backend service
echo Starting backend service...
cd /d "%~dp0backend"
start "Backend Service" cmd /k "py app.py"

REM Wait for backend to start
echo Waiting for backend service to start...
timeout /t 3 /nobreak >nul

REM Start frontend service
echo Starting frontend service...
cd /d "%~dp0frontend"
start "Frontend Service" cmd /k "npm run dev"

echo.
echo Application started successfully!
echo.
echo Access URLs:
echo    Frontend: http://localhost:5173
echo    Backend: http://localhost:5000
echo.
echo Tips:
echo    - Frontend and backend services run in new windows
echo    - Close the corresponding window to stop services
echo    - Check if ports are occupied if you encounter issues
echo.
echo Press any key to exit...
pause >nul