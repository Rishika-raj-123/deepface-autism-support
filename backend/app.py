"""
app.py — CalmPath Flask Backend
================================
Endpoints registered:
  POST /emotion          ← DeepFace webcam analysis
  GET  /emotion/status   ← model warm-up status
  GET  /health           ← basic liveness probe

Run:
  python app.py                    (dev, hot-reload)
  gunicorn app:app -b 0.0.0.0:5000 (prod)

First-time setup:
  pip install -r requirements.txt
  python -m spacy download en_core_web_sm
"""
import logging
import threading
from flask import Flask, jsonify
from flask_cors import CORS

import config
from routes.emotion import emotion_bp
from routes.chat import chat_bp

# ── Logging ────────────────────────────────────────────
logging.basicConfig(
    level   = logging.DEBUG if config.DEBUG else logging.INFO,
    format  = "%(asctime)s  %(levelname)-7s  %(name)s — %(message)s",
    datefmt = "%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── App factory ────────────────────────────────────────
def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["JSON_SORT_KEYS"] = False

    # Allow requests from the frontend (file://, localhost, etc.)
    CORS(app, origins=config.CORS_ORIGINS, supports_credentials=True)

    # ── Register blueprints ───────────────────────────
    app.register_blueprint(emotion_bp)
    app.register_blueprint(chat_bp)

    # ── Health probe ──────────────────────────────────
    @app.route("/health", methods=["GET"])
    def health():
        from services.emotion_service import is_model_ready, get_model_name
        return jsonify({
            "status":      "ok",
            "model_ready": is_model_ready(),
            "model":       get_model_name(),
        }), 200

    # ── Warm up DeepFace in background so first request is fast ──
    def _warmup():
        logger.info("Pre-warming DeepFace model in background thread …")
        from services.emotion_service import _ensure_model
        _ensure_model()

    threading.Thread(target=_warmup, daemon=True, name="deepface-warmup").start()

    return app


app = create_app()

if __name__ == "__main__":
    logger.info("Starting CalmPath backend on %s:%d (debug=%s)",
                config.HOST, config.PORT, config.DEBUG)
    app.run(
        host    = config.HOST,
        port    = config.PORT,
        debug   = config.DEBUG,
        use_reloader = False,   # reloader would double-load DeepFace weights
        threaded = True,
    )