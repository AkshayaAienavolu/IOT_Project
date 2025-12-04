#!/bin/bash

# Dashboard Server Startup Script for Raspberry Pi

# Set database path (default to local fer_events.db in project dir)
# If running from IOT_Project, use that. Otherwise fallback to home.
if [ -f "/home/pi/IOT_Project/fer_events.db" ]; then
    export FER_DB="/home/pi/IOT_Project/fer_events.db"
else
    export FER_DB="${FER_DB:-/home/pi/fer_events.db}"
fi

# Activate virtual environment if exists
if [ -d "/home/pi/IOT_Project/fer_env" ]; then
    source /home/pi/IOT_Project/fer_env/bin/activate
fi

# Navigate to project directory
cd /home/pi/IOT_Project

# Install Flask if not already installed
pip3 install flask >/dev/null 2>&1

echo "==================================="
echo "Starting Dashboard Server"
echo "==================================="
echo "Database: $FER_DB"
echo "Server will be available at:"
echo "  http://$(hostname -I | awk '{print $1}'):5000"
echo "==================================="

# Run the dashboard server
python3 dashboard_server.py
