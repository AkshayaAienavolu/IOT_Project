#!/bin/bash
# Complete IoT Health Monitoring System Startup Script

echo "🏥 Starting IoT Health Monitoring System"
echo "========================================"

# Activate virtual environment
source venv-fer/bin/activate

# Step 1: Generate mock sensor data for all existing users (one-time)
echo ""
echo "📊 Step 1: Generating sensor data for all users..."
python3 test_sensor_integration.py

# Step 2: Generate integrated dashboards
echo ""
echo "📈 Step 2: Generating integrated dashboards..."
python3 dashboard_integrated.py

# Step 3: Start auto sensor generator for new users (background)
echo ""
echo "🤖 Step 3: Starting auto sensor data generator..."
python3 auto_sensor_generator.py > logs/auto_sensor.log 2>&1 &
AUTO_SENSOR_PID=$!
echo "   ✓ Auto sensor generator started (PID: $AUTO_SENSOR_PID)"

# Step 4: Start dashboard server
echo ""
echo "🌐 Step 4: Starting dashboard server..."
echo "   Dashboard will auto-refresh every 2 minutes"
python3 dashboard_server.py

# Cleanup on exit
trap "echo 'Stopping services...'; kill $AUTO_SENSOR_PID 2>/dev/null; exit" SIGINT SIGTERM
