"""
Quick instructions for downloading and using your survey data
"""

print("""
╔══════════════════════════════════════════════════════════════╗
║  DOWNLOAD YOUR GOOGLE SHEETS SURVEY DATA                     ║
╚══════════════════════════════════════════════════════════════╝

📋 STEPS TO GET YOUR SURVEY DATA:

1. Open your Google Sheets survey responses:
   https://docs.google.com/spreadsheets/d/1eUfXO9RQnHH-rMpBTtL47GymYppsaFG2-71UL5Izjug/edit

2. Click: File → Download → Comma-separated values (.csv)

3. Save the file as: survey_responses.csv
   Location: C:\\Users\\18003\\Iot_proj\\survey_responses.csv

4. OPTIONAL - Process the data (already have built-in suggestions):
   > python process_survey_data.py

5. Test the system locally:
   > python test_wellbeing_system.py

6. Deploy to Raspberry Pi:
   > git add .
   > git commit -m "Add context-aware wellbeing system"
   > git push

7. On Raspberry Pi:
   > cd ~/IOT_Project
   > git pull
   > sudo systemctl restart dashboard_server

8. View in browser:
   Open your dashboard and scroll to "Context-Aware Wellbeing Guide"


╔══════════════════════════════════════════════════════════════╗
║  WHAT THE SYSTEM DOES                                        ║
╚══════════════════════════════════════════════════════════════╝

✅ Analyzes user's emotion patterns (last 7 days)
✅ Identifies dominant emotions and trends
✅ Matches emotions to survey contexts (exam, sleep, friend, etc.)
✅ Provides peer-sourced suggestions
✅ Adapts to time-of-day patterns
✅ Shows insights like "You've been feeling Sad 60% of the time"
✅ Gives both immediate and long-term tips


╔══════════════════════════════════════════════════════════════╗
║  EXAMPLE OUTPUT                                              ║
╚══════════════════════════════════════════════════════════════╝

📊 Your Emotional Patterns:
   • Past week: **Sad** dominated (60% of readings)
   • Recently shifting to: **Happy**
   • Most active during evening

💡 For Sad (your main emotion):
   • 💡 Survey insight: One result doesn't define you
   • 📈 Identify ONE thing to improve next time
   • 🎯 Focus on what you DID learn
   • 🤗 Talk about growth opportunities

🎯 Right now (Happy):
   • 😊 Enjoy this moment! Savor the good feeling
   • 📸 Capture happy moments
   • 💫 Share your joy with someone

🌟 Peer Wisdom:
   • 🌱 Track patterns to understand triggers
   • 💪 Small consistent actions > big occasional efforts
   • 🤝 Your wellbeing matters - reach out when needed


╔══════════════════════════════════════════════════════════════╗
║  YOUR SURVEY DATA SUMMARY                                     ║
╚══════════════════════════════════════════════════════════════╝

From your Google Sheets, you have:
• Emotions: Fear, Sad, Happy, Neutral
• Contexts: 
  - Fear: exam, project evaluation
  - Sad: grades/QRA marks, fight with friend, sleep/classes
  - Happy: food, talking to friends, positive mood

These contexts are NOW MATCHED to give targeted suggestions!

For example:
- If user mostly feels SAD + it's exam period
  → Get exam-specific advice from peers
- If user feels FEAR + late evening pattern
  → Get sleep/anxiety management tips

═══════════════════════════════════════════════════════════════

🚀 Ready to deploy? Run these commands:

   git add .
   git commit -m "Add context-aware wellbeing suggestions based on survey"
   git push

Then on Pi:
   cd ~/IOT_Project && git pull
   sudo systemctl restart dashboard_server

Done! Check your dashboard at:
   http://<raspberry-pi-ip>:5000/user/<your-user-id>

═══════════════════════════════════════════════════════════════
""")
