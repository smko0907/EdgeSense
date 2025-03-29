import paho.mqtt.client as mqtt
import json
import time

BROKER = "192.168.219.150"  # notebook ip
TOPIC = "edgesense/pi01/sensor"

def create_payload():
    return {
        "device_id": "pi01",
        "sensor_type": "speech",
        "value": "start",
        "confidence": 0.95,
        "timestamp": time.time()
    }

def main():
    client = mqtt.Client()
    client.connect(BROKER, 1883, 60)
    print(f"📡 Connected to MQTT Broker: {BROKER}")

    while True:
        payload = create_payload()
        json_payload = json.dumps(payload)
        client.publish(TOPIC, json_payload)
        print(f"Published to {TOPIC}: {json_payload}")
        time.sleep(3)

if __name__ == "__main__":
    main()
