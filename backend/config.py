"""
config.py — CalmPath Backend Configuration (clean + safe version)
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Flask ──────────────────────────────────────────────

DEBUG      = os.getenv("FLASK_DEBUG", "true").lower() == "true"
HOST       = os.getenv("FLASK_HOST", "0.0.0.0")
PORT       = int(os.getenv("FLASK_PORT", "5000"))

# NEVER hardcode secrets in real projects

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-this")

# ── CORS ───────────────────────────────────────────────

# For development, allow all. Restrict in production.

# ── CORS ───────────────────────────────────────────────
if DEBUG:
    CORS_ORIGINS = ["*"]
else:
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:5500",
    ]

# ── DeepFace ───────────────────────────────────────────

# Options: "VGG-Face" | "Facenet512" | "ArcFace" | "SFace"

# VGG-Face = faster, Facenet512 = more accurate

DEEPFACE_MODEL = os.getenv("DEEPFACE_MODEL", "VGG-Face")

# Detector options: opencv (fast) | retinaface (accurate) | mtcnn

DEEPFACE_DETECTOR = os.getenv("DEEPFACE_DETECTOR", "opencv")

# If True → throws error when no face detected

# Keep False for smoother UX

DEEPFACE_ENFORCE = os.getenv("DEEPFACE_ENFORCE", "false").lower() == "true"

# ── Firebase (optional, not used yet) ──────────────────

FIREBASE_CRED_PATH = os.getenv("FIREBASE_CRED_PATH", "firebase-adminsdk.json")
FIREBASE_ENABLED   = os.getenv("FIREBASE_ENABLED", "false").lower() == "true"

# ── Supabase ───────────────────────────────────────────
_proj_id = os.getenv("SUPABASE_PROJECT_ID")
SUPABASE_URL = f"https://{_proj_id}.supabase.co" if _proj_id else None
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")


# ── Emotion Mapping ────────────────────────────────────

# Convert DeepFace 7 emotions → 5 app-safe emotions

EMOTION_MAP = {
"angry":     "frustrated",
"disgust":   "frustrated",
"fear":      "frustrated",
"happy":     "happy",
"sad":       "sad",
"surprise":  "surprised",
"neutral":   "neutral",
}

# ── Frustration Threshold ──────────────────────────────

# When frustration crosses this, trigger "take a break"

FRUSTRATION_THRESHOLD = float(os.getenv("FRUSTRATION_THRESHOLD", "0.72"))

# ── Frame Size (must match frontend webcam settings) ───

FRAME_WIDTH  = int(os.getenv("FRAME_WIDTH", "320"))
FRAME_HEIGHT = int(os.getenv("FRAME_HEIGHT", "240"))