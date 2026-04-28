from flask import Blueprint, request, jsonify
from services.chat_service import generate_response

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    message = data.get("message", "")
    emotion = data.get("emotion", "neutral")

    if not message:
        return jsonify({"error": "Message required"}), 400

    reply = generate_response(message, emotion)

    return jsonify({"reply": reply}), 200