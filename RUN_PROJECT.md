# How to Run the Mobile FER Project

## Prerequisites
- Python environment `fer_env` activated
- Models exist: `models/fer_model_best.h5` and `models/pretrained/mobilenetv3_finetuned.h5`

## Step-by-Step Commands

### Step 1: Activate Environment

Open Command Prompt (cmd) and navigate to project folder:

```cmd
cd C:\Users\18003\Iot_proj
fer_env\Scripts\activate
```

You should see `(fer_env)` in your prompt.

### Step 2: Convert Model to TensorFlow.js

Convert your ensemble model to browser-compatible format:

```cmd
python convert_ensemble_to_tfjs.py
```

**Expected Output:**
```
✓ Models loaded
✓ Ensemble model built
✓ SavedModel saved
✓ TensorFlow.js conversion successful!
✓ Model saved to: webapp/model/
```

**Check:** Verify files exist:
```cmd
dir webapp\model
```

You should see `model.json` and weight files (`.bin`).

### Step 3: Start Web Server

Navigate to webapp folder and start HTTP server:

```cmd
cd webapp
python -m http.server 8000
```

**Expected Output:**
```
Serving HTTP on :: port 8000 (http://[::]:8000/) ...
```

### Step 4: Open in Browser

Open your browser and go to:
```
http://localhost:8000
```

### Step 5: Test the App

1. Click **"Start Camera"** button
2. Grant camera permission when prompted
3. Point camera at a face
4. See emotion predictions in real-time

## Quick Command Summary

```cmd
# 1. Activate environment
cd C:\Users\18003\Iot_proj
fer_env\Scripts\activate

# 2. Convert model (one-time, if not done)
python convert_ensemble_to_tfjs.py

# 3. Start server
cd webapp
python -m http.server 8000

# 4. Open browser: http://localhost:8000
```

## Troubleshooting

### Model Conversion Fails

**Error:** "Model not found"
```cmd
# Check if models exist
dir models\fer_model_best.h5
dir models\pretrained\mobilenetv3_finetuned.h5
```

**Error:** "tensorflowjs_converter not found"
- The script will try alternative method automatically
- Or install tensorflowjs: `pip install tensorflowjs`

### Server Won't Start

**Error:** "Port 8000 already in use"
```cmd
# Use different port
python -m http.server 8080
# Then open: http://localhost:8080
```

### Model Not Loading in Browser

**Check:**
1. Open browser console (F12)
2. Look for errors
3. Verify `webapp/model/model.json` exists
4. Check server is running

### Camera Not Working

- Must use `http://localhost:8000` (not `file://`)
- Grant camera permissions in browser
- Use Chrome/Edge/Firefox (not IE)

## Testing on Mobile Device

### Option 1: Same Network (WiFi)

1. Find your computer's IP address:
```cmd
ipconfig
```
Look for "IPv4 Address" (e.g., `192.168.1.100`)

2. On your phone, open:
```
http://192.168.1.100:8000
```

### Option 2: USB Tethering

1. Connect phone via USB
2. Enable USB tethering on phone
3. Use computer's IP address as above

### Option 3: Deploy Online

Deploy to GitHub Pages, Netlify, or Vercel for public access.

## Complete Workflow

```cmd
REM === Complete Workflow ===

REM 1. Navigate to project
cd C:\Users\18003\Iot_proj

REM 2. Activate environment
fer_env\Scripts\activate

REM 3. Convert model (first time only)
python convert_ensemble_to_tfjs.py

REM 4. Start web server
cd webapp
python -m http.server 8000

REM 5. Open browser to http://localhost:8000
REM 6. Click "Start Camera" and test!
```

## Notes

- Keep the server running while testing
- Press `Ctrl+C` to stop the server
- Model conversion only needs to be done once (unless models change)
- The web app works offline after initial load (if PWA is installed)

