# netsh advfirewall firewall add rule name="MQTT" dir=in action=allow protocol=TCP localport=1883 
# mosquitto.exe -c "C:\Program Files\mosquitto\mosquitto.conf" -v 

import paho.mqtt.client as mqtt

BROKER = "localhost"  # 외부 브로커가 아닌 내 노트북이 브로커니까 localhost
TOPIC = "edgesense/rpi5/sensor"

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker (rc={rc})")
    client.subscribe(TOPIC)
    print(f"Subscribed to: {TOPIC}")

def on_message(client, userdata, msg):
    print(f"📨 Received message on {msg.topic}: {msg.payload.decode()}")

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, 1883, 60)
    client.loop_forever()

if __name__ == "__main__":
    main()
