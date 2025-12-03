import random
import json
import sqlite3
from datetime import datetime, timedelta
from collections import Counter
import os

class WellbeingAdvisor:
    """Context-aware wellbeing suggestions based on survey data and emotion patterns"""
    
    def __init__(self, db_path='fer_events.db'):
        self.db_path = db_path
        # Context-aware suggestions based on survey data from your friends
        self.suggestions = {
            'Happy': {
                'contexts': {
                    'food': [
                        "🍽️ Your peers say: Good food = good mood! Savor this moment.",
                        "😊 Enjoy the positive feeling - mindful eating boosts happiness.",
                        "📸 Remember what works for you - keep a food-mood journal!",
                        "💫 Share the joy - recommend your favorite food to a friend."
                    ],
                    'friend': [
                        "🥰 Survey insight: Quality connections boost wellbeing!",
                        "💌 Your peers value this - send a quick 'thank you for being you' message.",
                        "🔄 Good relationships are two-way - check in on them too.",
                        "🌟 Schedule regular catch-ups to maintain this positive energy."
                    ],
                    'positive_mood': [
                        "📝 From survey: Write down 3 things going well (for tough days).",
                        "🙏 Your friends practice gratitude - it amplifies happiness!",
                        "⚡ Use this positive energy for something you've been avoiding.",
                        "🎁 Pay it forward - small acts of kindness boost happiness."
                    ],
                    'default': [
                        "🌟 Great mood! Share your positivity with others.",
                        "😊 Document what's making you happy - future you will thank you.",
                        "✨ This is great energy for tackling challenging tasks!",
                        "💫 Savor this feeling - positive emotions are energizing."
                    ]
                }
            },
            'Sad': {
                'contexts': {
                    'marks': [
                        "💡 Survey wisdom: One result doesn't define you - it's data, not destiny.",
                        "📈 Your peers suggest: Identify ONE specific thing to improve next time.",
                        "🎯 Focus on what you DID learn, even if the grade wasn't perfect.",
                        "🤗 Talk to your professor about growth opportunities."
                    ],
                    'fight': [
                        "💬 From your peers: Give yourself time to cool down before responding.",
                        "❤️ Survey insight: Good relationships survive disagreements.",
                        "✍️ Write down your feelings (you don't have to send it).",
                        "🕊️ When ready, reach out with 'Can we talk?'"
                    ],
                    'sleep': [
                        "😴 Survey data shows: Prioritize 7-8 hours tonight - it's essential!",
                        "☕ Your peers recommend: Reduce caffeine after 2 PM.",
                        "📵 Try screen-free 30 mins before bed.",
                        "🎧 Many find sleep meditation or calm podcasts helpful."
                    ],
                    'classes': [
                        "📚 From peers: Break overwhelming tasks into 25-min chunks (Pomodoro).",
                        "🗓️ Survey insight: One step at a time reduces overwhelm.",
                        "🤝 Study groups can help - you're not alone in this!",
                        "☀️ Take breaks - burnout helps nobody."
                    ],
                    'mood_swings': [
                        "🌈 Survey wisdom: Sadness without a reason is valid - emotions just happen.",
                        "🏃 Your peers find: 10-min walk can shift mood significantly.",
                        "☀️ Get some sunlight or bright light exposure.",
                        "🎨 Do something creative without judgment (doodle, music, cook)."
                    ],
                    'default': [
                        "🫂 It's okay to feel this way. Be kind to yourself.",
                        "💙 Consider reaching out to someone you trust.",
                        "🎵 Try gentle movement or uplifting music.",
                        "🌸 Remember: emotions are temporary. This will pass."
                    ]
                }
            },
            'Fear': {
                'contexts': {
                    'exam': [
                        "📚 Survey insight: Break your study into small chunks (Pomodoro: 25 min focus).",
                        "🧘 Peers recommend: Deep breathing - 4 sec in, 7 hold, 8 out.",
                        "💪 Your friends say: Preparation reduces anxiety. Make a simple checklist.",
                        "🤝 Talk to someone who has been through this exam."
                    ],
                    'project': [
                        "📝 From survey: Write down exactly what needs to be done.",
                        "⏰ Set realistic micro-goals for the next hour.",
                        "🎯 Peers say: Focus on progress, not perfection.",
                        "🌿 Take a 5-minute walk to clear your mind."
                    ],
                    'evaluation': [
                        "💭 Survey wisdom: Prepare what you CAN control, release what you can't.",
                        "📊 Break it down: What are you being evaluated on? Prioritize.",
                        "🗣️ Practice explaining your work to a friend.",
                        "😌 Your peers find meditation before evaluations helpful."
                    ],
                    'default': [
                        "🌸 Ground yourself: Name 5 things you can see right now.",
                        "💭 Ask: 'What's the worst that could happen? Can I handle it?'",
                        "🫁 Practice box breathing: Inhale-4, Hold-4, Exhale-4, Hold-4.",
                        "📞 Reach out to someone you trust if the feeling persists."
                    ]
                }
            },
            'Angry': {
                'contexts': {
                    'default': [
                        "🔥 Pause before reacting - anger is information about boundaries.",
                        "🏃 Physical activity helps: run, dance, punch a pillow safely.",
                        "🗣️ Express it safely: vent to a friend or journal it out.",
                        "❓ Ask: 'What boundary was crossed? What do I need?'"
                    ]
                }
            },
            'Neutral': {
                'contexts': {
                    'default': [
                        "🌿 Neutral is peaceful - no need to force emotions.",
                        "🎯 Good time to plan or organize something.",
                        "🧘 Try mindfulness: Just notice what you're experiencing.",
                        "📚 Perfect state for learning or tackling routine tasks."
                    ]
                }
            },
            'Disgust': {
                'contexts': {
                    'default': [
                        "🧹 Sometimes disgust signals a need for change.",
                        "🚪 Remove yourself from the triggering situation if possible.",
                        "💭 Reflect: What value of mine is being violated?",
                        "🌊 Let the feeling pass like a wave - it will."
                    ]
                }
            },
            'Surprise': {
                'contexts': {
                    'default': [
                        "✨ Unexpected moment! Take time to process this.",
                        "🎢 Life is unpredictable - embrace it!",
                "📖 Unexpected moments often become best memories.",
                        "🧠 Stay curious about what happens next."
                    ]
                }
            }
        }
    
    def _detect_context(self, user_id, days=7):
        """Analyze recent user patterns to detect context keywords"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            cursor.execute('''
                SELECT emotion, timestamp
                FROM emotions
                WHERE user_id = ? AND timestamp > ?
                ORDER BY timestamp DESC
                LIMIT 50
            ''', (user_id, cutoff))
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return None
            
            # Analyze patterns
            emotions = [row[0] for row in rows]
            timestamps = [datetime.fromisoformat(row[1]) for row in rows]
            
            # Detect time-based context
            hours = [ts.hour for ts in timestamps]
            avg_hour = sum(hours) / len(hours)
            
            # Detect emotion frequency
            emotion_counts = Counter(emotions)
            most_common = emotion_counts.most_common(1)[0][0]
            
            # Context keywords
            context = {
                'dominant_emotion': most_common,
                'recent_emotion': emotions[0] if emotions else 'Neutral',
                'time_period': 'morning' if avg_hour < 12 else 'afternoon' if avg_hour < 18 else 'evening',
                'frequency': len(rows),
                'diversity': len(set(emotions))
            }
            
            return context
            
        except Exception as e:
            print(f"Context detection error: {e}")
            return None
    
    def get_suggestions(self, emotion, context=None):
        """Get context-aware suggestions for an emotion"""
        if emotion not in self.suggestions:
            emotion = 'Neutral'
        
        emotion_data = self.suggestions[emotion]
        
        # If we have context information, try to match it
        if context and 'contexts' in emotion_data:
            contexts = emotion_data['contexts']
            
            # Try to match context keywords
            context_matches = []
            for ctx_key in contexts.keys():
                if ctx_key in str(context).lower():
                    context_matches.append(ctx_key)
            
            # Return matched context suggestions
            if context_matches:
                chosen_context = context_matches[0]
                return random.sample(contexts[chosen_context], min(4, len(contexts[chosen_context])))
            
            # Return default context for this emotion
            if 'default' in contexts:
                return random.sample(contexts['default'], min(4, len(contexts['default'])))
        
        # Fallback to any suggestions available
        if 'contexts' in emotion_data and 'default' in emotion_data['contexts']:
            return random.sample(emotion_data['contexts']['default'], 
                               min(4, len(emotion_data['contexts']['default'])))
        
        return ["Take a moment to reflect on your feelings."]
    
    def get_user_emotion_patterns(self, user_id, days=7):
        """Analyze user's emotion patterns"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            cursor.execute('''
                SELECT emotion, confidence, timestamp
                FROM emotions
                WHERE user_id = ? AND timestamp > ?
                ORDER BY timestamp DESC
            ''', (user_id, cutoff))
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return None
            
            emotions = [row[0] for row in rows]
            confidences = [row[1] for row in rows]
            timestamps = [datetime.fromisoformat(row[2]) for row in rows]
            
            emotion_counts = Counter(emotions)
            most_common = emotion_counts.most_common(1)[0][0]
            
            # Recent trend
            recent_cutoff = datetime.now() - timedelta(hours=24)
            recent_emotions = [e for e, ts in zip(emotions, timestamps) if ts > recent_cutoff]
            
            return {
                'total_events': len(rows),
                'most_common_emotion': most_common,
                'recent_emotion': recent_emotions[0] if recent_emotions else most_common,
                'emotion_distribution': dict(emotion_counts),
                'avg_confidence': sum(confidences) / len(confidences) if confidences else 0,
                'last_seen': timestamps[0].isoformat()
            }
        except Exception as e:
            print(f"Pattern analysis error: {e}")
            return None
    
    def generate_wellbeing_report(self, user_id):
        """Generate comprehensive wellbeing report with context-aware suggestions"""
        patterns = self.get_user_emotion_patterns(user_id)
        context = self._detect_context(user_id)
        
        if not patterns:
            return {
                'status': 'no_data',
                'message': 'No emotion data available yet.',
                'suggestions': [
                    '👋 Start using emotion detection to get personalized insights!',
                    '📊 Your wellbeing suggestions improve as we learn your patterns.',
                    '💡 Check back after a few days of usage.'
                ]
            }
        
        # Get context-aware suggestions
        primary_emotion = patterns['most_common_emotion']
        recent_emotion = patterns['recent_emotion']
        
        primary_suggestions = self.get_suggestions(primary_emotion, context)
        recent_suggestions = self.get_suggestions(recent_emotion, context)
        
        # Generate insights
        insights = []
        emotion_pct = (patterns['emotion_distribution'][primary_emotion] / patterns['total_events']) * 100
        insights.append(f"📊 Past week: **{primary_emotion}** dominated ({emotion_pct:.0f}% of readings)")
        
        if recent_emotion != primary_emotion:
            insights.append(f"🔄 Recently shifting to: **{recent_emotion}**")
        
        if context:
            insights.append(f"⏰ Most active during {context['time_period']}")
        
        return {
            'status': 'success',
            'user_id': user_id,
            'patterns': patterns,
            'context': context,
            'insights': insights,
            'primary_suggestions': {
                'title': f'For {primary_emotion} (your main emotion):',
                'emotion': primary_emotion,
                'tips': primary_suggestions
            },
            'recent_suggestions': {
                'title': f'Right now ({recent_emotion}):',
                'emotion': recent_emotion,
                'tips': recent_suggestions
            },
            'general_tips': [
                '🌱 Your peers shared: Track patterns to understand triggers',
                '💪 Survey insight: Small consistent actions > big occasional efforts',
                '🤝 Remember: Your wellbeing matters - reach out when needed'
            ]
        }
    
    def get_daily_tip(self):
        """Get a general mental health tip"""
        tips = [
            "💧 Stay hydrated - it affects mood!",
            "☀️ Try to get some natural sunlight today.",
            "😴 Quality sleep is crucial for emotional regulation.",
            "🥗 Eating well supports mental health.",
            "🤝 Social connection is vital - reach out!",
            "🏃 Even 10 minutes of movement boosts mood.",
            "📵 Take breaks from screens.",
            "🙏 Practice gratitude daily.",
            "🎨 Engage in creative activities.",
            "🌱 Small self-care acts add up!"
        ]
        return random.choice(tips)


# Test function
if __name__ == '__main__':
    print("🧪 Testing Context-Aware Wellbeing Advisor\n")
    
    advisor = WellbeingAdvisor()
    
    # Test with a sample user
    test_user = "fer_webapp_42271439d4380a17"
    
    report = advisor.generate_wellbeing_report(test_user)
    
    print(f"Status: {report['status']}\n")
    
    if report['status'] == 'success':
        print("📊 INSIGHTS:")
        for insight in report['insights']:
            print(f"   {insight}")
        
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
        print(f"Message: {report['message']}")
        for suggestion in report.get('suggestions', []):
            print(f"   • {suggestion}")
    
    print(f"\n💬 Daily Tip: {advisor.get_daily_tip()}")
