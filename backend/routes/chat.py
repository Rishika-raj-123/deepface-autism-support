from flask import Blueprint, request, jsonify, make_response
from services.chat_service import generate_response

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    # Handle CORS preflight
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return response

    data = request.get_json()

    message = data.get("message", "")
    emotion = data.get("emotion", "neutral")

    if not message:
        return jsonify({"error": "Message required"}), 400

    reply = generate_response(message, emotion)

    return jsonify({"reply": reply}), 200