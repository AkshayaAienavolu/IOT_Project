"""
Cleanup old users - Keep only the 5 most recent users
Deletes emotion events, sensor data, and dashboard files for old users
"""

import sqlite3
import shutil
import os

DB_PATH = 'fer_events.db'
DASHBOARD_DIR = 'dashboards'

def cleanup_old_users(keep_count=5):
    """Keep only the N most recent users, delete everything else"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all users ordered by most recent activity
    cursor.execute('''
        SELECT user_id, MAX(ts_received) as last_seen, COUNT(*) as event_count
        FROM events
        GROUP BY user_id
        ORDER BY last_seen DESC
    ''')
    
    all_users = cursor.fetchall()
    
    if len(all_users) <= keep_count:
        print(f"Only {len(all_users)} users found. Nothing to delete.")
        conn.close()
        return
    
    # Users to keep (most recent)
    users_to_keep = [user[0] for user in all_users[:keep_count]]
    
    # Users to delete (old ones)
    users_to_delete = [user[0] for user in all_users[keep_count:]]
    
    print(f"Total users: {len(all_users)}")
    print(f"Keeping {keep_count} most recent users:")
    for user_id, last_seen, count in all_users[:keep_count]:
        print(f"  ✓ {user_id} (last seen: {last_seen}, events: {count})")
    
    print(f"\nDeleting {len(users_to_delete)} old users:")
    for user_id, last_seen, count in all_users[keep_count:]:
        print(f"  ✗ {user_id} (last seen: {last_seen}, events: {count})")
    
    # Confirm deletion
    print("\n" + "="*60)
    response = input("Proceed with deletion? (yes/no): ").lower().strip()
    
    if response != 'yes':
        print("Cancelled.")
        conn.close()
        return
    
    print("\nDeleting data...")
    
    # Delete from events table
    events_deleted = 0
    for user_id in users_to_delete:
        cursor.execute('DELETE FROM events WHERE user_id = ?', (user_id,))
        events_deleted += cursor.rowcount
    
    print(f"  ✓ Deleted {events_deleted} emotion events")
    
    # Delete from sensor_data table (if exists)
    try:
        sensor_deleted = 0
        for user_id in users_to_delete:
            cursor.execute('DELETE FROM sensor_data WHERE user_id = ?', (user_id,))
            sensor_deleted += cursor.rowcount
        print(f"  ✓ Deleted {sensor_deleted} sensor readings")
    except sqlite3.OperationalError:
        print("  ℹ️  No sensor_data table found")
    
    conn.commit()
    conn.close()
    
    # Delete dashboard folders
    dashboards_deleted = 0
    if os.path.exists(DASHBOARD_DIR):
        for user_id in users_to_delete:
            user_folder = os.path.join(DASHBOARD_DIR, user_id.replace('/', '_'))
            if os.path.exists(user_folder):
                shutil.rmtree(user_folder)
                dashboards_deleted += 1
    
    print(f"  ✓ Deleted {dashboards_deleted} dashboard folders")
    
    print("\n" + "="*60)
    print(f"✓ Cleanup complete!")
    print(f"  Kept: {len(users_to_keep)} users")
    print(f"  Deleted: {len(users_to_delete)} users")
    print(f"  Total events deleted: {events_deleted}")

if __name__ == '__main__':
    cleanup_old_users(keep_count=5)
