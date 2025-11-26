# FER Mobile HTTPS Deployment

## Quick Start (HTTPS)

Your webapp is ready to serve over HTTPS using your self-signed certificate.

### Option 1: Double-click to start (Windows)
```
webapp/start_https.bat
```
Then open: **https://127.0.0.1:8443**

### Option 2: Command line (PowerShell)
```powershell
cd C:\Users\18003\Iot_proj\webapp
python serve_https.py
```

## Access from Phone

1. **Get your laptop IP:**
```powershell
ipconfig | findstr IPv4
# Look for: IPv4 Address . . . . . . . . . . . . . : 192.168.x.x
```

2. **On phone browser (same Wi-Fi), visit:**
```
https://192.168.x.x:8443
```

3. **Browser warning:** You'll see "Not secure" (normal for self-signed certs)
   - Click "Advanced" or "Not secure" 
   - Click "Proceed anyway"

4. **Grant camera permission** when prompted

5. **Click "Start Camera"** and show your face

## Permanent HTTPS Link

This setup gives you a **permanent HTTPS link** (as long as the server is running):
- Same link for all users: `https://<your-laptop-ip>:8443`
- No setup on user devices — just open the link
- Camera access works (HTTPS is secure)
- Model runs on-device (no server computation)

## Notes

- **Self-signed certificate**: Your certificate was generated for testing. Production deployments should use a proper CA (Let's Encrypt, etc.)
- **Port 8443**: Standard HTTPS port. You can change it in `serve_https.py` (line 28)
- **Firewall**: Ensure Windows firewall allows Python on port 8443 (or temporarily disable for testing)
- **Server must be running**: Unlike cloud hosting, you must keep this terminal open. For persistent hosting, use GitHub Pages, Netlify, or a VPS.

## Keep Server Running

To keep the HTTPS server running 24/7:
- **Option A**: Keep the terminal/batch file open (simple for testing)
- **Option B**: Use a VPS (AWS, DigitalOcean, Linode) and deploy your `webapp/` there with systemd service
- **Option C**: Use ngrok to tunnel through firewall (temporary)
- **Option D**: Use cloud hosting like GitHub Pages (easiest for permanent)

For now, the HTTPS server is ready!
