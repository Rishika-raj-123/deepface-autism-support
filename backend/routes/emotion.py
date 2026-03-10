from flask import Blueprint, request, jsonify

from utils.frame_decoder import decode_frame
from services.emotion_service import analyze_emotion

emotion_bp = Blueprint("emotion", __name__)


@emotion_bp.route("/emotion", methods=["POST"])
def detect_emotion():

    data = request.json

    if not data or "image" not in data:
        return jsonify({"error": "No image received"}), 400

    try:
        frame = decode_frame(data["image"])

        result = analyze_emotion(frame)

        return jsonify({
            "dominant": result["dominant_emotion"],
            "confidence": result["emotion"][result["dominant_emotion"]],
            "scores": result["emotion"]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500