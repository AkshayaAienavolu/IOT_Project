"""
mqtt_logger.py

Simple MQTT subscriber for Raspberry Pi to log incoming emotion events to SQLite.

Usage:
  - Install dependencies: `pip install paho-mqtt`
  - Configure via environment variables or edit the CONFIG dictionary below.
  - Run: `python mqtt_logger.py`

The script will create `fer_events.db` in the same folder and append incoming JSON payloads.
"""

import os
import json
import time
import sqlite3
import logging
from urllib.parse import urlparse
import ssl

import paho.mqtt.client as mqtt

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

# === Configuration ===
# You can override these with environment variables.
CONFIG = {
    'WSS_URL': os.environ.get('WSS_URL', ''),  # e.g. wss://abc123.s1.eu.hivemq.cloud:8883/mqtt
    'HOST': os.environ.get('MQTT_HOST', ''),   # optional, parsed from WSS_URL if empty
    'PORT': int(os.environ.get('MQTT_PORT', '8883')),
    'USERNAME': os.environ.get('MQTT_USERNAME', ''),
    'PASSWORD': os.environ.get('MQTT_PASSWORD', ''),
    'TOPIC': os.environ.get('MQTT_TOPIC', 'fer/events'),
    'CLIENT_ID': os.environ.get('MQTT_CLIENT_ID', 'fer_logger_' + str(int(time.time())))
}

DB_FILE = os.environ.get('FER_DB', 'fer_events.db')


def ensure_db(path=DB_FILE):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts_received TEXT,
        payload TEXT,
        user_id TEXT,
        emotion TEXT,
        confidence REAL
    );
    ''')
    conn.commit()
    conn.close()


def insert_event(payload_json):
    try:
        data = json.loads(payload_json)
    except Exception:
        data = {'raw': payload_json}

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    ts = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    user_id = data.get('user_id') if isinstance(data, dict) else None
    emotion = data.get('emotion') if isinstance(data, dict) else None
    confidence = data.get('confidence') if isinstance(data, dict) else None
    cur.execute('INSERT INTO events (ts_received, payload, user_id, emotion, confidence) VALUES (?, ?, ?, ?, ?)',
                (ts, json.dumps(data), user_id, emotion, confidence))
    conn.commit()
    conn.close()
    logging.info('Logged event: user=%s emotion=%s', user_id, emotion)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info('Connected to MQTT broker')
        client.subscribe(CONFIG['TOPIC'], qos=1)
        logging.info('Subscribed to topic %s', CONFIG['TOPIC'])
    else:
        logging.error('Failed to connect: rc=%s', rc)


def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8', errors='ignore')
    logging.debug('Received message on %s: %s', msg.topic, payload)
    insert_event(payload)


def main():
    # If WSS_URL provided, try to parse host/port
    if CONFIG['WSS_URL'] and not CONFIG['HOST']:
        try:
            parsed = urlparse(CONFIG['WSS_URL'])
            CONFIG['HOST'] = parsed.hostname
            CONFIG['PORT'] = parsed.port or CONFIG['PORT']
        except Exception:
            pass

    if not CONFIG['HOST']:
        logging.error('No MQTT host configured. Set WSS_URL or MQTT_HOST env var.')
        return

    ensure_db()

    client = mqtt.Client(client_id=CONFIG['CLIENT_ID'])
    if CONFIG['USERNAME']:
        client.username_pw_set(CONFIG['USERNAME'], CONFIG['PASSWORD'])

    # Use TLS
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
    client.tls_insecure_set(False)

    client.on_connect = on_connect
    client.on_message = on_message

    try:
        logging.info('Connecting to %s:%s', CONFIG['HOST'], CONFIG['PORT'])
        client.connect(CONFIG['HOST'], CONFIG['PORT'], keepalive=60)
    except Exception as e:
        logging.exception('Connection failure: %s', e)
        return

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        logging.info('Interrupted, stopping')
        client.disconnect()


if __name__ == '__main__':
    main()
