// =============================================================================
// FER Mobile - MediaPipe v0.4 Face Detection + TensorFlow.js Emotion
// Fast, proven approach
// =============================================================================

const MODEL_PATH = './model/model.json';
const TARGET_SIZE = 96;
const PREDICTION_INTERVAL = 300;
const LABELS = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise'];

let model = null;
let faceDetection = null;
let camera = null;
let running = false;
let lastPredictionTime = 0;

const video = document.getElementById('video');
const overlay = document.getElementById('overlay');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const status = document.getElementById('status');
const predList = document.getElementById('predList');

// ============== Model Loading ==============
async function loadModel() {
  console.log('Loading emotion model...');
  try {
    const response = await fetch(MODEL_PATH);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    
    const modelJson = await response.json();
    console.log('Is Graph model:', !!modelJson.modelTopology.node);

    if (modelJson.modelTopology.node) {
      model = await tf.loadGraphModel(tf.io.http(MODEL_PATH));
    } else {
      model = await tf.loadLayersModel(tf.io.http(MODEL_PATH));
    }

    console.log('✓ Emotion model loaded');
    setStatusSuccess('✓ Model ready');
    return model;
  } catch (err) {
    console.error('Model error:', err);
    setStatusError(`Model: ${err.message}`);
    throw err;
  }
}

// ============== MediaPipe Face Detection ==============
async function initFaceDetection() {
  console.log('Loading MediaPipe Face Detection v0.4...');
  try {
    // Create instance and configure options per MediaPipe v0.4 examples
    faceDetection = new FaceDetection({
      locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/face_detection@0.4/${file}`
    });

    // Configure model and confidence thresholds
    faceDetection.setOptions({
      model: 'short',
      minDetectionConfidence: 0.5
    });

    // Register results callback
    faceDetection.onResults(onFaceDetectionResults);

    console.log('✓ MediaPipe Face Detection instance created');
    setStatusSuccess('✓ Face detection ready');
  } catch (err) {
    console.error('Face detection error:', err);
    setStatusError(`Face detection: ${err.message}`);
    throw err;
  }
}

// ============== Face Detection Results Handler ==============
function onFaceDetectionResults(results) {
  console.log('onResults called with detections:', results.detections ? results.detections.length : 0);

  const ctx = overlay.getContext('2d');
  ctx.clearRect(0, 0, overlay.width, overlay.height);

  if (results.detections && results.detections.length > 0) {
    console.log('Processing', results.detections.length, 'faces');
    results.detections.forEach((detection, idx) => {
      // MediaPipe v0.4 format: boundingBox with xCenter, yCenter, width, height (relative 0-1)
      const bbox = detection.boundingBox;
      
      console.log(`Detection ${idx}:`, bbox);
      
      // Convert to pixel coordinates
      const x = bbox.xCenter * video.videoWidth - (bbox.width * video.videoWidth) / 2;
      const y = bbox.yCenter * video.videoHeight - (bbox.height * video.videoHeight) / 2;
      const w = bbox.width * video.videoWidth;
      const h = bbox.height * video.videoHeight;

      console.log(`Face pixel coords: x=${Math.round(x)}, y=${Math.round(y)}, w=${Math.round(w)}, h=${Math.round(h)}`);

      // Draw GREEN bounding box
      ctx.strokeStyle = '#00ff00';
      ctx.lineWidth = 4;
      ctx.strokeRect(x, y, w, h);

      // Draw confidence score
      const conf = detection.score ? detection.score[0] : 0.5;
      ctx.fillStyle = '#00ff00';
      ctx.font = 'bold 16px sans-serif';
      ctx.fillText(`Face ${(conf * 100).toFixed(0)}%`, x + 5, y - 8);

      // Draw center dot
      ctx.fillStyle = '#ff0000';
      ctx.beginPath();
      ctx.arc(bbox.xCenter * video.videoWidth, bbox.yCenter * video.videoHeight, 5, 0, Math.PI * 2);
      ctx.fill();

      // Predict emotion
      const now = Date.now();
      if (now - lastPredictionTime > PREDICTION_INTERVAL) {
        predictEmotionForFace(x, y, w, h);
        lastPredictionTime = now;
      }
    });
  } else {
    ctx.fillStyle = '#ff6b6b';
    ctx.font = '16px sans-serif';
    ctx.fillText('No faces detected', 10, 30);
  }
}

// ============== Extract Face & Predict ==============
function predictEmotionForFace(x, y, w, h) {
  if (!model || !running) return;

  try {
    // Extract face region
    const faceCanvas = document.createElement('canvas');
    faceCanvas.width = TARGET_SIZE;
    faceCanvas.height = TARGET_SIZE;
    const ctx = faceCanvas.getContext('2d');

    // Clamp coordinates
    const sx = Math.max(0, Math.floor(x));
    const sy = Math.max(0, Math.floor(y));
    const sw = Math.min(w, video.videoWidth - sx);
    const sh = Math.min(h, video.videoHeight - sy);

    if (sw <= 0 || sh <= 0) return;

    ctx.drawImage(video, sx, sy, sw, sh, 0, 0, TARGET_SIZE, TARGET_SIZE);
    // Pass bbox so we can draw single final emotion for this face/frame
    predictEmotion(faceCanvas, { x: sx, y: sy, w: sw, h: sh });
  } catch (err) {
    console.error('Face extraction error:', err);
  }
}

// ============== Emotion Prediction ==============
async function predictEmotion(faceCanvas, bbox = null) {
  if (!model) return;

  tf.engine().startScope();
  try {
    const img = tf.browser.fromPixels(faceCanvas)
      .resizeBilinear([TARGET_SIZE, TARGET_SIZE])
      .toFloat()
      .div(255.0)
      .expandDims(0);

    let preds;
    if (model.executeAsync) {
      preds = await model.executeAsync(img);
    } else if (model.execute) {
      preds = model.execute(img);
    } else {
      preds = model.predict(img);
    }

    if (Array.isArray(preds)) preds = preds[0];

    let probs = await preds.data();
    const sum = Array.from(probs).reduce((a, b) => a + b, 0);
    
    if (Math.abs(sum - 1.0) > 0.01) {
      const t = tf.tensor(probs);
      const exp = tf.exp(t.sub(tf.max(t)));
      probs = await exp.div(tf.sum(exp)).data();
      exp.dispose();
      t.dispose();
    }

    const results = Array.from(probs).map((p, i) => ({ label: LABELS[i], prob: p }))
      .sort((a, b) => b.prob - a.prob);

    console.log('Emotions (top):', results[0].label, (results[0].prob*100).toFixed(1) + '%');

    // Show only single final emotion per frame. If bbox provided, draw label near that face.
    showSinglePrediction(results[0], bbox);

    // Publish event to MQTT broker if client available (browser publishes JSON)
    try {
      if (typeof window.publishEmotionEvent === 'function') {
        const top = results[0];
        const userId = (window.MQTT_CONFIG && window.MQTT_CONFIG.CLIENT_ID) ? window.MQTT_CONFIG.CLIENT_ID : null;
        // publish: (userId, emotion, confidence, bbox)
        window.publishEmotionEvent(userId, top.label, top.prob, bbox);
      }
    } catch (e) {
      console.warn('publishEmotionEvent failed', e);
    }

    img.dispose();
    if (preds && typeof preds.dispose === 'function') preds.dispose();
  } catch (err) {
    console.error('Prediction error:', err);
  } finally {
    tf.engine().endScope();
  }
}

// Display only one emotion (top) per frame/face
function showSinglePrediction(topResult, bbox = null) {
  // Update textual prediction (single line)
  if (predList) {
    predList.innerHTML = `<div><strong>${topResult.label}</strong> ${(topResult.prob*100).toFixed(1)}%</div>`;
  }

  // Draw on overlay near bbox or top-left
  if (overlay && overlay.getContext) {
    const ctx = overlay.getContext('2d');
    // Clear only label region to avoid removing boxes; we'll redraw boxes in onFaceDetectionResults
    // For simplicity, clear whole overlay then let detection handler redraw boxes next frame.
    ctx.clearRect(0, 0, overlay.width, overlay.height);

    if (bbox) {
        // Draw label so it appears readable even when canvas is mirrored via CSS
        ctx.fillStyle = 'lime';
        ctx.font = 'bold 18px sans-serif';
        const text = `🎭 ${topResult.label} ${(topResult.prob*100).toFixed(0)}%`;
        const textWidth = ctx.measureText(text).width;
        // Compute canvas x so that after a CSS horizontal flip (scaleX(-1))
        // the label appears above the face bounding box. This works whether
        // the canvas is mirrored or not.
        const tx = Math.max(5, bbox.x + bbox.w - textWidth);
        const ty = Math.max(20, bbox.y - 8);
        ctx.fillText(text, tx, ty);
        // Also redraw bbox outline so label appears with box
        ctx.strokeStyle = '#00ff00';
        ctx.lineWidth = 3;
        ctx.strokeRect(bbox.x, bbox.y, bbox.w, bbox.h);
    } else {
      ctx.fillStyle = 'lime';
      ctx.font = 'bold 18px sans-serif';
      ctx.fillText(`🎭 ${topResult.label} ${(topResult.prob*100).toFixed(0)}%`, 10, 30);
    }
  }
}

// ============== UI ==============
function showPredictions(results) {
  let html = '';
  results.forEach(r => {
    html += `<div><strong>${r.label}</strong> ${(r.prob * 100).toFixed(1)}%</div>`;
  });
  predList.innerHTML = html || '—';

  if (results.length > 0) {
    const ctx = overlay.getContext('2d');
    ctx.fillStyle = 'lime';
    ctx.font = 'bold 18px sans-serif';
    ctx.fillText(`🎭 ${results[0].label}`, 10, 30);
  }
}

function setStatus(msg) {
  status.textContent = msg;
}

function setStatusSuccess(msg) {
  setStatus(msg);
  status.style.color = 'lime';
}

function setStatusError(msg) {
  setStatus(msg);
  status.style.color = '#ff6b6b';
}

// ============== Buttons ==============
startBtn.addEventListener('click', async () => {
  startBtn.disabled = true;
  try {
    setStatus('Loading model...');
    if (!model) await loadModel();

    setStatus('Initializing face detection...');
    if (!faceDetection) await initFaceDetection();

    setStatus('Starting camera...');

    // Prefer MediaPipe Camera util when available (faster, handles frames)
    if (typeof Camera !== 'undefined') {
      camera = new Camera(video, {
        onFrame: async () => {
          try {
            await faceDetection.send({ image: video });
          } catch (err) {
            console.error('Detection send error:', err);
          }
        },
        width: 640,
        height: 480
      });

      camera.start();
      // overlay size will update once video frames start
      running = true;
      stopBtn.disabled = false;
      setStatusSuccess('✓ Running — Show your face!');
    } else {
      // Fallback: use getUserMedia loop (already present on many browsers)
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 } }
      });
      video.srcObject = stream;
      await video.play();
      overlay.width = video.videoWidth;
      overlay.height = video.videoHeight;
      running = true;

      const loop = async () => {
        if (!running) return;
        try {
          await faceDetection.send({ image: video });
        } catch (err) {
          console.error('Detection error:', err);
        }
        requestAnimationFrame(loop);
      };
      loop();

      stopBtn.disabled = false;
      setStatusSuccess('✓ Running — Show your face!');
    }
  } catch (err) {
    console.error('Start error:', err);
    startBtn.disabled = false;
    setStatusError(`Failed: ${err.message}`);
  }
});

stopBtn.addEventListener('click', () => {
  running = false;
  stopBtn.disabled = true;
  startBtn.disabled = false;
  setStatus('Stopped');

  const stream = video.srcObject;
  if (stream) {
    stream.getTracks().forEach(t => t.stop());
    video.srcObject = null;
  }
  // Stop MediaPipe Camera if used
  if (camera && typeof camera.stop === 'function') {
    try { camera.stop(); } catch (e) { console.warn('Camera stop error:', e); }
    camera = null;
  }

  if (overlay && overlay.getContext) overlay.getContext('2d').clearRect(0, 0, overlay.width, overlay.height);
  predList.innerHTML = '—';
});

// ============== Init ==============
(async () => {
  try {
    const r = await fetch(MODEL_PATH, { method: 'HEAD' });
    if (r.ok) {
      setStatus('Ready — Click "Start Camera"');
    } else {
      setStatusError('Model not found');
    }
  } catch (err) {
    setStatusError('Cannot reach model');
  }
})();
