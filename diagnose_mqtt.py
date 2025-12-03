#!/usr/bin/env python3
"""
MQTT Diagnostic Tool - Run this to see exactly what's happening
"""
import paho.mqtt.client as mqtt
import ssl
import json
import time

CONFIG = {
    'HOST': '308c552d0a56494799306611ffacac19.s1.eu.hivemq.cloud',
    'PORT': 8883,
    'USERNAME': 'feronmobile',
    'PASSWORD': 'Qwerty123',
    'TOPIC': 'fer/events'
}

received_count = 0

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ CONNECTED to broker at {CONFIG['HOST']}")
        client.subscribe(CONFIG['TOPIC'], qos=0)
        print(f"✅ SUBSCRIBED to topic: {CONFIG['TOPIC']}")
        print("\n👂 Listening for messages... (Press Ctrl+C to stop)")
        print("=" * 60)
    else:
        print(f"❌ Connection FAILED with code {rc}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"\n⚠️  UNEXPECTED DISCONNECT! Code: {rc}")
        print("This might mean another client is using the same credentials")
    else:
        print("\n✅ Clean disconnect")

def on_message(client, userdata, msg):
    global received_count
    received_count += 1
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        user_id = payload.get('user_id', 'unknown')
        emotion = payload.get('emotion', 'unknown')
        print(f"\n📩 MESSAGE #{received_count} received:")
        print(f"   User: {user_id}")
        print(f"   Emotion: {emotion}")
        print(f"   Full payload: {json.dumps(payload, indent=2)}")
    except:
        print(f"\n📩 MESSAGE #{received_count} received (raw):")
        print(f"   {msg.payload}")
    print("=" * 60)

def main():
    print("\n🔍 MQTT Diagnostic Tool")
    print("=" * 60)
    print(f"Broker: {CONFIG['HOST']}:{CONFIG['PORT']}")
    print(f"Topic: {CONFIG['TOPIC']}")
    print(f"Username: {CONFIG['USERNAME']}")
    print("=" * 60)
    
    client_id = f"diagnostic_{int(time.time())}"
    print(f"Client ID: {client_id}\n")
    
    client = mqtt.Client(client_id=client_id)
    client.username_pw_set(CONFIG['USERNAME'], CONFIG['PASSWORD'])
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
    client.tls_insecure_set(False)
    
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    
    try:
        print("🔌 Connecting to broker...")
        client.connect(CONFIG['HOST'], CONFIG['PORT'], keepalive=60)
        client.loop_forever()
    except KeyboardInterrupt:
        print(f"\n\n📊 Summary: Received {received_count} messages")
        client.disconnect()
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == '__main__':
    main()
