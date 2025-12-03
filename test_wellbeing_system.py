"""
Test the context-aware wellbeing system
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from wellbeing_advisor import WellbeingAdvisor

def test_wellbeing_system():
    print("=" * 60)
    print("🧪 TESTING CONTEXT-AWARE WELLBEING SYSTEM")
    print("=" * 60)
    
    # Initialize advisor
    db_path = os.path.join(os.path.dirname(__file__), 'fer_events.db')
    advisor = WellbeingAdvisor(db_path=db_path)
    
    print(f"\n✅ Advisor initialized with database: {db_path}")
    
    # Test 1: Get suggestions for specific emotions
    print("\n" + "=" * 60)
    print("TEST 1: Emotion-specific suggestions")
    print("=" * 60)
    
    emotions_to_test = ['Happy', 'Sad', 'Fear', 'Angry']
    
    for emotion in emotions_to_test:
        suggestions = advisor.get_suggestions(emotion)
        print(f"\n🎯 {emotion}:")
        for i, suggestion in enumerate(suggestions[:3], 1):
            print(f"   {i}. {suggestion}")
    
    # Test 2: Context-aware suggestions
    print("\n" + "=" * 60)
    print("TEST 2: Context-aware suggestions (Sad + exam context)")
    print("=" * 60)
    
    sad_exam_context = "exam project evaluation"
    sad_suggestions = advisor.get_suggestions('Sad', sad_exam_context)
    print(f"\n🎯 Sad (context: {sad_exam_context}):")
    for i, suggestion in enumerate(sad_suggestions, 1):
        print(f"   {i}. {suggestion}")
    
    # Test 3: Full wellbeing report for a user
    print("\n" + "=" * 60)
    print("TEST 3: Full wellbeing report for a user")
    print("=" * 60)
    
    # Try to get first user from database
    import sqlite3
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT user_id FROM emotions LIMIT 1')
        result = cursor.fetchone()
        conn.close()
        
        if result:
            test_user_id = result[0]
            print(f"\n📊 Generating report for user: {test_user_id}")
            
            report = advisor.generate_wellbeing_report(test_user_id)
            
            print(f"\nStatus: {report['status']}")
            
            if report['status'] == 'success':
                print("\n📈 INSIGHTS:")
                for insight in report['insights']:
                    print(f"   • {insight}")
                
                print(f"\n💡 {report['primary_suggestions']['title']}")
                for tip in report['primary_suggestions']['tips']:
                    print(f"   • {tip}")
                
                print(f"\n🎯 {report['recent_suggestions']['title']}")
                for tip in report['recent_suggestions']['tips']:
                    print(f"   • {tip}")
                
                print("\n🌟 GENERAL TIPS:")
                for tip in report['general_tips']:
                    print(f"   • {tip}")
            else:
                print(f"\nMessage: {report['message']}")
                for suggestion in report.get('suggestions', []):
                    print(f"   • {suggestion}")
        else:
            print("\n⚠️  No users found in database. Skipping user-specific test.")
            
    except Exception as e:
        print(f"\n⚠️  Could not access database: {e}")
        print("Skipping user-specific test.")
    
    # Test 4: Daily tip
    print("\n" + "=" * 60)
    print("TEST 4: Daily wellbeing tip")
    print("=" * 60)
    print(f"\n💬 {advisor.get_daily_tip()}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Download your Google Sheets survey data as CSV")
    print("2. Save it as 'survey_responses.csv' in this directory")
    print("3. Run: python process_survey_data.py")
    print("4. Deploy to Raspberry Pi: git add ., git commit, git push")
    print("5. On Pi: git pull, restart dashboard_server.py")
    print("6. View dashboard to see context-aware suggestions!")


if __name__ == '__main__':
    test_wellbeing_system()
