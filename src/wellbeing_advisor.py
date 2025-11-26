import random
from datetime import datetime

class WellbeingAdvisor:
    """Provides personalized wellbeing suggestions based on detected emotions"""
    
    def __init__(self):
        self.suggestions = {
            'Happy': [
                "🌟 Great mood! Consider sharing your positivity with others.",
                "😊 Keep up the good vibes! Maybe try a new activity you've been curious about.",
                "✨ Wonderful energy! Document what's making you happy today.",
                "🎉 Fantastic! This is a great time to tackle challenging tasks.",
                "💫 Your positive energy is powerful - spread it around!"
            ],
            'Sad': [
                "🫂 It's okay to feel this way. Take a short break and practice deep breathing.",
                "💙 Consider reaching out to a friend or loved one for support.",
                "🎵 Listen to uplifting music or go for a gentle walk outside.",
                "🌸 Remember: emotions are temporary. Be kind to yourself right now.",
                "📝 Try journaling your thoughts - it can help process feelings.",
                "☕ Take a moment for self-care - a warm drink, soft music, or a cozy blanket."
            ],
            'Angry': [
                "🌬️ Take 5 deep breaths. Inhale for 4, hold for 4, exhale for 4.",
                "🚶 Step away from the situation if possible. A short walk can help.",
                "💪 Try progressive muscle relaxation - tense and release each muscle group.",
                "🏃 Channel this energy into physical activity like exercise or stretching.",
                "🧘 Count to 10 slowly before responding. Give yourself space to calm down.",
                "🎯 Identify what triggered this feeling and consider healthy ways to address it."
            ],
            'Fear': [
                "🌍 Ground yourself: Name 5 things you see, 4 you touch, 3 you hear.",
                "🫁 Practice box breathing: Inhale-4, Hold-4, Exhale-4, Hold-4.",
                "🛡️ Remember: You are safe in this moment. This feeling will pass.",
                "💬 Consider talking to someone you trust about what you're feeling.",
                "🌱 Focus on what you CAN control right now, not the 'what ifs'.",
                "✋ Place your hand on your heart and feel it beating - you're here, you're safe."
            ],
            'Neutral': [
                "⚖️ Steady state. Consider setting a small, achievable goal for today.",
                "🎯 Good baseline mood. Perfect time for planning or reflection.",
                "🌟 Balanced energy - maybe try something new to spark some joy!",
                "📚 This is a great time for learning or tackling routine tasks.",
                "🧩 Stable mood is good! Use this time productively."
            ],
            'Surprise': [
                "✨ Unexpected moment! Take time to process this new information.",
                "🌈 Embrace the novelty and stay present with what you're experiencing.",
                "📖 Capture this feeling through journaling or talking with someone.",
                "🎭 Surprises can be opportunities - stay open and curious!",
                "🔍 Reflect on what surprised you and what you can learn from it."
            ],
            'Disgust': [
                "🚪 Step away from the trigger if possible. Give yourself some distance.",
                "🧘 Practice acceptance - not everything needs your judgment right now.",
                "🧹 Cleanse your space or engage in a calming, refreshing activity.",
                "🌊 Wash your hands mindfully - sometimes physical rituals help reset.",
                "🌿 Focus on something pleasant - a favorite scent, taste, or sight."
            ]
        }
        
        # Extended suggestions for persistent patterns
        self.pattern_suggestions = {
            'Sad': [
                "You've been feeling down for a while. Consider talking to a mental health professional.",
                "Persistent sadness may benefit from professional support. You don't have to face this alone.",
                "If these feelings continue, reaching out to a counselor or therapist can really help."
            ],
            'Angry': [
                "Frequent anger might indicate underlying stress. Consider stress management techniques.",
                "If anger is persistent, it might help to explore the root causes with a professional.",
                "Regular anger can impact wellbeing. Anger management strategies could be beneficial."
            ],
            'Fear': [
                "Ongoing anxiety or fear is worth discussing with a healthcare provider.",
                "Persistent worry can be managed. Consider speaking with a mental health professional.",
                "If fear is interfering with daily life, professional support can make a real difference."
            ]
        }
    
    def get_suggestion(self, emotion):
        """
        Get a personalized wellbeing suggestion
        Args:
            emotion: Detected emotion string
        Returns:
            Suggestion text
        """
        suggestions = self.suggestions.get(emotion, 
                                          ["🧠 Stay mindful and present in this moment."])
        return random.choice(suggestions)
    
    def get_pattern_suggestion(self, emotion, frequency_threshold=0.6):
        """
        Get suggestion for persistent emotional patterns
        Args:
            emotion: Dominant emotion
            frequency_threshold: Threshold for 'persistent' (0-1)
        Returns:
            Pattern-based suggestion or None
        """
        if emotion in self.pattern_suggestions:
            return random.choice(self.pattern_suggestions[emotion])
        return None
    
    def get_pattern_analysis(self, emotion_history):
        """
        Analyze emotional patterns over time
        Args:
            emotion_history: List of recent emotions
        Returns:
            Analysis text
        """
        if not emotion_history:
            return "Insufficient data for analysis."
        
        from collections import Counter
        
        counts = Counter(emotion_history)
        total = len(emotion_history)
        
        analysis = "📊 Emotional Pattern Analysis:\n"
        analysis += "-" * 40 + "\n"
        
        for emotion, count in counts.most_common():
            percentage = (count / total) * 100
            bar = "█" * int(percentage / 5)  # Visual bar
            analysis += f"{emotion:10s}: {bar} {percentage:.1f}%\n"
        
        # Identify dominant emotion
        dominant = counts.most_common(1)[0]
        dominant_emotion = dominant[0]
        dominant_pct = (dominant[1] / total) * 100
        
        analysis += "\n"
        
        # Provide insights
        if dominant_pct > 60:
            analysis += f"⚠️  You've been mostly {dominant_emotion.lower()} recently.\n"
            pattern_sug = self.get_pattern_suggestion(dominant_emotion)
            if pattern_sug:
                analysis += f"💡 {pattern_sug}\n"
        elif len(counts) > 5:
            analysis += "🎭 Your emotions have been quite varied - that's normal!\n"
        else:
            analysis += "✅ Your emotional state shows healthy variation.\n"
        
        return analysis
    
    def get_daily_tip(self):
        """Get a general mental health tip for the day"""
        tips = [
            "💧 Stay hydrated - it affects mood more than you think!",
            "☀️ Try to get some natural sunlight today.",
            "😴 Quality sleep is crucial for emotional regulation.",
            "🥗 Eating well supports mental health as much as physical.",
            "🤝 Social connection is vital - reach out to someone today.",
            "🏃 Even 10 minutes of movement can boost your mood.",
            "📵 Take breaks from screens - your mind will thank you.",
            "🙏 Practice gratitude - name 3 things you're thankful for.",
            "🎨 Engage in a creative activity, even for just 5 minutes.",
            "🌱 Small acts of self-care add up to big changes."
        ]
        return random.choice(tips)
    
    def get_timestamp(self):
        """Get current timestamp for logging"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")