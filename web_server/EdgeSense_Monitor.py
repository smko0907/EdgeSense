from flask import Flask, Response, request, render_template_string
import cv2
import numpy as np
from openni import openni2

openni2.initialize()
device = openni2.Device.open_any()
color_stream = device.create_color_stream()
color_stream.start()

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

app = Flask(__name__)
latest_command = ""

def gen_frames():
    while True:
        frame = color_stream.read_frame()
        frame_data = frame.get_buffer_as_uint8()
        w, h = frame.width, frame.height
        img = np.frombuffer(frame_data, dtype=np.uint8).reshape((h, w, 3))
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)

        for (x, y, w_box, h_box) in faces:
            cv2.rectangle(img_bgr, (x, y), (x + w_box, y + h_box), (0, 255, 0), 2)

        ret, buffer = cv2.imencode('.jpg', img_bgr)
        if not ret:
            continue
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    with open('dashboard.html', encoding='utf-8') as f:
        return render_template_string(f.read())

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/command', methods=['POST'])
def receive_command():
    global latest_command
    command = request.json.get("message")
    if command == "stop":
        latest_command = """작업자가 "정지"를 요청했습니다!"""
    elif command == "come here":
        latest_command = "작업장으로 와주세요!"
    else:
        latest_command = ""
    return {"status": "ok"}

@app.route('/latest_command')
def get_latest_command():
    return {"command": latest_command}

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        color_stream.stop()
        openni2.unload()
