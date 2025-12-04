"""
MAX30100 Sensor Logger with MQTT Integration
Reads heart rate and SpO2, publishes to MQTT topic: sensor/health

Hardware Connection (Raspberry Pi):
- VIN → 3.3V
- GND → GND  
- SCL → GPIO 3 (SCL)
- SDA → GPIO 2 (SDA)

Install: sudo pip3 install max30100 paho-mqtt
Enable I2C: sudo raspi-config → Interface Options → I2C → Enable
"""

import time
import json
import sqlite3
from datetime import datetime
import paho.mqtt.client as mqtt

# Try to import MAX30100, fallback to simulation for testing
try:
    from max30100 import MAX30100
    SIMULATION_MODE = False
except ImportError:
    print("⚠️  MAX30100 library not found. Running in SIMULATION mode.")
    SIMULATION_MODE = True
    import random

# Database
DB_PATH = 'fer_events.db'

# MQTT Configuration (HiveMQ Cloud)
MQTT_BROKER = "308c552d0a56494799306611ffacac19.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USERNAME = "pi_subscriber"  # Using same credentials as logger
MQTT_PASSWORD = "Qwerty123"
MQTT_TOPIC = "sensor/health"

# Sensor reading interval (seconds)
READING_INTERVAL = 10

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✓ Connected to MQTT broker")
    else:
        print(f"✗ Connection failed with code {rc}")

def init_mqtt():
    """Initialize MQTT client"""
    client = mqtt.Client(client_id="pi_sensor_logger")
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.tls_set()
    client.on_connect = on_connect
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        return client
    except Exception as e:
        print(f"✗ MQTT connection error: {e}")
        return None

def save_to_database(user_id, heart_rate, spo2, timestamp):
    """Save sensor reading to local database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sensor_data (user_id, heart_rate, spo2, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (user_id, heart_rate, spo2, timestamp))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False

def read_sensor_simulated():
    """Simulate sensor readings for testing"""
    heart_rate = random.randint(60, 100)  # Normal range: 60-100 bpm
    spo2 = random.randint(95, 100)  # Normal range: 95-100%
    return heart_rate, spo2

def main():
    print("🏥 Starting MAX30100 Sensor Logger")
    print("=" * 50)
    
    # Initialize MQTT
    mqtt_client = init_mqtt()
    if not mqtt_client:
        print("⚠️  Running without MQTT (local logging only)")
    
    # Initialize sensor
    if not SIMULATION_MODE:
        try:
            sensor = MAX30100()
            sensor.enable_spo2()
            sensor.enable_hr()
            print("✓ MAX30100 sensor initialized")
        except Exception as e:
            print(f"✗ Sensor initialization failed: {e}")
            print("⚠️  Switching to SIMULATION mode")
            SIMULATION_MODE = True
    
    if SIMULATION_MODE:
        print("📊 SIMULATION MODE: Generating random sensor data")
    
    # Default user ID (can be changed via command line argument)
    import sys
    user_id = sys.argv[1] if len(sys.argv) > 1 else "sensor_user_001"
    
    print(f"👤 User ID: {user_id}")
    print(f"⏱️  Reading interval: {READING_INTERVAL} seconds")
    print(f"📍 MQTT Topic: {MQTT_TOPIC}")
    print("=" * 50)
    print("\nPress Ctrl+C to stop\n")
    
    reading_count = 0
    
    try:
        while True:
            timestamp = datetime.now().isoformat() + 'Z'
            
            # Read sensor data
            if SIMULATION_MODE:
                heart_rate, spo2 = read_sensor_simulated()
            else:
                try:
                    sensor.update()
                    heart_rate = sensor.get_heart_rate()
                    spo2 = sensor.get_spo2()
                    
                    # Validate readings
                    if heart_rate is None or heart_rate < 30 or heart_rate > 220:
                        print("⚠️  Invalid heart rate, skipping...")
                        time.sleep(READING_INTERVAL)
                        continue
                    if spo2 is None or spo2 < 70 or spo2 > 100:
                        print("⚠️  Invalid SpO2, skipping...")
                        time.sleep(READING_INTERVAL)
                        continue
                        
                except Exception as e:
                    print(f"✗ Sensor read error: {e}")
                    time.sleep(READING_INTERVAL)
                    continue
            
            reading_count += 1
            
            # Prepare data packet
            data = {
                'user_id': user_id,
                'heart_rate': int(heart_rate),
                'spo2': int(spo2),
                'timestamp': timestamp,
                'reading_number': reading_count
            }
            
            # Save to local database
            if save_to_database(user_id, int(heart_rate), int(spo2), timestamp):
                print(f"[{reading_count}] {timestamp}")
                print(f"    ❤️  Heart Rate: {heart_rate} bpm")
                print(f"    🫁 SpO2: {spo2}%")
                
                # Publish to MQTT
                if mqtt_client:
                    try:
                        mqtt_client.publish(MQTT_TOPIC, json.dumps(data), qos=1)
                        print(f"    ✓ Published to MQTT")
                    except Exception as e:
                        print(f"    ✗ MQTT publish error: {e}")
                
                print()
            
            time.sleep(READING_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping sensor logger...")
        if mqtt_client:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
        print(f"✓ Total readings: {reading_count}")
        print("✓ Sensor logger stopped")

if __name__ == '__main__':
    main()
