import cv2
import numpy as np
from openni import openni2
from flask import Flask, Response

# Initialize OpenNI once at the top
openni2.initialize()
device = openni2.Device.open_any()

# Start the color stream
color_stream = device.create_color_stream()
color_stream.start()

# Load your Haar Cascade
# face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

app = Flask(__name__)

def gen_frames():
    """
    Generator function that captures frames from the camera,
    annotates them (face detection), and yields them as JPEG byte arrays
    for the MJPEG stream.
    """
    while True:
        # Read a color frame
        frame = color_stream.read_frame()
        frame_data = frame.get_buffer_as_uint8()
        w, h = frame.width, frame.height

        # Convert frame data to NumPy array, then to BGR
        img = np.frombuffer(frame_data, dtype=np.uint8).reshape((h, w, 3))
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # Detect faces
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)

        # Draw rectangles around faces
        for (x, y, w_box, h_box) in faces:
            cv2.rectangle(img_bgr, (x, y), (x + w_box, y + h_box), (0, 255, 0), 2)

        # Encode as JPEG
        ret, buffer = cv2.imencode('.jpg', img_bgr)
        if not ret:
            continue  # if something went wrong encoding, skip

        # Convert to bytes and yield in HTTP multipart format
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    # A simple landing page
    return "<h2>공장 CCTV - Astra Pro (OpenNI) with 얼굴 감지 </h2>" \
           "<p>실시간 영상 확인은 <a href='/video_feed'>여기서</a> 가능합니다</p>"

@app.route('/video_feed')
def video_feed():
    """
    MJPEG stream route. This route yields raw JPEG frames one after another
    (multipart/x-mixed-replace). 
    """
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    try:
        # Start Flask web server on port 5000 (or choose another if you prefer)
        app.run(host='0.0.0.0', port=5000, debug=False)
    finally:
        # Clean up when the Flask server stops
        color_stream.stop()
        openni2.unload()
