"""
utils/frame_decoder.py
Decodes a base64-encoded image string (from canvas.toDataURL)
into an OpenCV-compatible numpy array (BGR, uint8).
"""
import base64
import re
import numpy as np
import cv2

# Optional: Add max size constant
MAX_IMAGE_SIZE = 1024 * 768 * 3  # ~2.3MB for 1024x768 RGB

def decode_frame(data_url: str) -> np.ndarray:
    """
    Accept either:
      - Raw base64 string
      - Data URL:  data:image/jpeg;base64,/9j/4AAQ...
    Returns BGR numpy array (H, W, 3) ready for DeepFace.
    Raises ValueError if decoding fails.
    """
    if not data_url:
        raise ValueError("Empty frame data")

    # Strip the data-URL prefix if present
    if data_url.startswith("data:"):
        match = re.match(r"data:[^;]+;base64,(.+)", data_url, re.DOTALL)
        if not match:
            raise ValueError("Malformed data URL")
        b64_str = match.group(1)
    else:
        b64_str = data_url

    # Remove any whitespace/newlines that may have crept in
    b64_str = b64_str.strip().replace("\n", "").replace(" ", "")

    # Pad to multiple of 4
    padding = len(b64_str) % 4
    if padding:
        b64_str += "=" * (4 - padding)

    try:
        raw_bytes = base64.b64decode(b64_str)
    except Exception as e:
        raise ValueError(f"Base64 decode failed: {e}")

    # Optional: Check decoded size
    if len(raw_bytes) > MAX_IMAGE_SIZE:
        raise ValueError(f"Decoded image too large: {len(raw_bytes)} bytes")

    img_array = np.frombuffer(raw_bytes, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("cv2.imdecode returned None — invalid image bytes")

    return img  # BGR uint8