# Dashboard & Sensor Integration Guide

## Part 1: Generate Emotion Dashboards

### On Raspberry Pi:

1. **Install dependencies:**
```bash
cd ~/IOT_Project
source venv-fer/bin/activate
pip install matplotlib numpy
```

2. **Copy dashboard.py to Pi** (if not already there via git pull):
```bash
git pull origin main
```

3. **Run dashboard generator:**
```bash
python dashboard.py /home/pi/fer_events.db
```

This creates 4 PNG charts:
- `emotion_distribution.png` - Bar chart of emotion counts
- `emotion_timeline.png` - Emotions over time
- `confidence_timeline.png` - Model confidence trends
- `user_activity.png` - Events per user

4. **View charts:**
- Copy to your laptop: `scp pi@<pi-ip>:~/IOT_Project/*.png .`
- Or open directly on Pi if you have GUI

---

## Part 2: Pulse Oximeter Integration Plan

### Hardware Setup:
- **Sensor**: MAX30100/MAX30102 pulse oximeter module
- **Connection**: I2C to Raspberry Pi GPIO (SDA to GPIO2, SCL to GPIO3)
- **Power**: 3.3V from Pi

### Software Steps:

#### 1. Enable I2C on Pi:
```bash
sudo raspi-config
# Interface Options → I2C → Enable
sudo reboot
```

#### 2. Install sensor library:
```bash
pip install max30102
# or for MAX30100:
pip install max30100
```

#### 3. Create sensor reader script (`sensor_publisher.py`):
- Reads SpO2 and heart rate every 5 seconds
- Publishes to MQTT topic `fer/sensors`

#### 4. Update database schema:
Add `sensor_readings` table with columns:
- id, ts, user_id, spo2, heart_rate, temperature

#### 5. Update `mqtt_logger.py`:
- Subscribe to both `fer/events` and `fer/sensors`
- Log sensor data to new table

#### 6. Create combined dashboard:
- Correlation: emotion vs heart rate
- Time-series: vitals + emotion together
- Alerts: abnormal readings

---

## Next Steps:

**For dashboards now:**
1. Run `dashboard.py` on Pi to generate charts
2. Review the visualizations

**For sensor integration:**
1. Acquire MAX30102 sensor module
2. Wire to Pi GPIO
3. I'll create the sensor publisher script
4. Update database schema
5. Build combined dashboard

Would you like me to:
- A) Create a web dashboard (Streamlit) so you can view charts in browser?
- B) Create the pulse oximeter integration scripts now (sensor_publisher.py)?
- C) Both?
