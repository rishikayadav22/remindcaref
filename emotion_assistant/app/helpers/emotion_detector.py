import cv2
from deepface import DeepFace

def detect_emotion(frame):
    try:
        result = DeepFace.analyze(
            frame,
            actions=['emotion'],
            enforce_detection=False
        )

        if isinstance(result, list):
            return result[0]['dominant_emotion']
        else:
            return result['dominant_emotion']

    except Exception as e:
        print("Emotion error:", e)
        return "Unknown"
def detect_emotion(img):
    from deepface import DeepFace
    result = DeepFace.analyze(img, actions=['emotion'])
    return result
