@echo off
REM Start the Smart Parking Management System Web Application

echo ==========================================
echo Smart Parking Management System
echo Web Application Launcher
echo ==========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    echo Virtual environment created.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Installing/updating dependencies...
pip install -r requirements.txt -q

echo.
echo ==========================================
echo Starting web server...
echo ==========================================
echo.
echo Access the dashboard at: http://localhost:5000
echo Press CTRL+C to stop the server
echo.

REM Start the Flask application
python web_app.py
