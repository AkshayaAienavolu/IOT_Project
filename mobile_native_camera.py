"""
MID REVIEW: Mobile camera using browser's native camera API
NO APP NEEDED - uses phone's browser camera directly!

Phone captures video → Sends to laptop → Processes → Displays result on phone
"""

from flask import Flask, render_template_string, request, jsonify, Response
import cv2
import numpy as np
import base64
import sys
import os
import json
from datetime import datetime

sys.path.append('src')

from face_detector import FaceDetector
from cross_dataset_ensemble_imagenet import CrossDatasetEnsemble
from three_dataset_ensemble import ThreeDatasetEnsemble
from wellbeing_advisor import WellbeingAdvisor

app = Flask(__name__)

# Initialize models
print("Loading models...")
face_detector = FaceDetector(method='haar')
emotion_recognizer = ThreeDatasetEnsemble()
wellbeing = WellbeingAdvisor()
print("Models loaded!")

@app.route('/')
def index():
    """Mobile interface with native camera AND video upload"""
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
            
            /* Tab Navigation */
            .tabs {
                display: flex;
                gap: 10px;
                margin-bottom: 15px;
            }
            
            .tab-button {
                flex: 1;
                padding: 15px;
                background: rgba(255,255,255,0.2);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 1rem;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s;
            }
            
            .tab-button.active {
                background: white;
                color: #667eea;
            }
            
            .tab-content {
                display: none;
            }
            
            .tab-content.active {
                display: block;
            }
            
            #video-container {
                position: relative;
                width: 50%;
                border-radius: 15px;
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                
                margin-bottom: 15px;
                background: black;
            }
            
            #video {
                
                width: 100%;
                display: block;
                transform: scaleX(-1);
            }
            
            #canvas, #video-preview {
                display: none;
            }
            
            /* Video Upload Section */
            .upload-section {
                background: white;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 15px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            
            .upload-section h3 {
                color: #667eea;
                margin-bottom: 15px;
            }
            
            .file-input-wrapper {
                position: relative;
                overflow: hidden;
                display: inline-block;
                width: 100%;
            }
            
            .file-input-wrapper input[type=file] {
                position: absolute;
                left: -9999px;
            }
            
            .file-input-label {
                display: block;
                padding: 15px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
                border-radius: 10px;
                cursor: pointer;
                font-size: 1.1rem;
                font-weight: bold;
            }
            
            .file-input-label:hover {
                opacity: 0.9;
            }
            
            #file-name {
                margin-top: 10px;
                color: #666;
                font-size: 0.9rem;
                text-align: center;
            }
            
            .process-button {
                width: 100%;
                padding: 15px;
                margin-top: 10px;
                background: #00c853;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 1.1rem;
                font-weight: bold;
                cursor: pointer;
                display: none;
            }
            
            .process-button:disabled {
                background: #ccc;
                cursor: not-allowed;
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
            
            .progress-bar {
                width: 100%;
                height: 8px;
                background: rgba(0,0,0,0.2);
                border-radius: 10px;
                overflow: hidden;
                margin-top: 10px;
                display: none;
            }
            
            .progress-fill {
                height: 100%;
                background: #00c853;
                width: 0%;
                transition: width 0.3s;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎭 Emotion Recognition</h1>
                <p>Live Camera & Video Upload</p>
            </div>
            
            <!-- Tab Navigation -->
            <div class="tabs">
                <button class="tab-button active" onclick="switchTab('live')">
                    📹 Live Camera
                </button>
                <button class="tab-button" onclick="switchTab('upload')">
                    📁 Upload Video
                </button>
            </div>
            
            <!-- Live Camera Tab -->
            <div id="live-tab" class="tab-content active">
                <div class="status" id="status">
                    <span class="loading">📹 Initializing camera...</span>
                </div>
                
                <div id="video-container">
                    <video id="video" autoplay playsinline></video>
                </div>
                <canvas id="canvas"></canvas>
            </div>
            
            <!-- Video Upload Tab -->
            <div id="upload-tab" class="tab-content">
                <div class="upload-section">
                    <h3>📁 Upload Video File</h3>
                    <p style="margin-bottom: 15px; color: #666;">
                        Supported formats: MP4, AVI, MOV, WebM
                    </p>
                    
                    <div class="file-input-wrapper">
                        <input type="file" id="video-file" accept="video/*" onchange="handleFileSelect(event)">
                        <label for="video-file" class="file-input-label">
                            📤 Choose Video File
                        </label>
                    </div>
                    
                    <div id="file-name"></div>
                    
                    <button id="process-button" class="process-button" onclick="processVideo()">
                        🎬 Process Video
                    </button>
                    
                    <div class="progress-bar" id="progress-bar">
                        <div class="progress-fill" id="progress-fill"></div>
                    </div>
                </div>
                
                <div id="video-container-upload" style="display:none;">
                    <video id="video-preview" controls style="width:100%; border-radius:15px;"></video>
                </div>
            </div>
            
            <!-- Results Display (Shared) -->
            <div class="emotion-display">
                <div class="emotion-name" id="emotion" style="color: #667eea;">
                    Detecting...
                </div>
                <div class="confidence" id="confidence">
                    --
                </div>
            </div>
            
            <div class="suggestion-box">
                <h3>💡 Wellbeing Suggestion</h3>
                <p id="suggestion">Start camera or upload video...</p>
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
            
            let currentTab = 'live';
            let processingInterval = null;
            let selectedFile = null;
            
            // Tab switching
            function switchTab(tab) {
                currentTab = tab;
                
                // Update tab buttons
                document.querySelectorAll('.tab-button').forEach(btn => {
                    btn.classList.remove('active');
                });
                event.target.classList.add('active');
                
                // Update tab content
                document.querySelectorAll('.tab-content').forEach(content => {
                    content.classList.remove('active');
                });
                document.getElementById(tab + '-tab').classList.add('active');
                
                // Stop live camera if switching away
                if (tab === 'upload' && processingInterval) {
                    clearInterval(processingInterval);
                    if (video.srcObject) {
                        video.srcObject.getTracks().forEach(track => track.stop());
                    }
                }
                
                // Start live camera if switching to it
                if (tab === 'live' && !video.srcObject) {
                    startCamera();
                }
            }
            
            // Live camera functions
            async function startCamera() {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({
                        video: { 
                            facingMode: 'user',
                            width: { ideal: 640 },
                            height: { ideal: 480 }
                        }
                    });
                    
                    video.srcObject = stream;
                    statusEl.innerHTML = '✅ Camera active';
                    
                    video.addEventListener('loadedmetadata', () => {
                        canvas.width = video.videoWidth;
                        canvas.height = video.videoHeight;
                        processFrame();
                    });
                    
                } catch (err) {
                    console.error('Camera error:', err);
                    statusEl.innerHTML = '❌ Camera access denied';
                    statusEl.style.background = 'rgba(255,0,0,0.3)';
                }
            }
            
            async function processFrame() {
                if (currentTab !== 'live') return;
                
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                const imageData = canvas.toDataURL('image/jpeg', 0.8);
                
                try {
                    const response = await fetch('/process_frame', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ image: imageData })
                    });
                    
                    const data = await response.json();
                    updateUI(data);
                    
                } catch (error) {
                    console.error('Processing error:', error);
                }
                
                setTimeout(processFrame, 500);
            }
            
            // Video upload functions
            function handleFileSelect(event) {
                selectedFile = event.target.files[0];
                if (selectedFile) {
                    document.getElementById('file-name').innerText = 
                        `Selected: ${selectedFile.name}`;
                    document.getElementById('process-button').style.display = 'block';
                    
                    // Show video preview
                    const videoPreview = document.getElementById('video-preview');
                    videoPreview.src = URL.createObjectURL(selectedFile);
                    document.getElementById('video-container-upload').style.display = 'block';
                }
            }
            
            async function processVideo() {
                if (!selectedFile) return;
                
                const processBtn = document.getElementById('process-button');
                const progressBar = document.getElementById('progress-bar');
                const progressFill = document.getElementById('progress-fill');
                
                processBtn.disabled = true;
                processBtn.innerText = '⏳ Processing...';
                progressBar.style.display = 'block';
                
                const formData = new FormData();
                formData.append('video', selectedFile);
                
                try {
                    const response = await fetch('/process_video', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    
                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;
                        
                        const chunk = decoder.decode(value);
                        const lines = chunk.split('\\n');
                        
                        for (const line of lines) {
                            if (line.startsWith('data: ')) {
                                const data = JSON.parse(line.slice(6));
                                
                                if (data.progress !== undefined) {
                                    progressFill.style.width = data.progress + '%';
                                }
                                
                                if (data.emotion) {
                                    updateUI(data);
                                }
                                
                                if (data.done) {
                                    processBtn.disabled = false;
                                    processBtn.innerText = '✅ Complete!';
                                    setTimeout(() => {
                                        processBtn.innerText = '🎬 Process Video';
                                        progressBar.style.display = 'none';
                                        progressFill.style.width = '0%';
                                    }, 2000);
                                }
                            }
                        }
                    }
                    
                } catch (error) {
                    console.error('Video processing error:', error);
                    processBtn.disabled = false;
                    processBtn.innerText = '❌ Error - Try Again';
                }
            }
            
            // Update UI with results
            function updateUI(data) {
                if (data.emotion) {
                    document.getElementById('emotion').innerText = data.emotion;
                    document.getElementById('emotion').style.color = 
                        emotionColors[data.emotion] || '#667eea';
                    
                    document.getElementById('confidence').innerText = 
                        data.confidence.toFixed(1) + '% confident';
                    
                    document.getElementById('suggestion').innerText = data.suggestion;
                }
            }
            
            // Start camera on load if on live tab
            window.addEventListener('load', () => {
                if (currentTab === 'live') {
                    startCamera();
                }
            });
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


@app.route('/process_video', methods=['POST'])
def process_video():
    """Process uploaded video file"""
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file'}), 400
        
        video_file = request.files['video']
        
        # Save temporarily
        import tempfile
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, 'uploaded_video.mp4')
        video_file.save(temp_path)
        
        def generate():
            """Stream processing results"""
            import cv2
            
            cap = cv2.VideoCapture(temp_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_count = 0
            
            emotion_counts = {}
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Process every 10th frame for speed
                if frame_count % 10 != 0:
                    continue
                
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
                        
                        # Count emotions
                        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                        
                        suggestion = wellbeing.get_suggestion(emotion)
                        
                        # Send progress
                        progress = int((frame_count / total_frames) * 100)
                        yield f"data: {json.dumps({'emotion': emotion, 'confidence': confidence * 100, 'suggestion': suggestion, 'progress': progress})}\n\n"
                
            cap.release()
            
            # Send final result (most common emotion)
            if emotion_counts:
                most_common = max(emotion_counts, key=emotion_counts.get)
                final_suggestion = wellbeing.get_suggestion(most_common)
                yield f"data: {json.dumps({'emotion': most_common, 'confidence': 100, 'suggestion': final_suggestion, 'done': True})}\n\n"
            
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        return Response(generate(), mimetype='text/event-stream')
        
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
    print(f"   https://{local_ip}:5000")
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
    
    app.run(host='0.0.0.0', port=5000, ssl_context=('cert.pem', 'key.pem'))
