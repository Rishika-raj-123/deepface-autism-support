import base64
import cv2
import numpy as np


def decode_frame(data_url):
    """
    Convert base64 image (from browser) into OpenCV image
    """

    # Remove header
    header, encoded = data_url.split(",", 1)

    # Decode base64 string
    img_bytes = base64.b64decode(encoded)

    # Convert bytes to numpy array
    np_arr = np.frombuffer(img_bytes, np.uint8)

    # Decode into OpenCV image
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    return frame