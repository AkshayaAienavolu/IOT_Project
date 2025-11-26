# Raspberry Pi Setup — Step-by-Step

This guide walks you through deploying the MQTT subscriber (`mqtt_logger.py`) on your Raspberry Pi to receive and log emotion events from the webapp.

---

## Prerequisites

- Raspberry Pi with Raspberry Pi OS (or similar Debian-based OS)
- Internet connection on the Pi
- HiveMQ Cloud cluster running (you already have the WSS endpoint and credentials)
- Git installed on the Pi (`sudo apt install git` if needed)

---

## Step 1: Connect to your Raspberry Pi

Use SSH or connect directly with keyboard/monitor.

```bash
ssh pi@<your-pi-ip-address>
# default password: raspberry (change it after first login for security)
```

---

## Step 2: Update system packages

```bash
sudo apt update
sudo apt upgrade -y
```

---

## Step 3: Install Python 3 and pip (if not already installed)

```bash
sudo apt install -y python3 python3-pip python3-venv
```

---

## Step 4: Clone or copy the repository to the Pi

**Option A: Clone from GitHub (recommended)**

```bash
cd ~
git clone https://github.com/AkshayaAienavolu/FER.git
cd FER
```

**Option B: Copy files manually**

If you prefer to copy only `mqtt_logger.py`, use `scp` from your laptop:

```powershell
# On your Windows machine (PowerShell):
scp C:\Users\18003\Iot_proj\mqtt_logger.py pi@<pi-ip>:~/mqtt_logger.py
```

Then on the Pi:
```bash
mkdir -p ~/FER
mv ~/mqtt_logger.py ~/FER/
cd ~/FER
```

---

## Step 5: Create a Python virtual environment

```bash
cd ~/FER
python3 -m venv venv-fer
source venv-fer/bin/activate
```

Your prompt should now show `(venv-fer)`.

---

## Step 6: Install dependencies

```bash
pip install --upgrade pip
pip install paho-mqtt
```

---

## Step 7: Create a Subscribe-only credential in HiveMQ Cloud

- Go to HiveMQ Cloud console → your cluster → Access Management.
- Click "Add Credentials" or create a new user.
- **Username**: e.g., `pi_subscriber`
- **Password**: choose a secure password (e.g., `PiSecure456`)
- **Permission**: Select **Subscribe Only**
- **Topic**: Restrict to `fer/events` if possible (recommended for security).
- Save the credentials.

---

## Step 8: Configure environment variables for `mqtt_logger.py`

Create a small script to set env vars and run the logger:

```bash
nano ~/FER/run_logger.sh
```

Paste the following (replace placeholders with your real values):

```bash
#!/bin/bash
export WSS_URL="wss://308c552d0a56494799306611ffacac19.s1.eu.hivemq.cloud:8883/mqtt"
export MQTT_USERNAME="pi_subscriber"
export MQTT_PASSWORD="PiSecure456"
export MQTT_TOPIC="fer/events"
export FER_DB="/home/pi/fer_events.db"

cd /home/pi/FER
source venv-fer/bin/activate
python3 mqtt_logger.py
```

Save and exit (Ctrl+O, Enter, Ctrl+X).

Make it executable:

```bash
chmod +x ~/FER/run_logger.sh
```

---

## Step 9: Test the logger manually

Run the logger in the foreground to verify it connects:

```bash
~/FER/run_logger.sh
```

You should see output like:

```
[2025-11-25 12:34:56] INFO: Connecting to 308c552d0a56494799306611ffacac19.s1.eu.hivemq.cloud:8883
[2025-11-25 12:34:57] INFO: Connected to MQTT broker
[2025-11-25 12:34:57] INFO: Subscribed to topic fer/events
```

Keep this running. Open your webapp (HTTPS) on a browser/mobile, start the camera, and watch for:

```
[2025-11-25 12:35:10] INFO: Logged event: user=fer_web_abc123 emotion=Happy
```

If you see that, the end-to-end flow is working! Press `Ctrl+C` to stop the logger.

---

## Step 10: Create a systemd service (run at boot)

Create the service file:

```bash
sudo nano /etc/systemd/system/fer-mqtt-logger.service
```

Paste the following (adjust paths/credentials as needed):

```ini
[Unit]
Description=FER MQTT Logger
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/FER
Environment="WSS_URL=wss://308c552d0a56494799306611ffacac19.s1.eu.hivemq.cloud:8883/mqtt"
Environment="MQTT_USERNAME=pi_subscriber"
Environment="MQTT_PASSWORD=PiSecure456"
Environment="MQTT_TOPIC=fer/events"
Environment="FER_DB=/home/pi/fer_events.db"
ExecStart=/home/pi/FER/venv-fer/bin/python /home/pi/FER/mqtt_logger.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Save and exit (Ctrl+O, Enter, Ctrl+X).

Reload systemd, enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable fer-mqtt-logger.service
sudo systemctl start fer-mqtt-logger.service
```

Check status:

```bash
sudo systemctl status fer-mqtt-logger.service
```

You should see `Active: active (running)`.

View live logs:

```bash
sudo journalctl -u fer-mqtt-logger -f
```

Press `Ctrl+C` to exit the log tail.

---

## Step 11: Verify database entries

Open the SQLite database to confirm events are being logged:

```bash
sqlite3 /home/pi/fer_events.db
```

In the sqlite prompt:

```sql
.mode column
.headers on
SELECT id, ts_received, user_id, emotion, confidence FROM events ORDER BY id DESC LIMIT 10;
.exit
```

You should see rows with `user_id`, `emotion`, and `confidence` values from the webapp.

---

## Step 12: Optional — Query and analyze events

Example queries:

```bash
# Count events by emotion
sqlite3 /home/pi/fer_events.db "SELECT emotion, COUNT(*) as count FROM events GROUP BY emotion ORDER BY count DESC;"

# Show last 20 events
sqlite3 /home/pi/fer_events.db "SELECT ts_received, user_id, emotion, confidence FROM events ORDER BY id DESC LIMIT 20;"

# Show events from a specific user
sqlite3 /home/pi/fer_events.db "SELECT * FROM events WHERE user_id='fer_web_abc123' ORDER BY id DESC LIMIT 10;"
```

---

## Troubleshooting

### Logger fails to connect

- Check internet connection on the Pi.
- Verify HiveMQ credentials (username/password) and permissions (Subscribe Only).
- Ensure the WSS URL is correct (check HiveMQ Cloud dashboard).
- Check firewall: outbound TLS (port 8883) should be allowed (usually default).

### No messages received but logger is connected

- Verify the browser webapp is publishing (check browser DevTools Console for "MQTT connected").
- Confirm both browser and Pi use the same topic (`fer/events`).
- Test with HiveMQ Cloud Web Client: subscribe to `fer/events` and see if messages appear when you run the webapp.

### Permission denied or TLS errors

- Update CA certificates on the Pi:
  ```bash
  sudo apt update
  sudo apt install --reinstall ca-certificates
  ```
- Check that `paho-mqtt` is installed in the venv (`pip list | grep paho`).

### Service fails to start

- Check logs:
  ```bash
  sudo journalctl -u fer-mqtt-logger -n 50
  ```
- Verify paths in the service file match your setup.
- Ensure the venv exists at `/home/pi/FER/venv-fer`.

---

## Next Steps

- Add downstream logic: modify `mqtt_logger.py` to trigger actions (GPIO, LED, send alerts) based on detected emotions.
- Scale: if you have multiple Pis, use different client IDs and separate DB files or a shared DB server.
- Security: rotate HiveMQ passwords periodically; use topic ACLs to restrict access.

---

**You're done!** The webapp publishes emotion events → HiveMQ Cloud → Raspberry Pi logs to SQLite.
