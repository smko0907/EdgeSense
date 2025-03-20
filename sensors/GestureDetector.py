import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Initialize video capture
cap = cv2.VideoCapture(0)

# Track finger movements for "Come Here"
finger_motion_count = 0
prev_finger_state = None

# Define hand tracking
with mp_hands.Hands(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    max_num_hands=1  # Track only one hand
) as hands:

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Flip frame horizontally for better tracking
        frame = cv2.flip(frame, 1)

        # Convert frame to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)

        gesture = "No Gesture"

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )

                # Extract landmark coordinates
                landmarks = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark])

                # Identify if fingers are up
                def is_finger_up(finger_tip, finger_base):
                    return landmarks[finger_tip][1] < landmarks[finger_base][1]  # Y-axis check

                fingers = [
                    is_finger_up(8, 6),  # Index
                    is_finger_up(12, 10),  # Middle
                    is_finger_up(16, 14),  # Ring
                    is_finger_up(20, 18)  # Pinky
                ]
                thumb_tip = landmarks[4]  # Thumb tip
                index_tip = landmarks[8]  # Index tip
                middle_tip = landmarks[12]  # Middle tip

                # Check if thumb and index tip are close (OK sign)
                thumb_index_distance = np.linalg.norm(thumb_tip[:2] - index_tip[:2])
                thumb_middle_distance = np.linalg.norm(thumb_tip[:2] - middle_tip[:2])
                
                is_ok_sign = thumb_index_distance < 0.05 and fingers[1] and fingers[2] and fingers[3]  # Middle, ring, pinky are extended

                # Count open fingers
                fingers_open = fingers.count(True) + (1 if is_finger_up(4, 2) else 0)

                # Detect "Stop" Gesture (All fingers open)
                if fingers_open == 5:
                    gesture = "Stop"

                # Improved Palm Orientation Detection (Wrist vs Middle Finger Base)
                wrist_y = landmarks[0][1]  # Wrist Y-coordinate
                mid_base_y = landmarks[9][1]  # Middle Finger Base Y-coordinate
                
                palm_down = wrist_y > mid_base_y  # If wrist is below middle base, palm is down
                palm_up = wrist_y < mid_base_y  # If wrist is above middle base, palm is up

                # Detect "Come Here" Gesture (Palm Up + Repeated Finger Movement)
                if palm_up:
                    moving_fingers = sum(fingers) in [1, 4]  # Only 1 or 4 fingers move
                    if moving_fingers:
                        if prev_finger_state != moving_fingers:
                            finger_motion_count += 1
                            prev_finger_state = moving_fingers

                        if finger_motion_count >= 3:  # Detect repeated motion
                            gesture = "Come Here"

                # Detect "OK" Gesture
                if is_ok_sign:
                    gesture = "OK"

        # Display gesture result
        cv2.putText(frame, gesture, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        # Show output
        cv2.imshow("Hand Gesture Recognition", frame)

        # Press 'q' to exit
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

# Cleanup
cap.release()
cv2.destroyAllWindows()
