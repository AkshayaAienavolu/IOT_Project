#!/bin/bash

# MQTT Logger Startup Script for Raspberry Pi

# Navigate to the directory where this script is located
cd "$(dirname "$0")"

# Activate virtual environment
if [ -d "venv-fer" ]; then
    source venv-fer/bin/activate
fi

echo "==================================="
echo "Starting MQTT Logger..."
echo "==================================="

# Stop any existing instance
pkill -f mqtt_logger.py

# Start the logger in the background
nohup python3 mqtt_logger.py > logger.log 2>&1 &

echo "Logger started! (PID $!)"
echo "Logs are being written to: $(pwd)/logger.log"
echo "To view logs, run: tail -f logger.log"
