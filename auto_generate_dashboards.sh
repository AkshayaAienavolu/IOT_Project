#!/bin/bash
# Auto-generate dashboard charts for all users
# Run this with cron every 5 minutes

cd /home/pi/IOT_Project
source venv-fer/bin/activate

# Generate charts
python3 dashboard_per_user.py /home/pi/fer_events.db >> /home/pi/dashboard_cron.log 2>&1

echo "Charts regenerated at $(date)" >> /home/pi/dashboard_cron.log
