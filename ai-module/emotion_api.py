from flask import Flask, request, jsonify
import base64
import numpy as np
import cv2

from face_detect import detect_emotion

app = Flask(__name__)

@app.route('/detect', methods=['POST'])
def detect():

    data = request.json['image']

    image_data = data.split(",")[1]

    image_bytes = base64.b64decode(image_data)

    np_arr = np.frombuffer(image_bytes, np.uint8)

    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    emotion, confidence = detect_emotion(frame)

    return jsonify({
        "emotion": emotion,
        "confidence": float(confidence)
    })

if __name__ == "__main__":
    app.run(port=5000)