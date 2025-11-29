# Web Dashboard Setup Guide

This guide explains how to set up and access the web-based dashboard to view emotion analysis charts in your browser.

## Overview

The web dashboard consists of:
- **Flask Server** (`dashboard_server.py`) - Runs on Raspberry Pi to serve charts
- **User Selection Page** - Shows all users with their stats
- **Individual User Dashboards** - Displays 4 charts per user + summary

## Setup on Raspberry Pi

### 1. Install Flask

```bash
cd /home/pi/IOT_Project
source fer_env/bin/activate  # Activate virtual environment
pip3 install flask
```

### 2. Make Startup Script Executable

```bash
chmod +x run_dashboard_server.sh
```

### 3. Start the Dashboard Server

```bash
./run_dashboard_server.sh
```

Or run directly:

```bash
export FER_DB="/home/pi/fer_events.db"
python3 dashboard_server.py
```

The server will start on port **5000** and display the access URL.

## Accessing the Dashboard

### Find Your Raspberry Pi IP Address

```bash
hostname -I
```

Example output: `192.168.1.100`

### Open in Browser

From any device on the same network:

```
http://192.168.1.100:5000
```

Replace `192.168.1.100` with your actual Pi IP address.

## Using the Dashboard

### Main Page (User Selection)

- **User Cards**: Click any user card to view their dashboard
- **Refresh Users**: Updates the user list from database
- **Regenerate Dashboards**: Re-creates all PNG charts from latest data

### User Dashboard Page

Each user gets:
- **Emotion Distribution** - Bar chart showing emotion counts with colors
- **Timeline** - Scatter plot of emotions over time
- **Confidence Trends** - Line chart of confidence scores
- **Hourly Activity** - Bar chart showing activity by hour (0-23)
- **Text Summary** - Statistics and insights

## Auto-Start on Boot (Optional)

To start the dashboard server automatically when Pi boots:

### Create Systemd Service

```bash
sudo nano /etc/systemd/system/dashboard.service
```

Add this content:

```ini
[Unit]
Description=Emotion Dashboard Web Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/IOT_Project
Environment="FER_DB=/home/pi/fer_events.db"
ExecStart=/home/pi/IOT_Project/fer_env/bin/python3 /home/pi/IOT_Project/dashboard_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable dashboard.service
sudo systemctl start dashboard.service
```

### Check Status

```bash
sudo systemctl status dashboard.service
```

### View Logs

```bash
sudo journalctl -u dashboard.service -f
```

## Running Both Services

You can run both the MQTT logger and dashboard server simultaneously:

**Terminal 1 - MQTT Logger:**
```bash
./run_logger.sh
```

**Terminal 2 - Dashboard Server:**
```bash
./run_dashboard_server.sh
```

Or use systemd to run both as services (see above).

## Troubleshooting

### Can't Access Dashboard from Other Devices

**Check firewall:**
```bash
sudo ufw allow 5000/tcp
```

**Check if server is running:**
```bash
ps aux | grep dashboard_server
```

### No Charts Displayed

1. Click **"Regenerate Dashboards"** button on main page
2. Wait ~30 seconds for charts to generate
3. Refresh the user dashboard page

### Port Already in Use

Change port in `dashboard_server.py`:
```python
app.run(host='0.0.0.0', port=8080, debug=False)  # Use 8080 instead
```

Then access at: `http://<pi-ip>:8080`

## API Endpoints

The server provides these endpoints:

- `GET /` - Main user selection page
- `GET /user/<user_id>` - Individual user dashboard
- `GET /api/users` - JSON list of all users
- `POST /api/regenerate` - Regenerate all charts
- `GET /dashboards/<path>` - Serve PNG chart files

## Mobile Access

The dashboard is mobile-responsive. Access from your phone browser:

```
http://<raspberry-pi-ip>:5000
```

Make sure your phone is on the same WiFi network as the Pi.

## Security Notes

This is a **local network server** for development/personal use:

- No authentication/authorization
- Anyone on your network can access it
- Don't expose port 5000 to the internet without adding security

For production use, consider:
- Adding password authentication
- Using HTTPS with SSL certificates
- Setting up a reverse proxy (nginx)

## Next Steps

- Set up automatic dashboard regeneration (cron job)
- Add pulse oximeter sensor data to dashboards
- Create combined emotion + vitals visualizations
