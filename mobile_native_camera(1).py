"""
MID REVIEW: Mobile camera using browser's native camera API
NO APP NEEDED - uses phone's browser camera directly!

Phone captures video → Sends to laptop → Processes → Displays result on phone

This uses cross dataset ensemble , whereas mobile_native_camera.py uses three datset ensemble.
"""

from flask import Flask, render_template_string, request, jsonify
import cv2
import numpy as np
import base64
import sys
from datetime import datetime

sys.path.append('src')

from face_detector import FaceDetector
from cross_dataset_ensemble_imagenet import CrossDatasetEnsemble
from wellbeing_advisor import WellbeingAdvisor

app = Flask(__name__)

# Initialize models
print("Loading models...")
face_detector = FaceDetector(method='haar')
emotion_recognizer = CrossDatasetEnsemble()
wellbeing = WellbeingAdvisor()
print("Models loaded!")

@app.route('/')
def index():
    """Mobile interface with native camera"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>Mobile FER</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body {
                font-family: 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 10px;
            }
            
            .container { max-width: 100%; margin: 0 auto; }
            
            .header {
                text-align: center;
                color: white;
                padding: 15px;
                background: rgba(0,0,0,0.3);
                border-radius: 15px;
                margin-bottom: 15px;
            }
            
            .header h1 { font-size: 1.8rem; margin-bottom: 5px; }
            .header p { font-size: 0.9rem; opacity: 0.9; }
            
            #video-container {
                position: relative;
                width: 100%;
                border-radius: 15px;
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                margin-bottom: 15px;
                background: black;
            }
            
            #video {
                width: 100%;
                display: block;
                transform: scaleX(-1); /* Mirror for selfie */
            }
            
            #canvas {
                display: none;
            }
            
            .emotion-display {
                background: white;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 15px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                text-align: center;
            }
            
            .emotion-name {
                font-size: 3rem;
                font-weight: bold;
                margin: 10px 0;
                text-transform: uppercase;
            }
            
            .confidence {
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
            }
            
            .suggestion-box h3 {
                color: #1f77b4;
                margin-bottom: 10px;
            }
            
            .status {
                text-align: center;
                color: white;
                padding: 10px;
                background: rgba(0,0,0,0.3);
                border-radius: 10px;
                margin-bottom: 15px;
            }
            
            .loading {
                display: inline-block;
                animation: pulse 1.5s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Emotion Recognition</h1>
                <p>Using Phone Camera</p>
            </div>
            
            <div class="status" id="status">
                <span class="loading">Initializing camera...</span>
            </div>
            
            <div id="video-container">
                <video id="video" autoplay playsinline></video>
            </div>
            <canvas id="canvas"></canvas>
            
            <div class="emotion-display">
                <div class="emotion-name" id="emotion" style="color: #667eea;">
                    Detecting...
                </div>
                <div class="confidence" id="confidence">
                    --
                </div>
            </div>
            
            <div class="suggestion-box">
                <h3>Wellbeing Suggestion</h3>
                <p id="suggestion">Point camera at your face...</p>
            </div>
        </div>
        
        <script>
            const video = document.getElementById('video');
            const canvas = document.getElementById('canvas');
            const ctx = canvas.getContext('2d');
            const statusEl = document.getElementById('status');
            
            const emotionColors = {
                'Happy': '#00ff00', 'Sad': '#0000ff', 'Angry': '#ff0000',
                'Surprise': '#ffff00', 'Fear': '#800080',
                'Disgust': '#008000', 'Neutral': '#808080'
            };
            
            // Start camera
            async function startCamera() {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({
                        video: { 
                            facingMode: 'user', // Front camera
                            width: { ideal: 640 },
                            height: { ideal: 480 }
                        }
                    });
                    
                    video.srcObject = stream;
                    statusEl.innerHTML = '✅ Camera active';
                    
                    // Set canvas size
                    video.addEventListener('loadedmetadata', () => {
                        canvas.width = video.videoWidth;
                        canvas.height = video.videoHeight;
                        
                        // Start processing
                        processFrame();
                    });
                    
                } catch (err) {
                    console.error('Camera error:', err);
                    statusEl.innerHTML = '❌ Camera access denied';
                    statusEl.style.background = 'rgba(255,0,0,0.3)';
                }
            }
            
            // Process frame and send to server
            async function processFrame() {
                // Capture frame
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                
                // Convert to base64
                const imageData = canvas.toDataURL('image/jpeg', 0.8);
                
                // Send to server
                try {
                    const response = await fetch('/process_frame', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ image: imageData })
                    });
                    
                    const data = await response.json();
                    
                    // Update UI
                    if (data.emotion) {
                        document.getElementById('emotion').innerText = data.emotion;
                        document.getElementById('emotion').style.color = 
                            emotionColors[data.emotion] || '#667eea';
                        
                        document.getElementById('confidence').innerText = 
                            data.confidence.toFixed(1) + '% confident';
                        
                        document.getElementById('suggestion').innerText = data.suggestion;
                    }
                    
                } catch (error) {
                    console.error('Processing error:', error);
                }
                
                // Process next frame (reduce frequency for performance)
                setTimeout(processFrame, 500); // 2 FPS
            }
            
            // Start when page loads
            window.addEventListener('load', startCamera);
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/process_frame', methods=['POST'])
def process_frame():
    """Process single frame from phone camera"""
    try:
        # Get image data
        data = request.json
        image_data = data['image'].split(',')[1]  # Remove data:image/jpeg;base64,
        
        # Decode base64 to image
        img_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Detect faces
        faces = face_detector.detect_faces(frame)
        
        if len(faces) > 0:
            x1, y1, x2, y2 = faces[0]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
            
            face_roi = frame[y1:y2, x1:x2]
            
            if face_roi.size > 0:
                # Predict emotion
                emotion, confidence, probs, individual, agreement = \
                    emotion_recognizer.predict_emotion(face_roi)
                
                suggestion = wellbeing.get_suggestion(emotion)
                
                return jsonify({
                    'emotion': emotion,
                    'confidence': confidence * 100,
                    'suggestion': suggestion,
                    'agreement': 'High' if agreement > 0.7 else 'Moderate'
                })
        
        return jsonify({
            'emotion': 'No face',
            'confidence': 0,
            'suggestion': 'Please look at the camera'
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    import socket
    
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print("\n" + "=" * 70)
    print("MID REVIEW: Mobile Camera FER (No App Needed!)")
    print("=" * 70)
    print(f"\n📱 Access from your phone:")
    print(f"   http://{local_ip}:5000")
    print("\nFeatures:")
    print("  ✓ Uses phone's native camera (no app needed)")
    print("  ✓ Front-facing camera for selfie")
    print("  ✓ Real-time emotion detection")
    print("  ✓ Wellbeing suggestions")
    print("\nMake sure:")
    print("  1. Phone and laptop on same WiFi")
    print("  2. Allow camera when browser asks")
    print("  3. Good lighting for best results")
    print("\n" + "=" * 70)
    print("Pipeline preserved for END REVIEW ✓")
    print("=" * 70 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)