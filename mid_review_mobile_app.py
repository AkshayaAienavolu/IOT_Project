"""
MID REVIEW: Real-time FER with phone camera
Video captured on phone, emotions displayed on phone screen in real-time

For END REVIEW: This will be extended with:
- Survey data integration
- Raspberry Pi dashboard
- Context-aware suggestions
"""

import cv2
import time
import sys
import numpy as np
from flask import Flask, render_template_string, Response, jsonify
import json
from datetime import datetime

sys.path.append('src')

from face_detector import FaceDetector
from cross_dataset_ensemble_imagenet import CrossDatasetEnsemble
from wellbeing_advisor import WellbeingAdvisor

# Initialize Flask app
app = Flask(__name__)

# Initialize models (load once)
print("Loading models...")
face_detector = FaceDetector(method='haar')
emotion_recognizer = CrossDatasetEnsemble()
wellbeing = WellbeingAdvisor()
print("Models loaded!")

# Global variables
current_emotion = "Neutral"
current_confidence = 0.0
current_suggestion = "Look at the camera"
model_agreement = "N/A"
fps = 0

# For END REVIEW: Survey data storage
survey_responses = []  # Will be used in END REVIEW

def generate_frames(camera_source=0):
    """Generate video frames with emotion detection"""
    global current_emotion, current_confidence, current_suggestion, model_agreement, fps
    
    cap = cv2.VideoCapture(camera_source)
    frame_count = 0
    start_time = time.time()
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        # Mirror for selfie view
        frame = cv2.flip(frame, 1)
        
        # Detect faces
        faces = face_detector.detect_faces(frame)
        
        for (x1, y1, x2, y2) in faces:
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
            
            face_roi = frame[y1:y2, x1:x2]
            
            if face_roi.size > 0:
                # Predict emotion
                emotion, confidence, probs, individual, agreement = \
                    emotion_recognizer.predict_emotion(face_roi)
                
                # Update globals
                current_emotion = emotion
                current_confidence = confidence
                current_suggestion = wellbeing.get_suggestion(emotion)
                model_agreement = "High" if agreement > 0.7 else "Moderate"
                
                # Draw on frame
                color = emotion_recognizer.get_emotion_color(emotion)
                thickness = 4 if agreement > 0.7 else 2
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
                
                # Emotion label
                label = f"{emotion} ({confidence*100:.0f}%)"
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)[0]
                
                # Background for label
                cv2.rectangle(frame, (x1, y1 - 50), 
                            (x1 + label_size[0] + 10, y1), (0, 0, 0), -1)
                
                # Label text
                cv2.putText(frame, label, (x1 + 5, y1 - 15),
                          cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)
        
        # Calculate FPS
        frame_count += 1
        elapsed = time.time() - start_time
        if elapsed > 1.0:
            fps = frame_count / elapsed
            frame_count = 0
            start_time = time.time()
        
        # FPS display
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    """Main page with video stream and emotion display"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>FER - Mobile View</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 10px;
            }
            
            .container {
                max-width: 100%;
                margin: 0 auto;
            }
            
            .header {
                text-align: center;
                color: white;
                padding: 15px;
                background: rgba(0,0,0,0.3);
                border-radius: 15px;
                margin-bottom: 15px;
            }
            
            .header h1 {
                font-size: 1.8rem;
                margin-bottom: 5px;
            }
            
            .header p {
                font-size: 0.9rem;
                opacity: 0.9;
            }
            
            .video-container {
                position: relative;
                width: 100%;
                border-radius: 15px;
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                margin-bottom: 15px;
            }
            
            #video-feed {
                width: 100%;
                display: block;
            }
            
            .emotion-display {
                background: white;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 15px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                animation: fadeIn 0.5s;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .emotion-name {
                font-size: 3rem;
                font-weight: bold;
                text-align: center;
                margin: 10px 0;
                text-transform: uppercase;
                letter-spacing: 2px;
            }
            
            .confidence {
                text-align: center;
                font-size: 1.5rem;
                color: #666;
                margin-bottom: 15px;
            }
            
            .suggestion-box {
                background: linear-gradient(135deg, #e8f4f8 0%, #d4e9f5 100%);
                padding: 20px;
                border-radius: 15px;
                border-left: 5px solid #1f77b4;
                margin-bottom: 15px;
                box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            }
            
            .suggestion-box h3 {
                color: #1f77b4;
                margin-bottom: 10px;
                font-size: 1.2rem;
            }
            
            .suggestion-box p {
                color: #333;
                line-height: 1.6;
                font-size: 1rem;
            }
            
            .stats {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
                margin-bottom: 15px;
            }
            
            .stat-card {
                background: white;
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            }
            
            .stat-card h4 {
                color: #666;
                font-size: 0.8rem;
                margin-bottom: 5px;
                text-transform: uppercase;
            }
            
            .stat-card p {
                font-size: 1.3rem;
                font-weight: bold;
                color: #333;
            }
            
            .footer {
                text-align: center;
                color: white;
                padding: 15px;
                background: rgba(0,0,0,0.3);
                border-radius: 15px;
                font-size: 0.8rem;
            }
            
            .pulse {
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎭 Emotion Recognition</h1>
                <p>Cross-Dataset AI System</p>
            </div>
            
            <div class="video-container">
                <img id="video-feed" src="{{ url_for('video_feed') }}" alt="Video Feed">
            </div>
            
            <div class="emotion-display">
                <div class="emotion-name" id="emotion" style="color: #667eea;">
                    Detecting...
                </div>
                <div class="confidence" id="confidence">
                    -- %
                </div>
            </div>
            
            <div class="suggestion-box">
                <h3>💡 Wellbeing Suggestion</h3>
                <p id="suggestion">Look at the camera to detect your emotion...</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <h4>FPS</h4>
                    <p id="fps" class="pulse">--</p>
                </div>
                <div class="stat-card">
                    <h4>Agreement</h4>
                    <p id="agreement">--</p>
                </div>
            </div>
            
            # <div class="footer">
            #     <p>MID REVIEW: Real-time Video Processing</p>
            #     <p style="font-size: 0.7rem; margin-top: 5px;">
            #         END REVIEW: Will include Survey Integration & RPi Dashboard
            #     </p>
            # </div>
        </div>
        
        <script>
            // Color mapping for emotions
            const emotionColors = {
                'Happy': '#00ff00',
                'Sad': '#0000ff',
                'Angry': '#ff0000',
                'Surprise': '#ffff00',
                'Fear': '#800080',
                'Disgust': '#008000',
                'Neutral': '#808080'
            };
            
            // Update emotion data every 500ms
            function updateData() {
                fetch('/get_emotion')
                    .then(response => response.json())
                    .then(data => {
                        // Update emotion
                        document.getElementById('emotion').innerText = data.emotion;
                        document.getElementById('emotion').style.color = 
                            emotionColors[data.emotion] || '#667eea';
                        
                        // Update confidence
                        document.getElementById('confidence').innerText = 
                            data.confidence.toFixed(1) + '% confident';
                        
                        // Update suggestion
                        document.getElementById('suggestion').innerText = data.suggestion;
                        
                        // Update stats
                        document.getElementById('fps').innerText = data.fps.toFixed(1);
                        document.getElementById('agreement').innerText = data.agreement;
                    })
                    .catch(error => console.error('Error:', error));
            }
            
            // Update every 500ms
            setInterval(updateData, 500);
            
            // Initial update
            updateData();
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(camera_source=0),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_emotion')
def get_emotion():
    """API endpoint to get current emotion data"""
    return jsonify({
        'emotion': current_emotion,
        'confidence': current_confidence * 100,
        'suggestion': current_suggestion,
        'agreement': model_agreement,
        'fps': fps,
        'timestamp': datetime.now().isoformat()
    })

# ============================================================================
# END REVIEW PREPARATION: Survey endpoints (not implemented yet)
# ============================================================================

@app.route('/save_survey', methods=['POST'])
def save_survey():
    """
    END REVIEW: Save survey responses
    Will store emotion + reason pairs for context-aware suggestions
    """
    # TODO: Implement in END REVIEW
    pass

@app.route('/get_contextual_advice')
def get_contextual_advice():
    """
    END REVIEW: Get advice based on survey data
    Will match current emotion with similar survey responses
    """
    # TODO: Implement in END REVIEW
    pass

# ============================================================================

if __name__ == '__main__':
    import socket
    
    # Get laptop IP
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print("\n" + "=" * 70)
    print("MID REVIEW: Mobile FER System")
    print("=" * 70)
    print(f"\n📱 Access from your phone:")
    print(f"   http://{local_ip}:5000")
    print("\nMake sure:")
    print("  1. Phone and laptop on same WiFi")
    print("  2. Allow camera access")
    print("  3. Good lighting for best results")
    print("\n" + "=" * 70)
    print("For END REVIEW: Survey + RPi Dashboard will be added")
    print("=" * 70 + "\n")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)