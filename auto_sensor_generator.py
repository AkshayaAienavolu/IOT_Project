"""
Auto-generate sensor data for new users
Monitors the events table and creates matching sensor data for any new emotion records
Run this in background to simulate sensor data for all users
"""

import sqlite3
import random
import time
from datetime import datetime, timedelta

DB_PATH = 'fer_events.db'
CHECK_INTERVAL = 30  # Check every 30 seconds

def get_last_processed_event():
    """Get the ID of the last processed event"""
    try:
        with open('.last_sensor_event_id', 'r') as f:
            return int(f.read().strip())
    except FileNotFoundError:
        return 0

def save_last_processed_event(event_id):
    """Save the ID of the last processed event"""
    with open('.last_sensor_event_id', 'w') as f:
        f.write(str(event_id))

def generate_sensor_for_emotion(emotion):
    """Generate realistic sensor values based on emotion"""
    if emotion in ['Happy', 'Surprise']:
        heart_rate = random.randint(70, 85)
        spo2 = random.randint(97, 100)
    elif emotion in ['Angry', 'Fear']:
        heart_rate = random.randint(90, 110)
        spo2 = random.randint(95, 98)
    elif emotion == 'Sad':
        heart_rate = random.randint(65, 75)
        spo2 = random.randint(96, 99)
    else:  # Neutral, Disgust
        heart_rate = random.randint(70, 80)
        spo2 = random.randint(96, 100)
    
    return heart_rate, spo2

def process_new_events():
    """Check for new emotion events and create matching sensor data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Ensure sensor_data table exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            heart_rate INTEGER,
            spo2 INTEGER,
            timestamp TEXT NOT NULL
        )
    ''')
    
    last_id = get_last_processed_event()
    
    # Get new events since last check
    cursor.execute('''
        SELECT id, user_id, ts_received, emotion
        FROM events
        WHERE id > ?
        ORDER BY id ASC
    ''', (last_id,))
    
    new_events = cursor.fetchall()
    
    if new_events:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Processing {len(new_events)} new emotion events...")
        
        for event_id, user_id, timestamp, emotion in new_events:
            # Generate sensor data
            heart_rate, spo2 = generate_sensor_for_emotion(emotion)
            
            # Add random offset to timestamp (within ±15 seconds)
            offset = random.randint(-15, 15)
            try:
                sensor_time = datetime.fromisoformat(timestamp.replace('Z', '')) + timedelta(seconds=offset)
                sensor_timestamp = sensor_time.isoformat() + 'Z'
            except:
                sensor_timestamp = timestamp
            
            # Insert sensor data
            cursor.execute('''
                INSERT INTO sensor_data (user_id, heart_rate, spo2, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (user_id, heart_rate, spo2, sensor_timestamp))
            
            print(f"  ✓ {user_id[:20]}... | {emotion:8s} → HR:{heart_rate:3d} SpO2:{spo2:3d}%")
            
            # Update last processed ID
            save_last_processed_event(event_id)
        
        conn.commit()
        print(f"  ✓ Saved {len(new_events)} sensor readings\n")
    
    conn.close()

def main():
    print("🏥 Auto Sensor Data Generator")
    print("=" * 60)
    print("Monitoring emotion events and generating matching sensor data...")
    print("Press Ctrl+C to stop\n")
    
    while True:
        try:
            process_new_events()
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping auto sensor data generator...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    main()
