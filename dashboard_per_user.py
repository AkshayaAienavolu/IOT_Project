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

def calculate_mental_state(emotion_counts, total_events):
    """Calculate mental health state based on emotion distribution"""
    if total_events == 0:
        return "Insufficient Data", "gray", "Not enough data to assess mental state."
    
    # Calculate percentages
    happy_pct = (emotion_counts.get('Happy', 0) / total_events) * 100
    neutral_pct = (emotion_counts.get('Neutral', 0) / total_events) * 100
    sad_pct = (emotion_counts.get('Sad', 0) / total_events) * 100
    angry_pct = (emotion_counts.get('Angry', 0) / total_events) * 100
    fear_pct = (emotion_counts.get('Fear', 0) / total_events) * 100
    
    positive = happy_pct
    negative = sad_pct + angry_pct + fear_pct
    
    # Determine mental state
    if positive >= 60:
        state = "Excellent"
        color = "green"
        advice = "You're showing very positive emotional patterns! Keep maintaining healthy habits and social connections."
    elif positive >= 40 and negative < 30:
        state = "Good"
        color = "lightgreen"
        advice = "You're in a healthy emotional state. Continue with balanced activities and self-care routines."
    elif negative >= 50:
        state = "Needs Attention"
        color = "orange"
        advice = "You're showing elevated negative emotions. Consider stress management techniques, talking to friends, or seeking professional support if feelings persist."
    elif negative >= 30:
        state = "Fair"
        color = "yellow"
        advice = "Your emotional state is mixed. Try to identify stressors and incorporate more positive activities. Regular exercise and social interaction can help."
    else:
        state = "Moderate"
        color = "lightyellow"
        advice = "Your emotions are relatively balanced. Focus on maintaining consistency in sleep, exercise, and social connections."
    
    return state, color, advice

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
    
    # 5. Generate text summary with mental state analysis
    # Get 7-day data for mental state (fetch separately)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cutoff_7d = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')
    cur.execute('''
        SELECT emotion FROM events 
        WHERE user_id = ? AND ts_received >= ?
    ''', (user_id, cutoff_7d))
    week_emotions = [row[0] for row in cur.fetchall()]
    conn.close()
    
    week_counts = Counter(week_emotions)
    mental_state, state_color, advice = calculate_mental_state(week_counts, len(week_emotions))
    
    with open(f'{output_folder}/summary.txt', 'w') as f:
        f.write(f'╔════════════════════════════════════════════════════════════╗\n')
        f.write(f'║           EMOTION ANALYSIS & MENTAL STATE REPORT          ║\n')
        f.write(f'╚════════════════════════════════════════════════════════════╝\n\n')
        
        f.write(f'User ID: {user_id}\n')
        f.write(f'Report Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        f.write(f'='*60 + '\n\n')
        
        # Mental State Assessment (7 days)
        f.write(f'🧠 MENTAL STATE ASSESSMENT (Last 7 Days)\n')
        f.write(f'-'*60 + '\n')
        f.write(f'Overall State: {mental_state}\n')
        f.write(f'Total Events Analyzed: {len(week_emotions)}\n\n')
        
        if len(week_emotions) > 0:
            f.write(f'7-Day Emotion Distribution:\n')
            for emotion, count in week_counts.most_common():
                pct = (count / len(week_emotions)) * 100
                f.write(f'  {emotion:10s}: {count:5d} ({pct:5.1f}%)\n')
            
            f.write(f'\n💡 Recommendation:\n{advice}\n')
        else:
            f.write('Insufficient data for 7-day assessment.\n')
        
        f.write(f'\n{"="*60}\n\n')
        
        # 2-Day Detailed Analysis
        f.write(f'📊 DETAILED ANALYSIS (Last 2 Days)\n')
        f.write(f'-'*60 + '\n')
        f.write(f'Total Events: {len(user_data)}\n\n')
        
        f.write('Emotion Breakdown:\n')
        for emotion, count in counts.most_common():
            pct = (count / len(user_data)) * 100
            bar = '█' * int(pct / 2)
            f.write(f'  {emotion:10s}: {count:5d} ({pct:5.1f}%) {bar}\n')
        
        f.write(f'\n📈 Confidence Metrics:\n')
        f.write(f'  Average: {sum(confidences)/len(confidences):.3f}\n')
        f.write(f'  Minimum: {min(confidences):.3f}\n')
        f.write(f'  Maximum: {max(confidences):.3f}\n')
        
        # Most common emotion
        top_emotion = counts.most_common(1)[0][0]
        f.write(f'\n🎯 Dominant Emotion: {top_emotion}\n')
        
        # Time range
        f.write(f'\n⏰ Activity Period:\n')
        f.write(f'  First Event: {timestamps[0].strftime("%Y-%m-%d %H:%M:%S")}\n')
        f.write(f'  Last Event:  {timestamps[-1].strftime("%Y-%m-%d %H:%M:%S")}\n')
        
        duration = timestamps[-1] - timestamps[0]
        f.write(f'  Duration: {duration}\n')
    
    print(f'   ✓ Generated 4 charts + mental state report in: {output_folder}')

def main():
    print(f'📁 Loading data from: {DB_PATH}')
    
    # Fetch 2-day data for charts
    chart_data = fetch_all_data(days=2)
    
    # Also get all users from last 7 days for mental state analysis
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cutoff_7d = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')
    cur.execute('SELECT DISTINCT user_id FROM events WHERE ts_received >= ?', (cutoff_7d,))
    all_users = sorted([row[0] for row in cur.fetchall()])
    conn.close()
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Generate dashboard for each user (use all_users from 7-day window)
    for user_id in all_users:
        # Get user's 2-day data for charts
        user_data = get_user_data(chart_data, user_id)
        
        # Skip if no data in last 2 days, but still create report with 7-day mental state
        if len(user_data) == 0:
            print(f'\n⚠️  User {user_id}: No activity in last 2 days (charts skipped, mental state only)')
            user_folder = os.path.join(OUTPUT_DIR, user_id.replace('/', '_'))
            os.makedirs(user_folder, exist_ok=True)
            
            # Create summary with mental state only
            conn = sqlite3.connect(DB_PATH)
    # Generate overall summary
    print(f'\n📊 Generating overall summary...')
    
    with open(f'{OUTPUT_DIR}/OVERALL_SUMMARY.txt', 'w') as f:
        f.write('OVERALL EMOTION ANALYSIS\n')
        f.write('='*60 + '\n\n')
        f.write(f'Total Events (2 days): {len(chart_data)}\n')
        f.write(f'Active Users (7 days): {len(all_users)}\n\n')
        
        f.write('Per-User Event Counts (Last 2 Days):\n')
        for user_id in all_users:
            count = len(get_user_data(chart_data, user_id))
            f.write(f'  {user_id}: {count}\n')
        
        if len(chart_data) > 0:
            f.write(f'\nOverall Emotion Distribution (Last 2 Days):\n')
            all_emotions = [row[2] for row in chart_data]
            overall_counts = Counter(all_emotions)
            for emotion, count in overall_counts.most_common():
                pct = (count / len(chart_data)) * 100
                f.write(f'  {emotion:10s}: {count:5d} ({pct:5.1f}%)\n')
    
    print(f'\n✅ Dashboard generation complete!')
    print(f'📂 Output directory: {OUTPUT_DIR}/')
    print(f'\nUser dashboards:')
    for user_id in all_users:
        folder = user_id.replace('/', '_')
        print(f'  - {OUTPUT_DIR}/{folder}/')data, user_folder)
    
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
