"""
Context-Aware Wellbeing Advisor
Uses user emotion patterns and survey data to provide personalized suggestions
"""

import sqlite3
from datetime import datetime, timedelta
from collections import Counter
import json

class WellbeingAdvisor:
    def __init__(self, db_path, survey_data_path=None):
        self.db_path = db_path
        self.survey_data = self._load_survey_data(survey_data_path) if survey_data_path else self._default_suggestions()
    
    def _load_survey_data(self, path):
        """Load survey data from JSON file"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            return self._default_suggestions()
    
    def _default_suggestions(self):
        """Default wellbeing suggestions based on emotions"""
        return {
            "Sad": {
                "immediate": [
                    "Take a short walk outside to get fresh air",
                    "Listen to uplifting music",
                    "Reach out to a friend or family member",
                    "Practice deep breathing for 5 minutes"
                ],
                "long_term": [
                    "Establish a regular exercise routine",
                    "Keep a gratitude journal",
                    "Ensure 7-8 hours of sleep daily",
                    "Join a social group or club"
                ]
            },
            "Angry": {
                "immediate": [
                    "Take 10 deep breaths before responding",
                    "Go for a brisk walk or run",
                    "Write down your feelings in a journal",
                    "Listen to calming music"
                ],
                "long_term": [
                    "Practice meditation or mindfulness",
                    "Identify triggers and plan coping strategies",
                    "Regular physical exercise",
                    "Seek professional counseling if needed"
                ]
            },
            "Fear": {
                "immediate": [
                    "Ground yourself: name 5 things you see, 4 you hear, 3 you feel",
                    "Practice box breathing (4-4-4-4 pattern)",
                    "Talk to someone you trust",
                    "Focus on what you can control"
                ],
                "long_term": [
                    "Gradual exposure to feared situations",
                    "Build a support network",
                    "Learn stress management techniques",
                    "Consider therapy (CBT is effective for anxiety)"
                ]
            },
            "Happy": {
                "immediate": [
                    "Share your joy with others",
                    "Document what made you happy today",
                    "Use this positive energy productively",
                    "Plan an activity you enjoy"
                ],
                "long_term": [
                    "Identify what triggers happiness for you",
                    "Create more opportunities for these activities",
                    "Practice gratitude regularly",
                    "Help others to amplify positive feelings"
                ]
            },
            "Neutral": {
                "immediate": [
                    "Check in with yourself: how are you really feeling?",
                    "Try something new to spark interest",
                    "Connect with a friend",
                    "Set a small achievable goal for today"
                ],
                "long_term": [
                    "Explore new hobbies or interests",
                    "Build meaningful relationships",
                    "Set personal growth goals",
                    "Practice mindfulness to increase awareness"
                ]
            },
            "Surprise": {
                "immediate": [
                    "Take a moment to process the situation",
                    "Reflect on whether this is positive or negative",
                    "Share the experience with someone",
                    "Write about what surprised you"
                ],
                "long_term": [
                    "Embrace spontaneity in safe ways",
                    "Practice adaptability",
                    "Keep an open mind to new experiences",
                    "Build resilience to handle unexpected situations"
                ]
            },
            "Disgust": {
                "immediate": [
                    "Remove yourself from the triggering situation",
                    "Practice acceptance of what you cannot change",
                    "Focus on something pleasant",
                    "Talk to someone about your feelings"
                ],
                "long_term": [
                    "Identify patterns in what triggers disgust",
                    "Practice emotional regulation",
                    "Set healthy boundaries",
                    "Work on acceptance and tolerance"
                ]
            }
        }
    
    def analyze_user_patterns(self, user_id, days=7):
        """Analyze user's emotion patterns over the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        cursor.execute("""
            SELECT emotion, ts_received, confidence 
            FROM events 
            WHERE user_id = ? AND ts_received >= ?
            ORDER BY ts_received ASC
        """, (user_id, cutoff))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return None
        
        emotions = [r[0] for r in rows]
        timestamps = [r[1] for r in rows]
        confidences = [r[2] for r in rows]
        
        # Analyze patterns
        emotion_counts = Counter(emotions)
        most_common = emotion_counts.most_common(3)
        
        # Time of day analysis
        hours = []
        for ts_str in timestamps:
            try:
                ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                hours.append(ts.hour)
            except:
                continue
        
        morning = sum(1 for h in hours if 6 <= h < 12)
        afternoon = sum(1 for h in hours if 12 <= h < 18)
        evening = sum(1 for h in hours if 18 <= h < 24)
        night = sum(1 for h in hours if 0 <= h < 6)
        
        return {
            'total_events': len(emotions),
            'most_common_emotions': most_common,
            'dominant_emotion': most_common[0][0] if most_common else 'Neutral',
            'avg_confidence': sum(confidences) / len(confidences) if confidences else 0,
            'time_distribution': {
                'morning': morning,
                'afternoon': afternoon,
                'evening': evening,
                'night': night
            },
            'days_analyzed': days
        }
    
    def get_suggestions(self, user_id, days=7):
        """Generate personalized wellbeing suggestions"""
        patterns = self.analyze_user_patterns(user_id, days)
        
        if not patterns:
            return {
                'message': 'Not enough data yet. Keep using the app!',
                'suggestions': []
            }
        
        dominant = patterns['dominant_emotion']
        total = patterns['total_events']
        time_dist = patterns['time_distribution']
        
        # Get suggestions for dominant emotion
        emotion_suggestions = self.survey_data.get(dominant, self.survey_data.get('Neutral', {}))
        
        # Build context-aware message
        context_msg = self._build_context_message(patterns)
        
        # Combine suggestions
        immediate = emotion_suggestions.get('immediate', [])
        long_term = emotion_suggestions.get('long_term', [])
        
        return {
            'analysis': patterns,
            'context_message': context_msg,
            'immediate_suggestions': immediate[:3],  # Top 3
            'long_term_suggestions': long_term[:3],  # Top 3
            'dominant_emotion': dominant
        }
    
    def _build_context_message(self, patterns):
        """Build a personalized context message"""
        dominant = patterns['dominant_emotion']
        total = patterns['total_events']
        days = patterns['days_analyzed']
        time_dist = patterns['time_distribution']
        
        # Find peak time
        peak_time = max(time_dist, key=time_dist.get)
        
        messages = [
            f"Over the last {days} days, we analyzed {total} emotion events.",
            f"Your most common emotion was **{dominant}**."
        ]
        
        if peak_time == 'morning':
            messages.append("You tend to be most active in the morning (6 AM - 12 PM).")
        elif peak_time == 'afternoon':
            messages.append("You tend to be most active in the afternoon (12 PM - 6 PM).")
        elif peak_time == 'evening':
            messages.append("You tend to be most active in the evening (6 PM - 12 AM).")
        elif peak_time == 'night':
            messages.append("You tend to be most active at night (12 AM - 6 AM). Consider adjusting your sleep schedule!")
        
        return ' '.join(messages)


def generate_wellbeing_report(db_path, user_id, output_file=None):
    """Generate a complete wellbeing report for a user"""
    advisor = WellbeingAdvisor(db_path)
    result = advisor.get_suggestions(user_id)
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
    
    return result


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python wellbeing_advisor.py <database_path> <user_id> [output_file]")
        sys.exit(1)
    
    db_path = sys.argv[1]
    user_id = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    report = generate_wellbeing_report(db_path, user_id, output_file)
    
    print("\n" + "="*60)
    print("WELLBEING ANALYSIS & SUGGESTIONS")
    print("="*60)
    print(f"\nUser: {user_id}")
    print(f"\n{report['context_message']}")
    print(f"\n🎯 Immediate Actions (Try these now):")
    for i, suggestion in enumerate(report['immediate_suggestions'], 1):
        print(f"   {i}. {suggestion}")
    
    print(f"\n📅 Long-term Strategies (Build these habits):")
    for i, suggestion in enumerate(report['long_term_suggestions'], 1):
        print(f"   {i}. {suggestion}")
    
    print("\n" + "="*60)
