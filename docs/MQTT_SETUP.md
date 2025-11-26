# MQTT Integration & Raspberry Pi Subscriber

This document explains how to wire the browser webapp to HiveMQ Cloud and run the Pi-side subscriber that logs emotion events to SQLite.

Steps (summary):

- Copy `webapp/mqtt_config.example.js` → `webapp/mqtt_config.js` and fill the values from HiveMQ Cloud (WSS URL, username, password).
- Deploy `mqtt_config.js` locally (do not commit) and open the Netlify-provided HTTPS site. The webapp will auto-connect to the broker.
- On the Raspberry Pi, install Python dependencies and place `mqtt_logger.py` on the Pi. Configure env vars or set the constants inside the file.
- Create a systemd unit to run `mqtt_logger.py` at boot (example included below).

---

1) Browser: prepare credentials

- Copy the example config:

```powershell
cd webapp
cp mqtt_config.example.js mqtt_config.js
# (Windows: use copy mqtt_config.example.js mqtt_config.js)
```

- Edit `mqtt_config.js` and paste the WSS URL, username and password from HiveMQ Cloud.

2) Verify connect in browser

- Open the Netlify site (HTTPS). In DevTools Console you should see "MQTT connected to ..." if connection succeeded.

3) Raspberry Pi: quick install

On the Pi:

```bash
# create a virtualenv (optional)
python3 -m venv ~/venv-fer
source ~/venv-fer/bin/activate
pip install --upgrade pip
pip install paho-mqtt
```

Copy `mqtt_logger.py` to the Pi (scp or git pull) and then create a small env file or export variables before running. Example env variables:

```bash
export WSS_URL="wss://<cluster-host>:8883/mqtt"
export MQTT_USERNAME="your-username"
export MQTT_PASSWORD="your-password"
export MQTT_TOPIC="fer/events"
export FER_DB=/home/pi/fer_events.db
python mqtt_logger.py
```

4) systemd unit (example)

Create `/etc/systemd/system/fer-mqtt-logger.service` with contents:

```ini
[Unit]
Description=FER MQTT Logger
After=network.target

[Service]
Type=simple
Environment="WSS_URL=wss://<cluster-host>:8883/mqtt"
Environment="MQTT_USERNAME=..."
Environment="MQTT_PASSWORD=..."
Environment="MQTT_TOPIC=fer/events"
Environment="FER_DB=/home/pi/fer_events.db"
WorkingDirectory=/home/pi/fer-project
ExecStart=/usr/bin/python3 /home/pi/fer-project/mqtt_logger.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Then enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable fer-mqtt-logger.service
sudo systemctl start fer-mqtt-logger.service
sudo journalctl -u fer-mqtt-logger -f
```

5) Troubleshooting

- If connection fails, check the browser console for TLS or CORS-related errors. HiveMQ Cloud WSS endpoints use a valid CA; the browser should accept them.
- On Pi, check `journalctl -u fer-mqtt-logger` for errors. Ensure `paho-mqtt` is installed and that the environment variables are correct.
