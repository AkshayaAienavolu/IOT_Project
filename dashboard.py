"""
Emotion Dashboard - Visualize FER data from SQLite

Usage:
    python dashboard.py [database_path]
    
Example:
    python dashboard.py /home/pi/fer_events.db
"""

import sqlite3
import sys
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import Counter

DB_PATH = sys.argv[1] if len(sys.argv) > 1 else 'fer_events.db'

def fetch_data(days=2):
    """Fetch emotion data from last N days"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Get data from last N days
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

def plot_emotion_distribution(data):
    """Bar chart: emotion counts"""
    emotions = [row[2] for row in data]
    counts = Counter(emotions)
    
    plt.figure(figsize=(10, 6))
    plt.bar(counts.keys(), counts.values(), color='steelblue')
    plt.xlabel('Emotion')
    plt.ylabel('Count')
    plt.title(f'Emotion Distribution (Last 2 Days, N={len(data)})')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('emotion_distribution.png', dpi=150)
    print('✓ Saved: emotion_distribution.png')
    plt.close()

def plot_emotion_timeline(data):
    """Line chart: emotion over time"""
    timestamps = [datetime.fromisoformat(row[0].replace('Z', '+00:00')) for row in data]
    emotions = [row[2] for row in data]
    
    # Map emotions to numeric values for plotting
    emotion_map = {'Angry': 0, 'Disgust': 1, 'Fear': 2, 'Happy': 3, 'Neutral': 4, 'Sad': 5, 'Surprise': 6}
    emotion_values = [emotion_map.get(e, 4) for e in emotions]
    
    plt.figure(figsize=(14, 6))
    plt.scatter(timestamps, emotion_values, alpha=0.6, s=10, c=emotion_values, cmap='viridis')
    plt.yticks(range(7), list(emotion_map.keys()))
    plt.xlabel('Time')
    plt.ylabel('Emotion')
    plt.title('Emotion Timeline (Last 2 Days)')
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig('emotion_timeline.png', dpi=150)
    print('✓ Saved: emotion_timeline.png')
    plt.close()

def plot_confidence_trends(data):
    """Line chart: confidence over time"""
    timestamps = [datetime.fromisoformat(row[0].replace('Z', '+00:00')) for row in data]
    confidences = [row[3] for row in data]
    
    plt.figure(figsize=(14, 6))
    plt.plot(timestamps, confidences, alpha=0.7, linewidth=0.5, color='green')
    plt.xlabel('Time')
    plt.ylabel('Confidence')
    plt.title('Prediction Confidence Over Time')
    plt.ylim(0, 1)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig('confidence_timeline.png', dpi=150)
    print('✓ Saved: confidence_timeline.png')
    plt.close()

def plot_user_activity(data):
    """Bar chart: events per user"""
    users = [row[1] for row in data]
    counts = Counter(users)
    
    plt.figure(figsize=(10, 6))
    plt.barh(list(counts.keys()), list(counts.values()), color='coral')
    plt.xlabel('Event Count')
    plt.ylabel('User ID')
    plt.title('Activity by User (Last 2 Days)')
    plt.tight_layout()
    plt.savefig('user_activity.png', dpi=150)
    print('✓ Saved: user_activity.png')
    plt.close()

def generate_summary(data):
    """Print summary statistics"""
    print('\n' + '='*50)
    print('EMOTION DATA SUMMARY (Last 2 Days)')
    print('='*50)
    print(f'Total Events: {len(data)}')
    
    if data:
        emotions = [row[2] for row in data]
        counts = Counter(emotions)
        print(f'\nEmotion Breakdown:')
        for emotion, count in counts.most_common():
            pct = (count / len(data)) * 100
            print(f'  {emotion:10s}: {count:5d} ({pct:5.1f}%)')
        
        confidences = [row[3] for row in data]
        avg_conf = sum(confidences) / len(confidences)
        print(f'\nAverage Confidence: {avg_conf:.3f}')
        
        users = set(row[1] for row in data)
        print(f'Unique Users: {len(users)}')
    
    print('='*50 + '\n')

def main():
    print(f'Loading data from: {DB_PATH}')
    data = fetch_data(days=2)
    
    if not data:
        print('❌ No data found for the last 2 days.')
        return
    
    print(f'✓ Loaded {len(data)} events')
    
    # Generate visualizations
    plot_emotion_distribution(data)
    plot_emotion_timeline(data)
    plot_confidence_trends(data)
    plot_user_activity(data)
    
    # Print summary
    generate_summary(data)
    
    print('Dashboard generation complete!')
    print('Open the PNG files to view charts.')

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
