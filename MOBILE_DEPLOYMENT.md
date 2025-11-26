# Mobile Deployment Guide - Cross-Dataset FER

This guide explains how to deploy your Cross-Dataset Facial Emotion Recognition model to mobile devices as a Progressive Web App (PWA).

## ✅ Requirements Met

- ✔ **Model runs ON the phone** - TensorFlow.js runs entirely in browser
- ✔ **Camera processed through browser** - MediaPipe Face Detection + getUserMedia API
- ✔ **Installable as PWA** - Manifest.json + Service Worker configured
- ✔ **Uses your OWN ensemble model** - Cross-Dataset (ImageNet + FER2013)
- ✔ **Cross-dataset robustness preserved** - Ensemble maintains ImageNet + FER2013 diversity

## 📋 Step-by-Step Deployment

### Step 1: Convert Ensemble Model to TensorFlow.js

Run the conversion script to create a browser-compatible model:

```bash
# Activate your environment
.\fer_env\Scripts\activate  # Windows
# or
source fer_env/bin/activate  # Linux/Mac

# Convert ensemble model
python convert_ensemble_to_tfjs.py
```

This will:
- Load your FER2013 and MobileNetV3 models
- Create a unified ensemble model
- Convert to TensorFlow.js format
- Save to `webapp/model/` directory

**Expected Output:**
```
✓ Model saved to: webapp/model/
  - model.json
  - weights.bin (or multiple shard files)
```

### Step 2: Verify Model Files

Check that the model files are in place:

```
webapp/
  ├── model/
  │   ├── model.json
  │   └── weights.bin (or *.bin shard files)
  ├── index.html
  ├── app.js
  ├── styles.css
  ├── manifest.json
  └── sw.js
```

### Step 3: Create PWA Icons (Optional but Recommended)

Create app icons for better PWA experience:

- `webapp/icon-192.png` (192x192 pixels)
- `webapp/icon-512.png` (512x512 pixels)

You can use any image editor or online tool to create these icons.

### Step 4: Serve via HTTP Server

**Important:** PWAs require HTTPS (or localhost). You cannot test from `file://` protocol.

#### Option A: Python HTTP Server (Development)

```bash
cd webapp
python -m http.server 8000
```

Then open: `http://localhost:8000`

#### Option B: Node.js HTTP Server

```bash
cd webapp
npx http-server -p 8000
```

#### Option C: Production Deployment

Deploy to:
- **GitHub Pages** (free, HTTPS included)
- **Netlify** (free, HTTPS included)
- **Vercel** (free, HTTPS included)
- **Your own server** (requires HTTPS certificate)

### Step 5: Test on Mobile Device

1. **On your phone**, open the web app URL (e.g., `https://your-domain.com`)
2. **Grant camera permission** when prompted
3. **Click "Start Camera"**
4. **Point camera at a face** - emotion predictions will appear
5. **Install as PWA** - Look for "Add to Home Screen" prompt

## 🎯 Features

### Cross-Dataset Ensemble
- **Model 1:** FER2013 trained from scratch (48x48 grayscale)
- **Model 2:** ImageNet-pretrained MobileNetV3 + FER2013 fine-tuned (96x96 RGB)
- **Ensemble Weight:** 40% FER2013 + 60% ImageNet
- **Total Training Data:** 14M (ImageNet) + 35K (FER2013) images

### On-Device Processing
- ✅ No server required
- ✅ Works offline (after initial load)
- ✅ Privacy-preserving (data never leaves device)
- ✅ Fast inference on mobile GPUs

### Browser Technologies
- **TensorFlow.js** - Model inference
- **MediaPipe Face Detection** - Face detection
- **getUserMedia API** - Camera access
- **Service Worker** - Offline support
- **Web App Manifest** - PWA installability

## 🔧 Troubleshooting

### Model Not Loading
- Check browser console for errors
- Verify `webapp/model/model.json` exists
- Ensure HTTP server is running (not file://)
- Check CORS headers if serving from different domain

### Camera Not Working
- Grant camera permissions in browser settings
- Use HTTPS (required for camera on most browsers)
- Check browser compatibility (Chrome, Firefox, Safari, Edge)

### Face Detection Issues
- Ensure good lighting
- Face should be clearly visible
- MediaPipe requires internet for first load (CDN)

### PWA Not Installing
- Must be served over HTTPS (or localhost)
- Manifest.json must be valid
- Service Worker must register successfully
- Browser must support PWA (Chrome, Edge, Safari iOS 11.3+)

## 📱 Mobile Browser Compatibility

| Browser | Camera | TensorFlow.js | PWA Install |
|---------|--------|---------------|-------------|
| Chrome Android | ✅ | ✅ | ✅ |
| Firefox Android | ✅ | ✅ | ⚠️ Limited |
| Safari iOS | ✅ | ✅ | ✅ (iOS 11.3+) |
| Chrome iOS | ✅ | ✅ | ❌ |
| Samsung Internet | ✅ | ✅ | ✅ |

## 🚀 Performance Tips

1. **Model Size:** The ensemble model may be large. Consider quantization:
   ```bash
   tensorflowjs_converter --quantize_float16 ...
   ```

2. **Face Detection:** MediaPipe is fast but requires internet for CDN. Consider bundling locally for offline use.

3. **Frame Rate:** Limit prediction frequency to avoid battery drain:
   - Current: Every frame
   - Optimized: Every 3-5 frames

4. **Memory:** Dispose tensors properly (already implemented in app.js)

## 📊 Model Architecture

```
Input: 96x96 RGB Image
  │
  ├─→ Branch 1: FER2013 (Grayscale 48x48)
  │     └─→ FER2013 Model (from scratch)
  │
  └─→ Branch 2: MobileNetV3 (RGB 96x96)
        └─→ ImageNet + FER2013 Model (transfer learning)
  │
  └─→ Ensemble Fusion (Weighted Average)
        └─→ Softmax
            └─→ 7 Emotion Probabilities
```

## 🎓 Next Steps

1. **Optimize Model:** Quantize to reduce size
2. **Add Features:** Emotion history, statistics
3. **Improve UI:** Better visualizations, animations
4. **Offline Support:** Bundle MediaPipe locally
5. **Analytics:** Track usage (privacy-preserving)

## 📝 Notes

- The model runs entirely in the browser using WebGL/WebGPU
- No data is sent to any server
- Works offline after initial model download
- Cross-dataset robustness is preserved through ensemble approach

