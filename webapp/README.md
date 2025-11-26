# FER Mobile Web App

Cross-Dataset Facial Emotion Recognition Progressive Web App

## Quick Start

1. **Convert Model:**
   ```bash
   python convert_ensemble_to_tfjs.py
   ```

2. **Start Server:**
   ```bash
   python -m http.server 8000
   ```

3. **Open in Browser:**
   ```
   http://localhost:8000
   ```

4. **On Mobile:**
   - Open the URL on your phone
   - Grant camera permission
   - Click "Start Camera"
   - Install as PWA when prompted

## Features

- ✅ Runs entirely on-device (no server needed)
- ✅ Cross-Dataset Ensemble (ImageNet + FER2013)
- ✅ MediaPipe face detection
- ✅ PWA installable
- ✅ Works offline
- ✅ Mobile-optimized UI

## File Structure

```
webapp/
├── index.html          # Main HTML
├── app.js              # Application logic
├── styles.css          # Mobile-optimized styles
├── manifest.json       # PWA manifest
├── sw.js              # Service worker
└── model/             # TensorFlow.js model (generated)
    ├── model.json
    └── weights.bin
```

## Requirements

- Modern browser with WebGL support
- Camera access permission
- HTTPS (or localhost) for PWA features

## Browser Support

- Chrome/Edge: Full support
- Firefox: Full support (PWA limited)
- Safari iOS: Full support (iOS 11.3+)
