"""
config.py — CalmPath Backend Configuration
Load from .env file or environment variables.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Flask ──────────────────────────────────────────────
DEBUG          = os.getenv("FLASK_DEBUG", "true").lower() == "true"
HOST           = os.getenv("FLASK_HOST", "0.0.0.0")
PORT           = int(os.getenv("FLASK_PORT", "5000"))
SECRET_KEY     = os.getenv("SECRET_KEY", "calmpath-dev-secret-change-in-prod")

# ── CORS (add your frontend origins here) ─────────────
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "null",          # file:// opened directly in browser
    "*",             # dev convenience — restrict in production
]

# ── DeepFace ───────────────────────────────────────────
# Options: "VGG-Face" | "Facenet512" | "ArcFace" | "SFace"
# Facenet512 is most accurate; VGG-Face is fastest.
DEEPFACE_MODEL    = os.getenv("DEEPFACE_MODEL",    "VGG-Face")
DEEPFACE_DETECTOR = os.getenv("DEEPFACE_DETECTOR", "opencv")   # opencv | retinaface | mtcnn
DEEPFACE_ENFORCE  = os.getenv("DEEPFACE_ENFORCE",  "false").lower() == "true"

# ── Firebase Admin SDK ─────────────────────────────────
FIREBASE_CRED_PATH = os.getenv("FIREBASE_CRED_PATH", "firebase-adminsdk.json")
FIREBASE_ENABLED   = os.getenv("FIREBASE_ENABLED",   "false").lower() == "true"

# ── Emotion mapping ────────────────────────────────────
# DeepFace returns 7 emotions; we map to 5 student-safe labels
EMOTION_MAP = {
    "angry":     "frustrated",
    "disgust":   "frustrated",
    "fear":      "frustrated",
    "happy":     "happy",
    "sad":       "sad",
    "surprise":  "surprised",
    "neutral":   "neutral",
}

# ── Frustration threshold (triggers AI break suggestion) ──
FRUSTRATION_THRESHOLD = float(os.getenv("FRUSTRATION_THRESHOLD", "0.72"))

# ── Frame size expected from frontend ─────────────────
FRAME_WIDTH  = 320
FRAME_HEIGHT = 240