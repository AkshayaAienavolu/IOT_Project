# Troubleshooting Guide

## Common Issues and Solutions

### "Failed to start — see console"

#### 1. Check Browser Console (F12)
Open Developer Tools (F12) and check the Console tab for specific errors.

#### 2. MediaPipe Not Loading
**Error:** "FaceDetection not loaded" or "MediaPipe error"

**Solutions:**
- Check internet connection (MediaPipe loads from CDN)
- Try refreshing the page
- Check if CDN is blocked (corporate firewall, etc.)
- Alternative: Use a different browser

#### 3. Model Not Loading
**Error:** "Failed to load model"

**Check:**
- Verify `webapp/model/model.json` exists
- Check that all `.bin` files are present
- Ensure HTTP server is running (not `file://`)
- Check browser console for CORS errors

#### 4. Camera Not Working
**Error:** "Camera access denied"

**Solutions:**
- Grant camera permissions in browser settings
- Use `http://localhost:8000` (not `file://`)
- Try a different browser (Chrome/Edge recommended)
- Check if another app is using the camera

#### 5. CORS Errors
**Error:** "Cross-Origin Request Blocked"

**Solution:**
- Must use HTTP server (not `file://`)
- Run: `python -m http.server 8000` from `webapp/` folder
- Access via `http://localhost:8000`

### Quick Debug Steps

1. **Open Browser Console (F12)**
   - Look for red error messages
   - Check Network tab for failed requests

2. **Verify Files Exist**
   ```cmd
   dir webapp\model
   ```
   Should see: `model.json` and 5 `.bin` files

3. **Check Server is Running**
   - Should see: "Serving HTTP on :: port 8000"
   - Access: `http://localhost:8000`

4. **Test Model Loading**
   - Open: `http://localhost:8000/model/model.json`
   - Should see JSON content (not 404)

5. **Test MediaPipe**
   - Check Network tab in DevTools
   - Look for requests to `cdn.jsdelivr.net`
   - Should see successful (200) responses

### Still Not Working?

1. **Clear Browser Cache**
   - Press Ctrl+Shift+Delete
   - Clear cached images and files

2. **Try Different Browser**
   - Chrome/Edge: Best support
   - Firefox: Good support
   - Safari: iOS 11.3+ required

3. **Check Firewall/Antivirus**
   - May block CDN requests
   - Temporarily disable to test

4. **Use Local MediaPipe (Advanced)**
   - Download MediaPipe files locally
   - Update paths in `index.html`

### Getting Help

If still stuck, provide:
1. Browser console errors (screenshot)
2. Browser name and version
3. Operating system
4. Steps you've tried

