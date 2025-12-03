# Context-Aware Wellbeing Suggestion System

## Overview
This system provides **personalized wellbeing suggestions** based on:
1. **User's emotion patterns** from the emotion detection system
2. **Survey data from peers** who shared what helps them in different emotional states
3. **Contextual matching** - suggestions adapt based on time patterns and emotion frequency

## Key Features

### 📊 Pattern Analysis
- Analyzes the user's last 7 days of emotion data
- Identifies dominant emotions and recent trends
- Detects time-of-day patterns (morning, afternoon, evening)

### 🎯 Context-Aware Suggestions
The system matches emotions with specific contexts:

**Fear Context:**
- `exam`, `project`, `evaluation` → Study strategies, breathing exercises
- `default` → Grounding techniques, asking supportive questions

**Sad Context:**
- `marks`, `grades` → Growth mindset, learning from feedback
- `fight`, `friend` → Conflict resolution, communication tips
- `sleep`, `tired` → Sleep hygiene, energy management
- `mood_swings` → Validation, gentle activities

**Happy Context:**
- `food` → Savoring moments, capturing joy
- `friend` → Relationship building, gratitude
- `positive_mood` → Amplifying happiness, paying it forward

### 💡 Peer-Based Insights
All suggestions are prefixed with phrases like:
- "Survey insight: ..."
- "Your peers recommend: ..."
- "From survey data: ..."

This reminds users that these tips come from **real people** who experienced similar emotions.

## How to Use

### Step 1: Download Survey Data
1. Open your Google Sheets survey responses
2. **File → Download → Comma-separated values (.csv)**
3. Save as `survey_responses.csv` in the project root

### Step 2: Process Survey Data (Optional)
```bash
python process_survey_data.py
```
This creates `wellbeing_knowledge.json` with processed patterns (though the system has built-in suggestions already).

### Step 3: Test Locally
```bash
python test_wellbeing_system.py
```

### Step 4: Deploy to Raspberry Pi
```bash
git add .
git commit -m "Add context-aware wellbeing suggestions"
git push
```

On the Pi:
```bash
cd ~/IOT_Project
git pull
sudo systemctl restart dashboard_server  # or restart manually
```

### Step 5: View in Dashboard
1. Open your dashboard: `http://<pi-ip>:5000/user/<your-user-id>`
2. Scroll to the **"Context-Aware Wellbeing Guide"** section
3. See personalized suggestions based on your emotion patterns!

## API Endpoint

### GET `/api/user/<user_id>/wellbeing`

**Response (success):**
```json
{
  "status": "success",
  "user_id": "fer_webapp_...",
  "patterns": {
    "total_events": 234,
    "most_common_emotion": "Happy",
    "recent_emotion": "Neutral",
    "emotion_distribution": {"Happy": 120, "Sad": 50, ...},
    "avg_confidence": 0.89
  },
  "insights": [
    "📊 Past week: **Happy** dominated (51% of readings)",
    "⏰ Most active during evening"
  ],
  "primary_suggestions": {
    "title": "For Happy (your main emotion):",
    "emotion": "Happy",
    "tips": [
      "😊 Enjoy this moment! Savor the good feeling",
      "📸 Capture happy moments (photo, journal entry)",
      ...
    ]
  },
  "recent_suggestions": {
    "title": "Right now (Neutral):",
    "emotion": "Neutral",
    "tips": [...]
  },
  "general_tips": [
    "🌱 Your peers shared: Track patterns to understand triggers",
    ...
  ]
}
```

**Response (no data):**
```json
{
  "status": "no_data",
  "message": "No emotion data available yet.",
  "suggestions": [
    "👋 Start using emotion detection to get personalized insights!",
    ...
  ]
}
```

## Code Structure

### `src/wellbeing_advisor.py`
Main class that:
- Loads emotion data from SQLite database
- Analyzes patterns (dominant emotion, time-of-day, trends)
- Matches emotions to contextual suggestions
- Generates comprehensive wellbeing reports

### `dashboard_server.py`
- Added API endpoint: `/api/user/<user_id>/wellbeing`
- Returns JSON with suggestions for dashboard

### `webapp/dashboard.html`
- `loadWellbeingSuggestions()` function
- Displays insights and suggestions in cards
- Shows disclaimer about non-medical advice

### `process_survey_data.py` (optional)
- Processes survey CSV data
- Creates knowledge base JSON
- Currently, built-in suggestions work without this

### `test_wellbeing_system.py`
- Tests emotion-specific suggestions
- Tests context-aware matching
- Tests full user report generation

## Customization

### Add New Emotion Contexts
Edit `src/wellbeing_advisor.py`:

```python
'Sad': {
    'contexts': {
        'your_new_context': [
            "💡 Survey insight: Your tip here",
            "🎯 Another helpful suggestion",
            ...
        ],
        ...
    }
}
```

### Adjust Analysis Window
Change the default 7-day window:

```python
advisor.generate_wellbeing_report(user_id, days=14)  # 2 weeks
```

## Important Notes

⚠️ **Not Medical Advice**
- Suggestions are peer-sourced and pattern-based
- Always includes disclaimer in UI
- Recommends professional help for persistent issues

🔒 **Privacy**
- Processes emotion patterns, not personal content
- Survey data is anonymized peer responses
- All analysis happens server-side (Pi)

🎓 **Educational Use**
- Perfect for IoT/emotion detection projects
- Demonstrates context-aware AI suggestions
- Shows practical use of survey data

## Troubleshooting

**"Could not load wellbeing suggestions"**
- Check dashboard_server.py is running on Pi
- Verify `/api/user/<id>/wellbeing` endpoint is accessible
- Check browser console for detailed error

**"No emotion data available yet"**
- Use the emotion detection app to collect data
- Wait 24-48 hours for meaningful patterns
- Check database has entries: `sqlite3 fer_events.db "SELECT COUNT(*) FROM emotions;"`

**Suggestions seem generic**
- Need more emotion events for context detection
- Ensure multiple emotions are being detected
- Check if time-of-day varies in your usage

## Future Enhancements

- [ ] Add more survey responses for richer context
- [ ] Implement ML to learn which suggestions users find helpful
- [ ] Add "Was this helpful?" feedback buttons
- [ ] Track suggestion effectiveness over time
- [ ] Generate weekly wellbeing summary emails

---

**Built with 💙 for the IoT Emotion Detection Project**
