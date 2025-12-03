"""
Test script for the Wellbeing Advisor
Run this to test wellbeing suggestions for a user
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wellbeing_advisor import WellbeingAdvisor

def test_wellbeing_advisor():
    """Test the wellbeing advisor with database"""
    
    # Database path
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'fer_events.db')
    SURVEY_PATH = os.path.join(BASE_DIR, 'survey_data.json')
    
    print("=" * 70)
    print("WELLBEING ADVISOR TEST")
    print("=" * 70)
    print(f"\nDatabase: {DB_PATH}")
    print(f"Survey Data: {SURVEY_PATH}")
    
    # Create advisor
    advisor = WellbeingAdvisor(DB_PATH, SURVEY_PATH)
    
    # Get a user ID from database
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT user_id, COUNT(*) as cnt FROM events GROUP BY user_id ORDER BY cnt DESC LIMIT 5")
    users = cursor.fetchall()
    conn.close()
    
    if not users:
        print("\n❌ No users found in database!")
        return
    
    print(f"\n📊 Found {len(users)} users in database")
    print("\nTop users:")
    for i, (user_id, count) in enumerate(users, 1):
        print(f"  {i}. {user_id} ({count} events)")
    
    # Test with first user
    test_user = users[0][0]
    print(f"\n{'=' * 70}")
    print(f"Testing with user: {test_user}")
    print("=" * 70)
    
    # Get suggestions
    result = advisor.get_suggestions(test_user, days=7)
    
    if not result.get('analysis'):
        print("\n⚠️ Not enough data for this user")
        return
    
    # Display results
    print(f"\n📈 ANALYSIS (Last 7 days)")
    print("-" * 70)
    analysis = result['analysis']
    print(f"Total Events: {analysis['total_events']}")
    print(f"Dominant Emotion: {analysis['dominant_emotion']}")
    print(f"Average Confidence: {analysis['avg_confidence']:.1f}%")
    print(f"\nEmotion Distribution:")
    for emotion, count in analysis['most_common_emotions'][:5]:
        print(f"  • {emotion}: {count} times")
    
    print(f"\nTime Distribution:")
    for period, count in analysis['time_distribution'].items():
        print(f"  • {period.capitalize()}: {count} events")
    
    print(f"\n\n💬 CONTEXT MESSAGE")
    print("-" * 70)
    print(result['context_message'])
    
    print(f"\n\n⚡ IMMEDIATE SUGGESTIONS")
    print("-" * 70)
    for i, suggestion in enumerate(result['immediate_suggestions'], 1):
        print(f"{i}. {suggestion}")
    
    print(f"\n\n📅 LONG-TERM STRATEGIES")
    print("-" * 70)
    for i, suggestion in enumerate(result['long_term_suggestions'], 1):
        print(f"{i}. {suggestion}")
    
    print("\n" + "=" * 70)
    print("✅ Test completed successfully!")
    print("=" * 70)

if __name__ == '__main__':
    test_wellbeing_advisor()
