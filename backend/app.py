from flask import Flask, jsonify
from flask_cors import CORS
from routes.emotion import emotion_bp

app = Flask(__name__)

CORS(app)

# register emotion API
app.register_blueprint(emotion_bp)


@app.route("/")
def home():
    return "Backend is running"


@app.route("/health")
def health():
    return jsonify({"status": "server running"})


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )