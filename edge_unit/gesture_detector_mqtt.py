import cv2
import numpy as np
import tensorflow as tf
import mediapipe as mp
import paho.mqtt.client as mqtt
import json
import time

# MQTT 설정
BROKER = "192.168.219.150"  # Windows 노트북 IP
TOPIC = "edgesense/rpi5/gesture"

# 모델 및 레이블 로드
MODEL_NAME = 'gesture_model'
model = tf.keras.models.load_model(f"{MODEL_NAME}.h5")
class_names = np.load("gesture_label_classes.npy", allow_pickle=True)

# MediaPipe Hands 설정
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# 랜드마크 추출 함수
def extract_landmarks(image):
    results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.extend([lm.x, lm.y, lm.z])
            return np.array(landmarks), hand_landmarks
    return None, None

# MQTT 전송 함수
def publish_to_mqtt(label, confidence):
    client = mqtt.Client()
    client.connect(BROKER, 1883, 60)

    payload = {
        "device_id": "rpi5",
        "sensor_type": "gesture",
        "value": label,
        "confidence": float(confidence),
        "timestamp": time.time()
    }

    json_data = json.dumps(payload)
    client.publish(TOPIC, json_data)
    print(f"[MQTT] Published: {json_data}")
    client.disconnect()

# 웹캠 시작
cap = cv2.VideoCapture(0)
print("[INFO] Press 'q' to quit.")

last_label = None
last_publish_time = 0
PUBLISH_INTERVAL = 3  # 동일 제스처일 경우 최소 3초 간격으로 전송

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    input_data, hand_landmarks = extract_landmarks(frame)

    if input_data is not None:
        input_data = np.expand_dims(input_data, axis=0)
        prediction = model.predict(input_data)[0]
        predicted_index = np.argmax(prediction)
        confidence = prediction[predicted_index]
        predicted_label = class_names[predicted_index]

        # 화면에 출력
        display_text = f"{predicted_label} ({confidence*100:.1f}%)"
        cv2.putText(frame, display_text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 191, 0), 2)
        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # MQTT 전송 조건: 새 제스처 or 일정 시간 경과
        current_time = time.time()
        if (predicted_label != last_label) or (current_time - last_publish_time > PUBLISH_INTERVAL):
            publish_to_mqtt(predicted_label, confidence)
            last_label = predicted_label
            last_publish_time = current_time

    else:
        cv2.putText(frame, "No hand detected", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100), 2)

    cv2.imshow("Live Gesture Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
