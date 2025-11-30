// MQTT client helper for the webapp.
// Relies on `mqtt` global (mqtt.min.js). Reads `window.MQTT_CONFIG` provided by mqtt_config.js

(function () {
  if (typeof mqtt === 'undefined') {
    console.warn('mqtt library not found. MQTT will be disabled.');
    return;
  }

  const cfg = window.MQTT_CONFIG || null;
  if (!cfg) {
    console.warn('MQTT_CONFIG not found. Copy mqtt_config.example.js to mqtt_config.js and fill credentials.');
    return;
  }

  let client = null;

  // Ensure a stable client id per browser/device: prefer configured CLIENT_ID,
  // otherwise persist a generated id to localStorage AND cookie for extra persistence
  function ensureClientId() {
    try {
      if (cfg.CLIENT_ID) return cfg.CLIENT_ID;
      const key = 'fer_client_id';
      let id = null;
      
      // Try localStorage first
      try { id = localStorage.getItem(key); } catch (e) { /* localStorage may be unavailable */ }
      
      // If not in localStorage, try cookie as backup
      if (!id) {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
          const [name, value] = cookie.trim().split('=');
          if (name === key) {
            id = value;
            break;
          }
        }
      }
      
      // Generate new ID if still not found
      if (!id) {
        // Use crypto-safe id when available
        if (typeof crypto !== 'undefined' && crypto.getRandomValues) {
          const buf = new Uint8Array(8);
          crypto.getRandomValues(buf);
          id = 'fer_webapp_' + Array.from(buf).map(b => b.toString(16).padStart(2, '0')).join('');
        } else {
          id = 'fer_webapp_' + Math.random().toString(16).slice(2, 10);
        }
        
        // Store in BOTH localStorage AND cookie (365 days expiry)
        try { localStorage.setItem(key, id); } catch (e) { /* ignore write errors */ }
        try {
          const expires = new Date();
          expires.setFullYear(expires.getFullYear() + 1);
          document.cookie = `${key}=${id}; expires=${expires.toUTCString()}; path=/; SameSite=Strict`;
        } catch (e) { /* ignore cookie errors */ }
      } else {
        // ID found, ensure it's in both storages
        try { localStorage.setItem(key, id); } catch (e) { /* ignore */ }
        try {
          const expires = new Date();
          expires.setFullYear(expires.getFullYear() + 1);
          document.cookie = `${key}=${id}; expires=${expires.toUTCString()}; path=/; SameSite=Strict`;
        } catch (e) { /* ignore */ }
      }
      
      cfg.CLIENT_ID = id;
      return id;
    } catch (e) {
      // Fallback
      cfg.CLIENT_ID = cfg.CLIENT_ID || ('fer_web_' + Math.random().toString(16).slice(2, 8));
      return cfg.CLIENT_ID;
    }
  }

  function connect() {
    try {
      const options = {
        keepalive: 30,
        clientId: ensureClientId(),
        username: cfg.USERNAME,
        password: cfg.PASSWORD,
        reconnectPeriod: 2000,
        clean: true,
        connectTimeout: 30 * 1000
      };

      client = mqtt.connect(cfg.WSS_URL, options);

      client.on('connect', function () {
        console.log('MQTT connected to', cfg.WSS_URL);
      });

      client.on('reconnect', function () {
        console.log('MQTT reconnecting...');
      });

      client.on('error', function (err) {
        console.warn('MQTT error', err && err.message || err);
      });

      client.on('close', function () {
        console.log('MQTT connection closed');
      });

    } catch (e) {
      console.error('Failed to start MQTT client', e);
    }
  }

  // Expose init function
  window.initMqtt = function () {
    if (client && client.connected) return;
    connect();
  };

  // publishEmotionEvent(userId, emotion, confidence, bbox)
  if (typeof window.publishEmotionEvent === 'undefined') {
    window.publishEmotionEvent = function (userId, emotion, confidence, bbox) {
      if (!client || !client.connected) {
        console.debug('MQTT not connected; skipping publish');
        return;
      }

      const payload = {
        user_id: userId || null,
        emotion: emotion || null,
        confidence: typeof confidence === 'number' ? confidence : null,
        bbox: bbox || null,
        ts: new Date().toISOString()
      };

      try {
        client.publish(cfg.TOPIC, JSON.stringify(payload), { qos: cfg.QOS || 0 }, function (err) {
          if (err) console.warn('MQTT publish error', err);
        });
      } catch (e) {
        console.warn('MQTT publish exception', e);
      }
    };
  }

  // Auto-init
  try { window.initMqtt(); } catch (e) { /* ignore */ }

})();
