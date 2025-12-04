# Integrated Health Monitoring System
## Facial Emotion + MAX30100 Sensor Integration

This system combines facial emotion recognition with physiological sensor data (heart rate, SpO2) to provide comprehensive mental-state monitoring.

## 🔧 Hardware Setup (Raspberry Pi)

### MAX30100 Sensor Connection
```
MAX30100 Pin  →  Raspberry Pi Pin
────────────────────────────────
VIN           →  3.3V (Pin 1)
GND           →  GND (Pin 6)
SCL           →  GPIO 3 / SCL (Pin 5)
SDA           →  GPIO 2 / SDA (Pin 3)
```

### Enable I2C on Raspberry Pi
```bash
sudo raspi-config
# Select: Interface Options → I2C → Enable
sudo reboot
```

### Verify I2C Connection
```bash
sudo i2cdetect -y 1
# You should see device at address 0x57
```

## 📦 Installation

### On Raspberry Pi
```bash
cd IOT_Project

# Install MAX30100 library
sudo pip3 install max30100

# Create sensor data table
python3 create_sensor_table.py
```

## 🚀 Running the System

### Option 1: With Real MAX30100 Sensor

```bash
# Terminal 1: Start emotion logger (already running)
python3 mqtt_logger.py

# Terminal 2: Start sensor logger
python3 sensor_logger.py your_user_id

# Terminal 3: Start dashboard server
python3 dashboard_server.py
```

### Option 2: Testing with Simulated Data

```bash
# Generate test sensor data matched with existing emotions
python3 test_sensor_integration.py

# Generate integrated dashboards
python3 dashboard_integrated.py

# Start dashboard server
python3 dashboard_server.py
```

## 📊 Dashboard Files Generated

Each user gets:
1. **Text Report** (`summary.txt`):
   - Integrated Mental-State Assessment
   - Physiological Metrics (HR, SpO2)
   - Emotion Distribution
   - Context-aware Wellbeing Suggestions

2. **Charts** (PNG files):
   - `integrated_timeline.png` - Heart rate + emotions over time
   - `hr_by_emotion.png` - Heart rate distribution by emotion
   - `spo2_timeline.png` - Blood oxygen levels over time

## 🌐 Accessing Dashboards

### Via Web Browser
```
http://10.221.24.195:5000/user/<your_user_id>
```

Or from Netlify camera app → Click "My Dashboard"

## 📝 How It Works

### 1. Data Collection
- **Emotion Data**: Collected from browser camera (TensorFlow.js)
- **Sensor Data**: Collected from MAX30100 sensor on Raspberry Pi
- Both stored in `fer_events.db` with timestamps

### 2. Data Matching
- System matches emotion records with sensor readings
- Tolerance: ±30 seconds timestamp difference
- Creates paired data points: (emotion, heart_rate, spo2, timestamp)

### 3. Mental-State Analysis
Combines both data sources:
- **Excellent**: Positive emotions + healthy vitals
- **Good**: Balanced emotions + stable vitals
- **Stressed**: Negative emotions + elevated heart rate
- **Physiological Alert**: Abnormal vitals regardless of emotion
- **Low Mood**: Predominant sadness
- **Moderate**: Mixed state

### 4. Wellbeing Suggestions
Context-aware tips based on:
- Dominant emotion patterns
- Physiological stress indicators (HR > 90, SpO2 < 95)
- Survey data from peers
- Temporal patterns

## 🔄 Automated Dashboard Generation

### Using cron (runs every 5 minutes)
```bash
crontab -e

# Add this line:
*/5 * * * * cd /home/pi/IOT_Project && python3 dashboard_integrated.py >> logs/dashboard.log 2>&1
```

## 📱 MQTT Topics

- `fer/events` - Emotion data from browsers
- `sensor/health` - Sensor data from Raspberry Pi

## 🗄️ Database Schema

### `events` table (existing)
- user_id, emotion, confidence, ts_received, bbox

### `sensor_data` table (new)
- id, user_id, heart_rate, spo2, timestamp

## 🧪 Testing

### 1. Test with simulated data:
```bash
python3 test_sensor_integration.py
python3 dashboard_integrated.py
```

### 2. Check database:
```bash
sqlite3 fer_events.db
SELECT COUNT(*) FROM sensor_data;
SELECT * FROM sensor_data LIMIT 5;
```

### 3. View generated dashboard:
```bash
ls -la dashboards/fer_webapp_*/
cat dashboards/fer_webapp_*/summary.txt
```

## ⚠️ Troubleshooting

### Sensor not detected
```bash
# Check I2C
sudo i2cdetect -y 1

# Check permissions
sudo usermod -a -G i2c pi
```

### No matched data
- Ensure both emotion and sensor loggers are running
- Check timestamps are recent (within 7 days)
- Verify same user_id for both data sources

### Import errors
```bash
pip3 install max30100 paho-mqtt matplotlib
```

## 📈 Normal Ranges

- **Heart Rate**: 60-100 bpm (adults at rest)
- **SpO2**: 95-100% (normal oxygen saturation)

⚠️ Values outside these ranges may indicate stress or health issues. Consult healthcare professionals for medical concerns.

## 🔐 Privacy Note

All data is stored locally on Raspberry Pi. No cloud storage. Sensor data is personal health information - handle securely.
