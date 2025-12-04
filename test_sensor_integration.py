"""
Test the integrated dashboard with simulated sensor data
This creates fake sensor readings matched with existing emotion data
"""

import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = 'fer_events.db'

def generate_test_sensor_data():
    """Generate test sensor data matched with existing emotion data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get recent emotion data
    cursor.execute('''
        SELECT user_id, ts_received, emotion
        FROM events
        WHERE ts_received > ?
        ORDER BY ts_received DESC
        LIMIT 100
    ''', ((datetime.now() - timedelta(days=7)).isoformat(),))
    
    emotions = cursor.fetchall()
    
    if not emotions:
        print("No emotion data found. Run the camera app first.")
        conn.close()
        return
    
    print(f"Found {len(emotions)} emotion records. Generating matching sensor data...")
    
    # Create sensor_data table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            heart_rate INTEGER,
            spo2 INTEGER,
            timestamp TEXT NOT NULL
        )
    ''')
    
    # Generate sensor data for each emotion record
    count = 0
    for user_id, timestamp, emotion in emotions:
        # Generate realistic values based on emotion
        if emotion in ['Happy', 'Surprise']:
            heart_rate = random.randint(70, 85)  # Normal-elevated
            spo2 = random.randint(97, 100)
        elif emotion in ['Angry', 'Fear']:
            heart_rate = random.randint(90, 110)  # Elevated (stress)
            spo2 = random.randint(95, 98)
        elif emotion == 'Sad':
            heart_rate = random.randint(65, 75)  # Slightly lower
            spo2 = random.randint(96, 99)
        else:  # Neutral, Disgust
            heart_rate = random.randint(70, 80)  # Normal
            spo2 = random.randint(96, 100)
        
        # Add random offset to timestamp (within ±15 seconds)
        offset = random.randint(-15, 15)
        sensor_time = datetime.fromisoformat(timestamp.replace('Z', '')) + timedelta(seconds=offset)
        sensor_timestamp = sensor_time.isoformat() + 'Z'
        
        cursor.execute('''
            INSERT INTO sensor_data (user_id, heart_rate, spo2, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (user_id, heart_rate, spo2, sensor_timestamp))
        
        count += 1
    
    conn.commit()
    conn.close()
    
    print(f"✓ Generated {count} sensor readings")
    print("\nNow run: python3 dashboard_integrated.py")

if __name__ == '__main__':
    generate_test_sensor_data()
