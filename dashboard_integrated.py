"""
Integrated Dashboard - Combines Emotion + Sensor Data
Matches facial emotion data with sensor readings by timestamp
Generates comprehensive mental-state reports
"""

import sqlite3
import sys
import os
import argparse
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import Counter

# Import wellbeing advisor
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from wellbeing_advisor import WellbeingAdvisor

# Parse arguments
parser = argparse.ArgumentParser(description='Generate integrated dashboards')
parser.add_argument('db_path', nargs='?', default='fer_events.db', help='Path to SQLite database')
parser.add_argument('--user', help='Generate for specific user ID only')
args = parser.parse_args()

DB_PATH = args.db_path
OUTPUT_DIR = 'dashboards'

def match_emotion_with_sensor(days=7):
    """Match emotion data with sensor data by timestamp (within 30 seconds)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    
    # Get all emotion data
    cursor.execute('''
        SELECT user_id, emotion, confidence, ts_received
        FROM events
        WHERE ts_received > ?
        ORDER BY ts_received ASC
    ''', (cutoff,))
    
    emotions = cursor.fetchall()
    
    # Get all sensor data
    cursor.execute('''
        SELECT user_id, heart_rate, spo2, timestamp
        FROM sensor_data
        WHERE timestamp > ?
        ORDER BY timestamp ASC
    ''', (cutoff,))
    
    sensors = cursor.fetchall()
    conn.close()
    
    # Match by timestamp (within 30 seconds)
    matched_data = []
    
    for user_id, emotion, confidence, emotion_ts in emotions:
        emotion_time = datetime.fromisoformat(emotion_ts.replace('Z', ''))
        
        # Find closest sensor reading for same user within 30 seconds
        best_match = None
        min_diff = timedelta(seconds=30)
        
        for s_user_id, hr, spo2, sensor_ts in sensors:
            if s_user_id != user_id:
                continue
                
            sensor_time = datetime.fromisoformat(sensor_ts.replace('Z', ''))
            time_diff = abs(emotion_time - sensor_time)
            
            if time_diff < min_diff:
                min_diff = time_diff
                best_match = (hr, spo2, sensor_ts)
        
        if best_match:
            hr, spo2, sensor_ts = best_match
            matched_data.append({
                'user_id': user_id,
                'emotion': emotion,
                'confidence': confidence,
                'heart_rate': hr,
                'spo2': spo2,
                'timestamp': emotion_ts,
                'match_quality': min_diff.total_seconds()
            })
    
    return matched_data

def analyze_mental_state(matched_data):
    """Analyze integrated mental state from emotion + sensor data"""
    if not matched_data:
        return {
            'state': 'No Data',
            'color': 'gray',
            'description': 'Insufficient data for analysis'
        }
    
    # Calculate averages
    avg_hr = sum(d['heart_rate'] for d in matched_data) / len(matched_data)
    avg_spo2 = sum(d['spo2'] for d in matched_data) / len(matched_data)
    
    # Count emotions
    emotions = [d['emotion'] for d in matched_data]
    emotion_counts = Counter(emotions)
    total = len(emotions)
    
    happy_pct = (emotion_counts.get('Happy', 0) / total) * 100
    neutral_pct = (emotion_counts.get('Neutral', 0) / total) * 100
    sad_pct = (emotion_counts.get('Sad', 0) / total) * 100
    stress_pct = ((emotion_counts.get('Angry', 0) + emotion_counts.get('Fear', 0)) / total) * 100
    
    # Physiological stress indicators
    hr_stress = avg_hr > 90  # Elevated heart rate
    spo2_low = avg_spo2 < 95  # Low oxygen
    
    # Combined analysis
    if happy_pct > 50 and not hr_stress and not spo2_low:
        state = "Excellent"
        color = "green"
        description = f"Positive emotions ({happy_pct:.0f}%) with healthy vitals (HR: {avg_hr:.0f}, SpO2: {avg_spo2:.0f}%)"
    
    elif neutral_pct > 50 and not hr_stress and not spo2_low:
        state = "Good"
        color = "lightgreen"
        description = f"Balanced emotions with stable vitals (HR: {avg_hr:.0f}, SpO2: {avg_spo2:.0f}%)"
    
    elif (sad_pct > 30 or stress_pct > 20) and hr_stress:
        state = "Stressed"
        color = "orange"
        description = f"Negative emotions ({sad_pct + stress_pct:.0f}%) with elevated heart rate ({avg_hr:.0f} bpm)"
    
    elif hr_stress or spo2_low:
        state = "Physiological Alert"
        color = "orange"
        description = f"Vital signs need attention (HR: {avg_hr:.0f}, SpO2: {avg_spo2:.0f}%)"
    
    elif sad_pct > 40:
        state = "Low Mood"
        color = "yellow"
        description = f"Predominant sadness ({sad_pct:.0f}%) detected"
    
    else:
        state = "Moderate"
        color = "yellow"
        description = f"Mixed emotional state with acceptable vitals"
    
    return {
        'state': state,
        'color': color,
        'description': description,
        'avg_hr': avg_hr,
        'avg_spo2': avg_spo2,
        'emotion_counts': emotion_counts
    }

def create_integrated_charts(user_id, matched_data, output_folder):
    """Create charts combining emotion and sensor data"""
    os.makedirs(output_folder, exist_ok=True)
    
    if not matched_data:
        return
    
    # Extract data
    timestamps = [datetime.fromisoformat(d['timestamp'].replace('Z', '')) for d in matched_data]
    emotions = [d['emotion'] for d in matched_data]
    heart_rates = [d['heart_rate'] for d in matched_data]
    spo2_values = [d['spo2'] for d in matched_data]
    
    # 1. Heart Rate + Emotion Timeline
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    fig.suptitle(f'Physiological + Emotional Timeline - {user_id}', fontsize=14, fontweight='bold')
    
    ax1.plot(timestamps, heart_rates, 'r-o', linewidth=2, markersize=4, label='Heart Rate')
    ax1.axhline(y=90, color='orange', linestyle='--', alpha=0.5, label='Elevated Threshold')
    ax1.set_ylabel('Heart Rate (bpm)', fontsize=11)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Color-code emotions on timeline
    emotion_colors = {'Happy': 'green', 'Sad': 'blue', 'Angry': 'red', 
                     'Fear': 'purple', 'Neutral': 'gray', 'Surprise': 'yellow', 'Disgust': 'brown'}
    for i, (ts, emo) in enumerate(zip(timestamps, emotions)):
        ax2.scatter(ts, 1, c=emotion_colors.get(emo, 'black'), s=100, alpha=0.7)
    
    ax2.set_ylabel('Emotion', fontsize=11)
    ax2.set_yticks([])
    ax2.set_xlabel('Time', fontsize=11)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{output_folder}/integrated_timeline.png', dpi=100, bbox_inches='tight')
    plt.close()
    
    # 2. Heart Rate vs Emotion Distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    emotion_hr_map = {}
    for emo, hr in zip(emotions, heart_rates):
        if emo not in emotion_hr_map:
            emotion_hr_map[emo] = []
        emotion_hr_map[emo].append(hr)
    
    box_data = [emotion_hr_map[emo] for emo in emotion_hr_map.keys()]
    ax.boxplot(box_data, labels=list(emotion_hr_map.keys()))
    ax.set_ylabel('Heart Rate (bpm)', fontsize=11)
    ax.set_xlabel('Emotion', fontsize=11)
    ax.set_title(f'Heart Rate Distribution by Emotion - {user_id}', fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{output_folder}/hr_by_emotion.png', dpi=100, bbox_inches='tight')
    plt.close()
    
    # 3. SpO2 Timeline
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(timestamps, spo2_values, 'b-o', linewidth=2, markersize=4)
    ax.axhline(y=95, color='red', linestyle='--', alpha=0.5, label='Normal Threshold')
    ax.set_ylabel('SpO2 (%)', fontsize=11)
    ax.set_xlabel('Time', fontsize=11)
    ax.set_title(f'Blood Oxygen Levels - {user_id}', fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{output_folder}/spo2_timeline.png', dpi=100, bbox_inches='tight')
    plt.close()
    
    print(f'   ✓ Created 3 integrated charts')

def create_integrated_report(user_id, matched_data, analysis, output_folder):
    """Create text report combining all data"""
    advisor = WellbeingAdvisor(DB_PATH)
    
    with open(f'{output_folder}/summary.txt', 'w') as f:
        f.write('=' * 70 + '\n')
        f.write('║     INTEGRATED MENTAL-STATE & HEALTH REPORT               ║\n')
        f.write('=' * 70 + '\n')
        f.write(f'User ID: {user_id}\n')
        f.write(f'Report Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        f.write('=' * 70 + '\n\n')
        
        # Overall State
        f.write('🧠 INTEGRATED MENTAL-STATE ASSESSMENT\n')
        f.write('-' * 70 + '\n')
        f.write(f'Overall State: {analysis["state"]}\n')
        f.write(f'Analysis: {analysis["description"]}\n')
        f.write(f'Data Points: {len(matched_data)} matched emotion-sensor readings\n\n')
        
        # Physiological Metrics
        f.write('❤️  PHYSIOLOGICAL METRICS (Average)\n')
        f.write('-' * 70 + '\n')
        f.write(f'Heart Rate: {analysis["avg_hr"]:.1f} bpm ')
        if analysis["avg_hr"] > 90:
            f.write('⚠️  ELEVATED\n')
        elif analysis["avg_hr"] < 60:
            f.write('⚠️  LOW\n')
        else:
            f.write('✓ NORMAL\n')
        
        f.write(f'SpO2: {analysis["avg_spo2"]:.1f}% ')
        if analysis["avg_spo2"] < 95:
            f.write('⚠️  LOW\n')
        else:
            f.write('✓ NORMAL\n')
        f.write('\n')
        
        # Emotion Distribution
        f.write('😊 EMOTION DISTRIBUTION\n')
        f.write('-' * 70 + '\n')
        for emotion, count in analysis["emotion_counts"].most_common():
            pct = (count / len(matched_data)) * 100
            f.write(f'  {emotion:10s}: {count:5d} ({pct:5.1f}%)\n')
        f.write('\n')
        
        # Wellbeing Suggestions (context-aware based on emotions + vitals)
        f.write('💡 Wellbeing Suggestions\n')
        f.write('-' * 70 + '\n')
        
        try:
            report = advisor.generate_wellbeing_report(user_id)
            if report['status'] == 'success':
                # Add physiological context first
                if analysis["avg_hr"] > 90:
                    f.write('   • ❤️  Your heart rate is elevated. Try deep breathing exercises.\n')
                if analysis["avg_spo2"] < 95:
                    f.write('   • 🫁 Low oxygen levels detected. Ensure proper ventilation and consider consulting a doctor.\n')
                
                # Add emotion-based suggestions from survey
                for tip in report['primary_suggestions']['tips'][:3]:
                    f.write(f'   • {tip}\n')
                
                # Add health maintenance tips based on overall state
                if analysis["state"] == "Excellent" or analysis["state"] == "Good":
                    f.write('   • 🌟 Your metrics look great! Keep up your healthy habits.\n')
                    f.write('   • 📊 Regular monitoring helps catch changes early.\n')
            else:
                # Fallback suggestions based on vitals and emotions
                if analysis["avg_hr"] > 90:
                    f.write('   • ❤️  Elevated heart rate detected. Practice relaxation techniques.\n')
                if analysis["avg_spo2"] < 95:
                    f.write('   • 🫁 Monitor oxygen levels and consult a healthcare provider.\n')
                f.write('   • 💧 Stay hydrated throughout the day.\n')
                f.write('   • 🧘 Maintain regular sleep and exercise routines.\n')
        except Exception as e:
            # Ultimate fallback
            if analysis["avg_hr"] > 90:
                f.write('   • ❤️  Your heart rate is elevated. Try deep breathing exercises.\n')
            if analysis["avg_spo2"] < 95:
                f.write('   • 🫁 Low oxygen levels detected. Ensure proper ventilation.\n')
            f.write('   • 💧 Stay hydrated and maintain regular sleep schedule.\n')
            f.write('   • 📊 Continue monitoring your health metrics regularly.\n')
        
        f.write('\n')
        f.write('=' * 70 + '\n')
        f.write('Note: This report combines facial emotion analysis with physiological\n')
        f.write('sensor data. Consult healthcare professionals for medical concerns.\n')
        f.write('=' * 70 + '\n')

def main():
    print("🏥 Integrated Dashboard Generator (Emotion + Sensor Data)")
    print("=" * 60)
    
    # Match emotion and sensor data
    print("📊 Matching emotion data with sensor readings...")
    matched_data = match_emotion_with_sensor(days=7)
    
    if not matched_data:
        print("⚠️  No matched data found. Ensure both emotion and sensor data exist.")
        return
    
    print(f"✓ Found {len(matched_data)} matched data points")
    
    # Group by user
    users = {}
    for data in matched_data:
        user_id = data['user_id']
        # Filter if specific user requested
        if args.user and user_id != args.user:
            continue
            
        if user_id not in users:
            users[user_id] = []
        users[user_id].append(data)
    
    if args.user and not users:
        print(f"⚠️  User {args.user} not found in recent data.")
        return

    print(f"✓ Processing {len(users)} users")
    print()
    
    # Generate dashboards for each user
    for user_id, user_data in users.items():
        print(f"👤 Generating dashboard for: {user_id}")
        
        # Analyze mental state
        analysis = analyze_mental_state(user_data)
        print(f"   State: {analysis['state']}")
        
        # Create output folder
        user_folder = os.path.join(OUTPUT_DIR, user_id.replace('/', '_'))
        os.makedirs(user_folder, exist_ok=True)
        
        # Create charts
        create_integrated_charts(user_id, user_data, user_folder)
        
        # Create text report
        create_integrated_report(user_id, user_data, analysis, user_folder)
        print(f"   ✓ Dashboard saved to: {user_folder}")
        print()
    
    print("=" * 60)
    print(f"✓ All dashboards generated successfully!")
    print(f"📁 Output directory: {OUTPUT_DIR}")

if __name__ == '__main__':
    main()
