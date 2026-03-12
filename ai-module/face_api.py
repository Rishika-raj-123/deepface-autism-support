from flask import Flask, request, jsonify
from flask_cors import CORS
from deepface import DeepFace
import cv2
import numpy as np
import base64
import gc

app = Flask(__name__)
CORS(app)

@app.route('/analyze-frame', methods=['POST'])
def analyze_frame():
    try:
        data = request.json['image']
        data = data.split(',')[1]
        img_data = base64.b64decode(data)
        nparr = np.frombuffer(img_data, np.uint8)
        
        # This decodes the image EXACTLY like cv2.imread does in your script
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # 1. REMOVE RESIZING: We send the full image to keep the quality high
        # 2. MATCH SCRIPT SETTINGS: Use the default DeepFace logic
        results = DeepFace.analyze(
            img_path=frame, 
            actions=['emotion'], 
            enforce_detection=False,
            detector_backend='opencv' # This is what your script uses
        )
        
        res = results[0]
        # We take the raw dominant emotion without any extra filters
        emotion_label = res['dominant_emotion']

        return jsonify({"emotion": emotion_label})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True, use_reloader=False)