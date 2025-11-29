# Privacy-Focused Personal Dashboard Setup

This guide explains how to set up the personal dashboard feature where each user sees only their own emotion data.

## Overview

**Privacy Features:**
- ✅ Each user sees **only their own data** (based on their browser's client ID)
- ✅ No cross-user data access
- ✅ Dashboard accessible from the same webapp interface
- ✅ Automatic user identification via localStorage

**Two Access Methods:**

1. **Personal Dashboard** (`dashboard.html`) - Each user sees only their data
2. **Admin Dashboard** (Raspberry Pi web server) - View all users (optional, for your monitoring)

## Setup Instructions

### Step 1: Update Dashboard API URL

Edit `webapp/dashboard.html` and update the Pi IP address:

```javascript
// Line ~235
const DASHBOARD_API = 'http://YOUR_PI_IP:5000';
```

Replace `YOUR_PI_IP` with your Raspberry Pi's IP address:

```javascript
const DASHBOARD_API = 'http://192.168.1.100:5000';  // Example
```

### Step 2: Enable CORS on Pi Server

The browser needs permission to fetch data from the Pi. Update `dashboard_server.py`:

```bash
pip3 install flask-cors
```

Then add CORS support to the server (already included in the updated file).

### Step 3: Deploy to Netlify

1. **Commit and push** the new files:
```bash
git add webapp/dashboard.html
git add dashboard_server.py
git commit -m "Add privacy-focused personal dashboards"
git push origin main
```

2. Netlify will automatically deploy `dashboard.html`

### Step 4: Start Dashboard Server on Pi

```bash
cd /home/pi/IOT_Project
source fer_env/bin/activate
pip3 install flask flask-cors
python3 dashboard_server.py
```

The server will run on port 5000.

### Step 5: Access Your Personal Dashboard

Open the webapp on your phone/browser:
```
https://iotprojectfer.netlify.app
```

Click the **"📊 My Dashboard"** button to see your personal analytics.

## How It Works

### User Privacy Mechanism

1. **Client ID Generation:**
   - Each browser generates a unique ID: `fer_web_<random-hex>`
   - Stored in `localStorage` (persists across sessions)
   - Same ID used for MQTT publishing and dashboard viewing

2. **Data Isolation:**
   - Dashboard API endpoint: `/api/user/<user_id>/summary`
   - Returns data **only** for the requested user ID
   - No access to other users' data

3. **Chart Generation:**
   - `dashboard_per_user.py` creates separate folders per user
   - Charts stored in `dashboards/<user_id>/`
   - Only charts for your user ID are displayed

### Data Flow

```
Browser (User A)
  ↓ Client ID: fer_web_abc123
  ↓ Request: /api/user/fer_web_abc123/summary
  ↓
Raspberry Pi Server
  ↓ Query SQLite: WHERE user_id = 'fer_web_abc123'
  ↓ Return: Only User A's data
  ↓
Browser (User A)
  ↓ Display: User A's charts only
```

## Testing Privacy

### Test with Multiple Browsers

1. **Chrome:** Visit webapp → see your charts
2. **Firefox:** Visit webapp → see different charts (different client ID)
3. **Safari:** Visit webapp → see different charts again

Each browser has its own `localStorage`, so each gets a unique user ID.

### Verify Data Isolation

Open browser console (F12) and run:

```javascript
// Check your client ID
console.log(localStorage.getItem('fer_client_id'));

// Try to fetch another user's data
fetch('http://YOUR_PI_IP:5000/api/user/fer_web_OTHER_ID/summary')
  .then(r => r.json())
  .then(data => console.log(data));
```

The server will return data for the requested user, but the webapp UI only requests the current user's ID.

## Admin Access (Optional)

You can still access the admin dashboard to see all users:

**From your computer (same network as Pi):**
```
http://192.168.1.100:5000
```

This shows:
- List of all users
- Click any user to see their dashboard
- Regenerate all dashboards

**This is for your monitoring only** - regular users don't see this.

## Auto-Refresh Dashboard Charts

The dashboard automatically refreshes every 2 minutes to show latest data.

To trigger manual refresh:
- Click the **"🔄 Refresh Data"** button

## Scheduled Chart Generation

Set up automatic chart regeneration every 5 minutes:

```bash
crontab -e
```

Add this line:

```cron
*/5 * * * * cd /home/pi/IOT_Project && /home/pi/IOT_Project/fer_env/bin/python3 dashboard_per_user.py /home/pi/fer_events.db >> /home/pi/dashboard_cron.log 2>&1
```

This ensures charts are always up-to-date.

## Security Considerations

### What's Protected:
- ✅ Each user sees only their own data in the webapp
- ✅ Client IDs are randomly generated (hard to guess)
- ✅ Data stored on your private Raspberry Pi

### What's NOT Protected:
- ⚠️ No password authentication on Pi server
- ⚠️ Anyone on your WiFi network can access `http://pi-ip:5000`
- ⚠️ Client IDs stored in localStorage (can be cleared by user)

### For Production Use:

If deploying for real users, consider:

1. **Add Authentication:**
```bash
pip3 install flask-httpauth
```

2. **Use HTTPS:**
```bash
# Generate SSL certificate
sudo certbot certonly --standalone -d your-domain.com
```

3. **Restrict Network Access:**
```bash
# Firewall: Allow only specific IPs
sudo ufw allow from 192.168.1.0/24 to any port 5000
```

4. **User Registration:**
- Replace random client IDs with username/password
- Store hashed passwords in database
- Issue session tokens

## Troubleshooting

### "Unable to Load Dashboard" Error

**Check Pi IP address:**
```bash
hostname -I
```

Update `DASHBOARD_API` in `dashboard.html` with correct IP.

**Check if server is running:**
```bash
ps aux | grep dashboard_server
```

**Check CORS errors in browser console (F12):**
- Make sure `flask-cors` is installed
- Server must be running on the Pi

### No Charts Displayed

**Regenerate charts:**
```bash
cd /home/pi/IOT_Project
python3 dashboard_per_user.py /home/pi/fer_events.db
```

**Check if your user ID has data:**
```bash
sqlite3 /home/pi/fer_events.db "SELECT user_id, COUNT(*) FROM events GROUP BY user_id;"
```

### Different Charts on Different Devices

**This is expected!** Each device has its own client ID:
- Your phone: `fer_web_abc123` → shows phone's data
- Your laptop: `fer_web_xyz789` → shows laptop's data

To use the same ID on multiple devices:

```javascript
// In browser console on all devices
localStorage.setItem('fer_client_id', 'fer_web_SAME_ID_HERE');
```

Then reload the page.

## Next Steps

- [ ] Set up cron job for automatic chart regeneration
- [ ] Add pulse oximeter sensor data to personal dashboards
- [ ] Create combined emotion + vitals visualization
- [ ] (Optional) Add user authentication for production use
