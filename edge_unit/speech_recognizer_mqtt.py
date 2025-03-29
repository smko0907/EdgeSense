import paho.mqtt.client as mqtt
import whisper
import pyaudio
import wave
import json
import time
import os
from datetime import datetime

BROKER = "192.168.219.150"  # <- Windows 노트북 IP
TOPIC = "edgesense/rpi5/speech"
MIC_DEVICE_INDEX = 1  # <- USB 마이크 인덱스로 바꿔야 할 수 있음

class SpeechRecognizer:
    def __init__(self, model_name="base"):
        self.model = whisper.load_model(model_name)
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.audio = pyaudio.PyAudio()

    def record_audio(self, duration=5):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"temp_{timestamp}.wav"
        print(f"[INFO] Recording audio for {duration} seconds...")

        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            input_device_index=MIC_DEVICE_INDEX,  # <- 설정 필요
            frames_per_buffer=self.chunk
        )

        frames = []
        for _ in range(0, int(self.rate / self.chunk * duration)):
            data = stream.read(self.chunk, exception_on_overflow=False)
            frames.append(data)

        stream.stop_stream()
        stream.close()

        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(frames))

        print(f"[INFO] Audio recorded and saved as: {filename}")
        return filename

    def transcribe(self, audio_file):
        print("[INFO] Transcribing audio...")
        result = self.model.transcribe(audio_file, launguage="ko")
        print(f"[RESULT] Recognized text: \"{result['text']}\"")

        segments = result.get("segments", [])
        confidence = segments[0].get("confidence", 0.95) if segments else 0.0
        return result['text'], confidence

def publish_to_mqtt(text, confidence):
    client = mqtt.Client()
    client.connect(BROKER, 1883, 60)

    payload = {
        "device_id": "rpi5",
        "sensor_type": "speech",
        "value": text,
        "confidence": confidence,
        "timestamp": time.time()
    }

    json_data = json.dumps(payload)
    client.publish(TOPIC, json_data)
    print(f"[MQTT] Published to topic '{TOPIC}': {json_data}")
    client.disconnect()

if __name__ == "__main__":
    recognizer = SpeechRecognizer()

    while True:
        audio_file = recognizer.record_audio(duration=5)
        text, confidence = recognizer.transcribe(audio_file)

        if text.strip():
            publish_to_mqtt(text, confidence)
        else:
            print("[WARN] No valid speech recognized. Skipping MQTT publish.")

        time.sleep(2)
