"""
Test the integrated dashboard with simulated sensor data
This creates fake sensor readings matched with existing emotion data FOR ALL USERS
"""

import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = 'fer_events.db'

def generate_test_sensor_data():
    """Generate test sensor data matched with existing emotion data for ALL users"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get ALL users from events table
    cursor.execute('''
        SELECT DISTINCT user_id FROM events
        ORDER BY user_id
    ''')
    
    all_users = [row[0] for row in cursor.fetchall()]
    
    if not all_users:
        print("No users found in database. Run the camera app first.")
        conn.close()
        return
    
    print(f"Found {len(all_users)} users:")
    for user in all_users:
        print(f"  - {user}")
    print()
    
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
    
    # Clear existing sensor data to regenerate fresh
    print("Clearing existing sensor data...")
    cursor.execute('DELETE FROM sensor_data')
    conn.commit()
    
    total_count = 0
    
    # For each user, get their emotion data and generate matching sensor data
    for user_id in all_users:
        print(f"\nProcessing user: {user_id}")
        
        # Get recent emotion data for this user (last 7 days)
        cursor.execute('''
            SELECT user_id, ts_received, emotion
            FROM events
            WHERE user_id = ? AND ts_received > ?
            ORDER BY ts_received DESC
            LIMIT 200
        ''', (user_id, (datetime.now() - timedelta(days=7)).isoformat()))
        
        emotions = cursor.fetchall()
        
        if not emotions:
            print(f"  ⚠️  No recent data for {user_id}, skipping...")
            continue
        
        print(f"  Found {len(emotions)} emotion records")
        
        # Generate sensor data for each emotion record
        user_count = 0
        for uid, timestamp, emotion in emotions:
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
            ''', (uid, heart_rate, spo2, sensor_timestamp))
            
            user_count += 1
            total_count += 1
        
        conn.commit()
        print(f"  ✓ Generated {user_count} sensor readings")
    
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"✓ Total sensor readings generated: {total_count}")
    print(f"✓ Users with sensor data: {len(all_users)}")
    print(f"\nNext steps:")
    print(f"  1. Run: python3 dashboard_integrated.py")
    print(f"  2. Restart: pkill -f dashboard_server.py && python3 dashboard_server.py")
    print(f"{'='*60}")

if __name__ == '__main__':
    generate_test_sensor_data()
