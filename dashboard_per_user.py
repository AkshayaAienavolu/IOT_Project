"""
Per-User Emotion Dashboard - Individual reports for each user

Usage:
    python dashboard_per_user.py [database_path]
    
Generates:
    - Overall summary dashboard
    - Individual folder for each user with their charts
"""

import sqlite3
import sys
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from collections import Counter

DB_PATH = sys.argv[1] if len(sys.argv) > 1 else 'fer_events.db'
OUTPUT_DIR = 'dashboards'

def fetch_all_data(days=2):
    """Fetch all emotion data from last N days"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    cur.execute('''
        SELECT ts_received, user_id, emotion, confidence 
        FROM events 
        WHERE ts_received >= ?
        ORDER BY ts_received ASC
    ''', (cutoff,))
    
    rows = cur.fetchall()
    conn.close()
    return rows

def get_user_data(all_data, user_id):
    """Filter data for specific user"""
    return [row for row in all_data if row[1] == user_id]

def create_user_dashboard(user_id, user_data, output_folder):
    """Generate complete dashboard for one user"""
    os.makedirs(output_folder, exist_ok=True)
    
    print(f'\n📊 Generating dashboard for: {user_id}')
    print(f'   Events: {len(user_data)}')
    
    # 1. Emotion distribution
    emotions = [row[2] for row in user_data]
    counts = Counter(emotions)
    
    plt.figure(figsize=(10, 6))
    colors = {'Angry':'red', 'Disgust':'purple', 'Fear':'orange', 'Happy':'green', 
              'Neutral':'gray', 'Sad':'blue', 'Surprise':'yellow'}
    bar_colors = [colors.get(e, 'gray') for e in counts.keys()]
    
    plt.bar(counts.keys(), counts.values(), color=bar_colors, alpha=0.7, edgecolor='black')
    plt.xlabel('Emotion', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    plt.title(f'Emotion Distribution - {user_id}\n(N={len(user_data)} events)', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{output_folder}/emotion_distribution.png', dpi=150)
    plt.close()
    
    # 2. Timeline
    timestamps = [datetime.fromisoformat(row[0].replace('Z', '+00:00')) for row in user_data]
    emotion_map = {'Angry': 0, 'Disgust': 1, 'Fear': 2, 'Happy': 3, 'Neutral': 4, 'Sad': 5, 'Surprise': 6}
    emotion_values = [emotion_map.get(e, 4) for e in emotions]
    emotion_colors = [colors.get(e, 'gray') for e in emotions]
    
    plt.figure(figsize=(14, 6))
    plt.scatter(timestamps, emotion_values, alpha=0.6, s=30, c=emotion_colors, edgecolors='black', linewidth=0.5)
    plt.yticks(range(7), list(emotion_map.keys()))
    plt.xlabel('Time', fontsize=12)
    plt.ylabel('Emotion', fontsize=12)
    plt.title(f'Emotion Timeline - {user_id}', fontsize=14, fontweight='bold')
    plt.grid(axis='y', alpha=0.3)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(f'{output_folder}/timeline.png', dpi=150)
    plt.close()
    
    # 3. Confidence trends
    confidences = [row[3] for row in user_data]
    
    plt.figure(figsize=(14, 6))
    plt.plot(timestamps, confidences, alpha=0.7, linewidth=1, color='green', marker='o', markersize=2)
    plt.axhline(y=sum(confidences)/len(confidences), color='red', linestyle='--', label=f'Avg: {sum(confidences)/len(confidences):.3f}')
    plt.xlabel('Time', fontsize=12)
    plt.ylabel('Confidence', fontsize=12)
    plt.title(f'Prediction Confidence - {user_id}', fontsize=14, fontweight='bold')
    plt.ylim(0, 1)
    plt.legend()
    plt.grid(alpha=0.3)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(f'{output_folder}/confidence.png', dpi=150)
    plt.close()
    
    # 4. Hourly activity heatmap
    hours = [datetime.fromisoformat(row[0].replace('Z', '+00:00')).hour for row in user_data]
    hour_counts = Counter(hours)
    
    plt.figure(figsize=(12, 5))
    all_hours = range(24)
    counts_list = [hour_counts.get(h, 0) for h in all_hours]
    
    plt.bar(all_hours, counts_list, color='steelblue', alpha=0.7, edgecolor='black')
    plt.xlabel('Hour of Day', fontsize=12)
    plt.ylabel('Event Count', fontsize=12)
    plt.title(f'Activity by Hour - {user_id}', fontsize=14, fontweight='bold')
    plt.xticks(all_hours)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{output_folder}/hourly_activity.png', dpi=150)
    plt.close()
    
    # 5. Generate text summary
    with open(f'{output_folder}/summary.txt', 'w') as f:
        f.write(f'EMOTION ANALYSIS REPORT\n')
        f.write(f'User: {user_id}\n')
        f.write(f'Period: Last 2 days\n')
        f.write(f'='*60 + '\n\n')
        f.write(f'Total Events: {len(user_data)}\n\n')
        
        f.write('Emotion Breakdown:\n')
        for emotion, count in counts.most_common():
            pct = (count / len(user_data)) * 100
            f.write(f'  {emotion:10s}: {count:5d} ({pct:5.1f}%)\n')
        
        f.write(f'\nAverage Confidence: {sum(confidences)/len(confidences):.3f}\n')
        f.write(f'Min Confidence: {min(confidences):.3f}\n')
        f.write(f'Max Confidence: {max(confidences):.3f}\n')
        
        # Most common emotion
        top_emotion = counts.most_common(1)[0][0]
        f.write(f'\nDominant Emotion: {top_emotion}\n')
        
        # Time range
        f.write(f'\nFirst Event: {timestamps[0].strftime("%Y-%m-%d %H:%M:%S")}\n')
        f.write(f'Last Event: {timestamps[-1].strftime("%Y-%m-%d %H:%M:%S")}\n')
    
    print(f'   ✓ Generated 4 charts + summary in: {output_folder}')

def main():
    print(f'📁 Loading data from: {DB_PATH}')
    all_data = fetch_all_data(days=2)
    
    if not all_data:
        print('❌ No data found for the last 2 days.')
        return
    
    print(f'✓ Loaded {len(all_data)} total events')
    
    # Get unique users
    users = sorted(set(row[1] for row in all_data))
    print(f'✓ Found {len(users)} unique users')
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Generate dashboard for each user
    for user_id in users:
        user_data = get_user_data(all_data, user_id)
        user_folder = os.path.join(OUTPUT_DIR, user_id.replace('/', '_'))
        create_user_dashboard(user_id, user_data, user_folder)
    
    # Generate overall summary
    print(f'\n📊 Generating overall summary...')
    
    with open(f'{OUTPUT_DIR}/OVERALL_SUMMARY.txt', 'w') as f:
        f.write('OVERALL EMOTION ANALYSIS\n')
        f.write('='*60 + '\n\n')
        f.write(f'Total Events: {len(all_data)}\n')
        f.write(f'Unique Users: {len(users)}\n\n')
        
        f.write('Per-User Event Counts:\n')
        for user_id in users:
            count = len(get_user_data(all_data, user_id))
            f.write(f'  {user_id}: {count}\n')
        
        f.write(f'\nOverall Emotion Distribution:\n')
        all_emotions = [row[2] for row in all_data]
        overall_counts = Counter(all_emotions)
        for emotion, count in overall_counts.most_common():
            pct = (count / len(all_data)) * 100
            f.write(f'  {emotion:10s}: {count:5d} ({pct:5.1f}%)\n')
    
    print(f'\n✅ Dashboard generation complete!')
    print(f'📂 Output directory: {OUTPUT_DIR}/')
    print(f'\nUser dashboards:')
    for user_id in users:
        folder = user_id.replace('/', '_')
        print(f'  - {OUTPUT_DIR}/{folder}/')

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
