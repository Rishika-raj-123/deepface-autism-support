from deepface import DeepFace
import threading

# global model variable
_model = None

# thread lock (safe for multiple requests)
_lock = threading.Lock()


def load_model():
    global _model

    if _model is None:
        with _lock:
            if _model is None:
                print("Loading DeepFace emotion model...")
                _model = DeepFace.build_model("Emotion")
                print("Model loaded successfully")


def analyze_emotion(frame):

    # make sure model is loaded
    load_model()

    result = DeepFace.analyze(
        frame,
        actions=["emotion"],
        enforce_detection=False
    )

    return result[0]