#!/bin/bash
# Start the Smart Parking Management System Web Application

echo "=========================================="
echo "Smart Parking Management System"
echo "Web Application Launcher"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "Virtual environment created."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing/updating dependencies..."
pip install -r requirements.txt -q

echo ""
echo "=========================================="
echo "Starting web server..."
echo "=========================================="
echo ""
echo "Access the dashboard at: http://localhost:5000"
echo "Press CTRL+C to stop the server"
echo ""

# Start the Flask application
python web_app.py
