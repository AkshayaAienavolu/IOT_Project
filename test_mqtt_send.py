import paho.mqtt.client as mqtt
import json
import time
import ssl

# Use the same config as the logger
CONFIG = {
    'WSS_URL': "wss://308c552d0a56494799306611ffacac19.s1.eu.hivemq.cloud:8884/mqtt",
    'HOST': "308c552d0a56494799306611ffacac19.s1.eu.hivemq.cloud",
    'PORT': 8883,
    'USERNAME': "feronmobile",
    'PASSWORD': "Qwerty123",
    'TOPIC': "fer/events"
}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker!")
        # Publish a test message
        payload = {
            "user_id": "TEST_USER_MANUAL",
            "emotion": "happy",
            "confidence": 0.99,
            "ts": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        }
        client.publish(CONFIG['TOPIC'], json.dumps(payload), qos=0)
        print(f"Sent test message to {CONFIG['TOPIC']}")
        time.sleep(2)  # Give time for message to send
        client.disconnect()
        print("Done!")
    else:
        print(f"Failed to connect: {rc}")

client = mqtt.Client(client_id="test_sender_" + str(int(time.time())))
client.username_pw_set(CONFIG['USERNAME'], CONFIG['PASSWORD'])
client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
client.tls_insecure_set(False)
client.on_connect = on_connect

print(f"Connecting to {CONFIG['HOST']}...")
client.connect(CONFIG['HOST'], CONFIG['PORT'], keepalive=60)
client.loop_forever()
