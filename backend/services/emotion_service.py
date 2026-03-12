"""
services/emotion_service.py
Wraps DeepFace with:
  - Singleton model loading (warm-up on first call, ~8s)
  - Thread-safe analysis via a lock
  - Graceful fallback when no face is detected
  - Performance logging
"""
import threading
import time
import logging
from typing import Optional

import numpy as np

from config import DEEPFACE_MODEL, DEEPFACE_DETECTOR, DEEPFACE_ENFORCE
from utils.frame_decoder import decode_frame
from utils.emotion_mapper import map_emotions, safe_emotion_response

logger = logging.getLogger(__name__)

# ── Module-level state ─────────────────────────────────
_lock        = threading.Lock()
_model_ready = False
_deepface    = None          # imported lazily to avoid slow startup


def _ensure_model() -> None:
    """
    Import DeepFace and run a tiny warm-up frame the first time.
    Subsequent calls return immediately.
    """
    global _deepface, _model_ready
    if _model_ready:
        return

    with _lock:
        if _model_ready:   # double-checked inside lock
            return

        logger.info("Loading DeepFace model '%s' …", DEEPFACE_MODEL)
        t0 = time.time()

        # Lazy import — avoids 3-4s import time on every restart
        from deepface import DeepFace as _df
        _deepface = _df

        # Warm-up: analyse a black 48×48 frame so the model weights are
        # loaded into GPU/CPU memory before the first real request arrives.
        try:
            dummy = np.zeros((48, 48, 3), dtype=np.uint8)
            _deepface.analyze(
                img_path           = dummy,
                actions            = ["emotion"],
                detector_backend   = DEEPFACE_DETECTOR,
                enforce_detection  = False,
                silent             = True,
            )
        except Exception:
            pass   # warm-up failure is non-fatal

        _model_ready = True
        logger.info("DeepFace ready in %.1fs", time.time() - t0)


# ── Public API ─────────────────────────────────────────

def analyse_frame(frame_data: str) -> dict:
    """
    Accept a base64 data-URL from the browser canvas.
    Returns the mapped emotion dict (see emotion_mapper.map_emotions).

    On any error returns a safe neutral response so the frontend
    doesn't crash.
    """
    # Decode base64 → numpy BGR array
    try:
        img_bgr = decode_frame(frame_data)
    except ValueError as e:
        logger.warning("Frame decode error: %s", e)
        return safe_emotion_response("decode_error")

    # Ensure model is loaded (no-op after first call)
    _ensure_model()

    t0 = time.time()
    try:
        with _lock:
            results = _deepface.analyze(
                img_path          = img_bgr,
                actions           = ["emotion"],
                detector_backend  = DEEPFACE_DETECTOR,
                enforce_detection = DEEPFACE_ENFORCE,
                silent            = True,
            )
    except Exception as e:
        err_str = str(e).lower()
        if "face" in err_str or "detector" in err_str or "detection" in err_str:
            # No face found in frame — student looked away
            logger.debug("No face detected: %s", e)
            return safe_emotion_response("no_face")
        logger.error("DeepFace analysis error: %s", e)
        return safe_emotion_response("analysis_error")

    elapsed_ms = round((time.time() - t0) * 1000)
    logger.debug("DeepFace analysis: %dms", elapsed_ms)

    # DeepFace returns a list when detecting multiple faces; take first
    result = results[0] if isinstance(results, list) else results
    mapped = map_emotions(result)
    mapped["processing_ms"] = elapsed_ms
    return mapped


def is_model_ready() -> bool:
    return _model_ready


def get_model_name() -> str:
    return DEEPFACE_MODEL