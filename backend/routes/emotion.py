"""
routes/emotion.py
POST /emotion

Receives a base64 webcam frame from index.html (student page),
runs DeepFace analysis, returns mapped emotion scores.

Expected JSON body:
    {
        "frame":     "data:image/jpeg;base64,/9j/...",
        "studentId": "student-001",          // optional
        "taskId":    "demo-1"                // optional
    }

Response (200):
    {
        "dominant":      "neutral",
        "confidence":    0.68,
        "look_away":     false,
        "rawScores": {
            "happy":      0.12,
            "frustrated": 0.07,
            "neutral":    0.68,
            "sad":        0.08,
            "surprised":  0.05
        },
        "processing_ms": 142,
        "model":         "VGG-Face"
    }

Response (400 / 500):
    { "error": "..." }
"""
import logging
from flask import Blueprint, request, jsonify

from services.emotion_service import analyse_frame, get_model_name, is_model_ready

logger = logging.getLogger(__name__)

emotion_bp = Blueprint("emotion", __name__)


@emotion_bp.route("/emotion", methods=["POST"])
def emotion():
    # ── 1. Parse request ──────────────────────────────
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    frame_data = data.get("frame", "").strip()
    if not frame_data:
        return jsonify({"error": "Missing 'frame' field"}), 400
    
    # Optional: Add size validation to prevent abuse
    if len(frame_data) > 200000:  # ~150KB for base64 image
        logger.warning("Frame too large: %d bytes", len(frame_data))
        return jsonify({"error": "Frame too large"}), 413

    student_id = data.get("studentId", "unknown")
    task_id    = data.get("taskId",    "none")

    # ── 2. Model health check ─────────────────────────
    if not is_model_ready():
        # Model is still warming up (first request after server start).
        # Return a neutral result so the frontend doesn't stall.
        logger.info("Model not ready yet — returning neutral for student %s", student_id)
        return jsonify({
            "dominant":      "neutral",
            "confidence":    0.0,
            "look_away":     False,
            "rawScores":     {"happy":0.0,"frustrated":0.0,"neutral":0.0,"sad":0.0,"surprised":0.0},
            "processing_ms": 0,
            "model":         get_model_name(),
            "status":        "warming_up",
        }), 200

    # ── 3. Analyse frame ──────────────────────────────
    logger.debug("/emotion  student=%s  task=%s  frame_len=%d",
                 student_id, task_id, len(frame_data))

    result = analyse_frame(frame_data)

    # ── 4. Build response ─────────────────────────────
    response = {
        **result,
        "model":      get_model_name(),
        "studentId":  student_id,
        "taskId":     task_id,
    }

    # ── 5. Sync with Supabase (Background or Async would be better) ──
    from services.supabase_service import save_session_data
    # We'll assume the frontend sends a valid child_id in 'studentId'
    # For now, we only update if it's a real session (not warming up)
    if student_id != "unknown":
        # We don't have the full session stats here easily without more state,
        # but we can at least log that the student is active.
        # This is a bit simplified; a better way would be a dedicated /sync endpoint.
        pass

    return jsonify(response), 200


@emotion_bp.route("/emotion/status", methods=["GET"])
def emotion_status():
    """Health check — lets the frontend know if DeepFace is ready."""
    return jsonify({
        "ready":  is_model_ready(),
        "model":  get_model_name(),
    }), 200