"""
Create sensor data table in the database
Run this once on Raspberry Pi: python3 create_sensor_table.py
"""

import sqlite3

DB_PATH = 'fer_events.db'

def create_sensor_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create sensor_data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            heart_rate INTEGER,
            spo2 INTEGER,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES events(user_id)
        )
    ''')
    
    # Create index for faster timestamp-based queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_sensor_timestamp 
        ON sensor_data(user_id, timestamp)
    ''')
    
    conn.commit()
    conn.close()
    print("✓ Sensor data table created successfully!")

if __name__ == '__main__':
    create_sensor_table()
