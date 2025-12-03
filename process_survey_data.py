"""
Process survey data and create a wellbeing knowledge base
This script analyzes emotion-context patterns from survey responses
"""
import json
import csv
from collections import defaultdict

def process_survey_data(csv_file='survey_responses.csv'):
    """
    Extract patterns from survey data:
    - What contexts trigger each emotion
    - What helps people in specific emotional states
    """
    
    # Knowledge base structure
    knowledge_base = {
        'emotion_contexts': defaultdict(list),
        'suggestions': defaultdict(list),
        'patterns': []
    }
    
    # Predefined wellbeing suggestions based on common patterns
    wellbeing_strategies = {
        'Fear': [
            {
                'trigger': ['exam', 'test', 'evaluation', 'project'],
                'suggestions': [
                    '📚 Break your study into small chunks (Pomodoro technique: 25 min focus)',
                    '🧘 Try deep breathing: 4 seconds in, 7 hold, 8 out',
                    '💪 Remember: Preparation reduces anxiety. Make a simple checklist.',
                    '🤝 Talk to a friend who has been through this'
                ]
            },
            {
                'trigger': ['deadline', 'submission', 'presentation'],
                'suggestions': [
                    '📝 Write down exactly what needs to be done',
                    '⏰ Set realistic micro-goals for the next hour',
                    '🎯 Focus on progress, not perfection',
                    '🌿 Take a 5-minute walk to clear your mind'
                ]
            },
            {
                'trigger': ['general', 'unknown', 'default'],
                'suggestions': [
                    '🌸 Ground yourself: Name 5 things you can see right now',
                    '💭 Ask: "What is the worst that could happen? Can I handle it?"',
                    '🎵 Listen to calming music or nature sounds',
                    '📞 Reach out to someone you trust'
                ]
            }
        ],
        'Sad': [
            {
                'trigger': ['marks', 'grades', 'performance', 'QRA'],
                'suggestions': [
                    '💡 One result does not define you - it is data, not destiny',
                    '📈 Identify one specific thing to improve next time',
                    '🎯 Celebrate what you DID learn, even if grade was not perfect',
                    '🤗 Talk to your professor or TA about growth opportunities'
                ]
            },
            {
                'trigger': ['fight', 'argument', 'conflict', 'friend'],
                'suggestions': [
                    '💬 Give yourself time to cool down before responding',
                    '❤️ Remember: Good relationships survive disagreements',
                    '✍️ Write down your feelings (you do not have to send it)',
                    '🕊️ When ready, reach out with "Can we talk?"'
                ]
            },
            {
                'trigger': ['sleep', 'tired', 'exhausted', 'classes'],
                'suggestions': [
                    '😴 Prioritize 7-8 hours of sleep tonight - it is not lazy, it is essential',
                    '☕ Reduce caffeine after 2 PM',
                    '📵 Screen-free 30 mins before bed',
                    '🎧 Try a sleep meditation or calm podcast'
                ]
            },
            {
                'trigger': ['mood swings', 'do not know', 'no reason'],
                'suggestions': [
                    '🌈 Sadness without a reason is valid - emotions just happen',
                    '🏃 Move your body: 10-min walk can shift your mood',
                    '☀️ Get some sunlight or bright light exposure',
                    '🎨 Do something creative without judgment (doodle, music, cook)'
                ]
            }
        ],
        'Happy': [
            {
                'trigger': ['food', 'ate', 'tasty'],
                'suggestions': [
                    '😊 Enjoy this moment! Savor the good feeling',
                    '📸 Capture happy moments (photo, journal entry)',
                    '💫 Share your joy - tell someone what made you happy',
                    '🎉 Good food = good mood. Remember what works for you!'
                ]
            },
            {
                'trigger': ['friend', 'talked', 'conversation', 'Best friend'],
                'suggestions': [
                    '🥰 Quality connections boost wellbeing - schedule regular catch-ups',
                    '💌 Send a quick "that meant a lot to me" message',
                    '🔄 Good relationships are two-way - check in on them too',
                    '🌟 Cultivate friendships that energize you'
                ]
            },
            {
                'trigger': ['positive', 'grate', 'going well', 'mood'],
                'suggestions': [
                    '📝 Write down 3 specific things going well (for tough days)',
                    '🙏 Practice gratitude - it amplifies happiness',
                    '⚡ Use this positive energy for something you have been avoiding',
                    '🎁 Pay it forward - small acts of kindness boost happiness'
                ]
            }
        ],
        'Neutral': [
            {
                'trigger': ['general', 'default', 'me'],
                'suggestions': [
                    '🌿 Neutral is peaceful - no need to force emotions',
                    '🎯 Good time to plan or organize something',
                    '🧘 Try mindfulness: Just notice what you are experiencing',
                    '📚 Engage in a hobby or learn something new'
                ]
            }
        ],
        'Angry': [
            {
                'trigger': ['general', 'default'],
                'suggestions': [
                    '🔥 Pause before reacting - anger is information',
                    '🏃 Physical activity helps: run, dance, punch a pillow',
                    '🗣️ Express it safely: vent to a friend or journal',
                    '❓ Ask: "What boundary was crossed? What do I need?"'
                ]
            }
        ],
        'Disgust': [
            {
                'trigger': ['general', 'default'],
                'suggestions': [
                    '🧹 Sometimes disgust signals a need for change',
                    '🚪 Remove yourself from the triggering situation if possible',
                    '💭 Reflect: What value of mine is being violated?',
                    '🌊 Let the feeling pass like a wave - it will'
                ]
            }
        ],
        'Surprise': [
            {
                'trigger': ['general', 'default'],
                'suggestions': [
                    '✨ Surprise is brief - notice how you feel underneath',
                    '🎢 Life is unpredictable - embrace the unexpected',
                    '📖 Unexpected moments often become best memories',
                    '🧠 Stay curious about what happens next'
                ]
            }
        ]
    }
    
    try:
        # Read CSV file
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                timestamp = row.get('Timestamp', '')
                # Handle column names with trailing spaces
                emotion = row.get('What is your current emotion ?', '').strip()
                if not emotion:
                    emotion = row.get('What is your current emotion ? ', '').strip()
                reason = row.get('What is the reason for your selected emotion ?', '').strip()
                if not reason:
                    reason = row.get('What is the reason for your selected emotion ? ', '').strip()
                
                if emotion and reason:
                    knowledge_base['emotion_contexts'][emotion].append({
                        'reason': reason,
                        'timestamp': timestamp
                    })
                    
                    knowledge_base['patterns'].append({
                        'emotion': emotion,
                        'context': reason,
                        'timestamp': timestamp
                    })
    
    except FileNotFoundError:
        print("⚠️  CSV file not found. Using predefined knowledge base.")
    
    # Add wellbeing strategies to knowledge base
    knowledge_base['suggestions'] = wellbeing_strategies
    
    # Generate statistics
    stats = {
        'total_responses': len(knowledge_base['patterns']),
        'emotions_tracked': list(knowledge_base['emotion_contexts'].keys()),
        'emotion_distribution': {
            emotion: len(contexts) 
            for emotion, contexts in knowledge_base['emotion_contexts'].items()
        }
    }
    
    return knowledge_base, stats


def save_knowledge_base(knowledge_base, stats, output_file='wellbeing_knowledge.json'):
    """Save processed knowledge base to JSON"""
    
    output = {
        'metadata': {
            'source': 'Emotion Detection Study Survey',
            'generated': '2025-12-04',
            'description': 'Context-aware wellbeing suggestions based on peer survey data'
        },
        'statistics': stats,
        'knowledge_base': {
            'emotion_contexts': dict(knowledge_base['emotion_contexts']),
            'suggestions': knowledge_base['suggestions'],
            'patterns': knowledge_base['patterns']
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Knowledge base saved to {output_file}")
    print(f"\n📊 Statistics:")
    print(f"   Total responses: {stats['total_responses']}")
    print(f"   Emotions tracked: {', '.join(stats['emotions_tracked'])}")
    print(f"\n📈 Emotion distribution:")
    for emotion, count in stats['emotion_distribution'].items():
        print(f"   {emotion}: {count} responses")


if __name__ == '__main__':
    print("🔄 Processing survey data...\n")
    
    kb, stats = process_survey_data()
    save_knowledge_base(kb, stats)
    
    print("\n✨ Done! Now you can use this knowledge base for context-aware suggestions.")
