
import cv2
import os
from datetime import datetime
from django.core.files import File
from .helpers.emotion_detector import detect_emotion
from .models import EmotionSnapshot

# Folder to store snapshots locally
SNAPSHOT_DIR = "snapshots"
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

class VideoCamera:
    """
    Handles video capture, emotion detection, and snapshot saving for rapid emotion changes.
    """
    def __init__(self, switch_threshold=2):
        self.video = cv2.VideoCapture(0)
        self.previous_emotion = None
        self.last_switch_time = None
        self.switch_threshold = switch_threshold  # seconds

    def __del__(self):
        self.video.release()

    def capture_snapshot(self, frame, emotion):
        """
        Save snapshot locally and in Django DB with timestamp.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"emotion_{emotion}_{timestamp}.jpg"
        filepath = os.path.join(SNAPSHOT_DIR, filename)

        # Save locally
        cv2.imwrite(filepath, frame)
        print(f"[Snapshot] {emotion} captured at {timestamp}")

        # Save to DB
        try:
            with open(filepath, "rb") as f:
                django_file = File(f)
                snapshot = EmotionSnapshot(emotion=emotion)
                snapshot.image.save(filename, django_file, save=True)
        except Exception as e:
            print(f"Error saving snapshot to DB: {e}")

    def get_frame(self):
        """
        Capture a frame, detect emotion, check for rapid switch, and return JPEG + emotion.
        """
        success, frame = self.video.read()
        if not success:
            return None, None

        # Detect emotion using DeepFace
        emotion = detect_emotion(frame)

        # Check for rapid emotion switch
        now = datetime.now()
        if self.previous_emotion is not None and emotion != self.previous_emotion:
            # If last switch was within threshold or first switch
            if self.last_switch_time is None or (now - self.last_switch_time).total_seconds() <= self.switch_threshold:
                self.capture_snapshot(frame, emotion)
            self.last_switch_time = now

        self.previous_emotion = emotion

        # Draw emotion text on video frame
        cv2.putText(frame, f"Emotion: {emotion}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2)

        # Encode frame as JPEG
        _, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes(), emotion
