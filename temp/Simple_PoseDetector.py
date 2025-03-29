import cv2
import mediapipe as mp
import numpy as np

class PoseDetector:
    def __init__(self, mode=False, model_complexity=1, smooth_landmarks=True, detection_confidence=0.5, tracking_confidence=0.5):
        """Initialize the pose detector using MediaPipe."""
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=mode,
            model_complexity=model_complexity,
            smooth_landmarks=smooth_landmarks,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils

    def detect_pose(self, frame):
        """Detect human pose and return keypoints."""
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)
        return results

    def draw_landmarks(self, frame, results):
        """Draw pose landmarks on the image."""
        if results.pose_landmarks:
            self.mp_draw.draw_landmarks(frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
        return frame

    def get_keypoints(self, results):
        """Extract keypoints from the detected pose."""
        if not results.pose_landmarks:
            return None
        
        keypoints = []
        for landmark in results.pose_landmarks.landmark:
            keypoints.append((landmark.x, landmark.y, landmark.z))
        return np.array(keypoints)

    def recognize_gesture(self, keypoints):
        """Basic gesture recognition based on keypoint positions."""
        if keypoints is None:
            return "No Pose Detected"

        # Example: Detect raised hands
        left_wrist = keypoints[15]  # Index for left wrist
        right_wrist = keypoints[16]  # Index for right wrist
        nose = keypoints[0]  # Nose position

        if left_wrist[1] < nose[1] and right_wrist[1] < nose[1]:
            return "Hands Raised"
        elif left_wrist[1] > nose[1] and right_wrist[1] > nose[1]:
            return "Hands Down"
        return "Unknown Gesture"

def main():
    """Run real-time pose detection."""
    cap = cv2.VideoCapture(0)  # Open webcam (Change to video file path if needed)
    detector = PoseDetector()

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        results = detector.detect_pose(frame)
        frame = detector.draw_landmarks(frame, results)
        keypoints = detector.get_keypoints(results)
        gesture = detector.recognize_gesture(keypoints)

        cv2.putText(frame, f"Gesture: {gesture}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Pose Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
