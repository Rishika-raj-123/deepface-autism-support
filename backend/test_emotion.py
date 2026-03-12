"""
test_emotion.py — Quick integration test for /emotion endpoint
Run AFTER starting the server with: python app.py

Usage:
    python test_emotion.py                     # uses webcam frame
    python test_emotion.py --image face.jpg    # uses a file
    python test_emotion.py --test-look-away    # test frustration threshold
"""
import argparse
import base64
import json
import sys
import time
import urllib.request
import urllib.error

BASE_URL = "http://localhost:5000"


def b64_from_file(path: str) -> str:
    with open(path, "rb") as f:
        raw = f.read()
    return "data:image/jpeg;base64," + base64.b64encode(raw).decode()


def b64_black_frame() -> str:
    """Generate a tiny black JPEG as a no-face test frame."""
    import numpy as np
    import cv2
    img = np.zeros((240, 320, 3), dtype=np.uint8)
    _, buf = cv2.imencode(".jpg", img)
    return "data:image/jpeg;base64," + base64.b64encode(buf.tobytes()).decode()


def b64_frustrated_face() -> str:
    """Generate a test frame that should trigger frustration (red tint)."""
    import numpy as np
    import cv2
    # Red-tinted image might be interpreted as angry/frustrated
    img = np.zeros((240, 320, 3), dtype=np.uint8)
    img[:, :, 2] = 255  # Make it red (BGR format)
    _, buf = cv2.imencode(".jpg", img)
    return "data:image/jpeg;base64," + base64.b64encode(buf.tobytes()).decode()


def post_json(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode()
    req  = urllib.request.Request(
        url,
        data    = data,
        headers = {"Content-Type": "application/json"},
        method  = "POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def test_look_away_threshold():
    """Test that frustration threshold triggers look_away."""
    print("\n── Testing look_away threshold ───────────────────────────")
    frame = b64_frustrated_face()
    payload = {
        "frame":     frame,
        "studentId": "test-student",
        "taskId":    "test-look-away",
    }
    
    try:
        result = post_json(f"{BASE_URL}/emotion", payload)
        print(f"   Frustration score: {result['rawScores'].get('frustrated', 0):.3f}")
        print(f"   Look away: {result['look_away']}")
        return result
    except Exception as e:
        print(f"   ✗ Request failed: {e}")
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", help="Path to a JPEG image to analyse", default=None)
    parser.add_argument("--test-look-away", action="store_true", 
                       help="Test frustration threshold triggering")
    args = parser.parse_args()

    # ── Health check ─────────────────────────────────
    print("\n── 1. Health probe ──────────────────────────────────────")
    try:
        with urllib.request.urlopen(f"{BASE_URL}/health", timeout=5) as r:
            health = json.loads(r.read())
            print(json.dumps(health, indent=2))
    except urllib.error.URLError as e:
        print(f"  ✗ Server not reachable: {e}")
        print("  → Start the server first: python app.py")
        sys.exit(1)

    # ── Wait for model to warm up ─────────────────────
    print("\n── 2. Waiting for DeepFace model to warm up …")
    for attempt in range(30):
        with urllib.request.urlopen(f"{BASE_URL}/emotion/status", timeout=5) as r:
            status = json.loads(r.read())
        if status.get("ready"):
            print(f"   ✓ Model ready ({attempt+1} poll(s))")
            break
        print(f"   … warming up ({attempt+1}/30)")
        time.sleep(2)
    else:
        print("   ✗ Model did not warm up in 60s — check logs")
        sys.exit(1)

    # ── Test look away if requested ───────────────────
    if args.test_look_away:
        result = test_look_away_threshold()
        if result:
            print("\n── Look away test complete ─────────────────────────────")
        return

    # ── Analyse a frame ───────────────────────────────
    print("\n── 3. Analysing frame ───────────────────────────────────")
    if args.image:
        print(f"   Using image: {args.image}")
        frame = b64_from_file(args.image)
    else:
        print("   Using black test frame (no face expected)")
        frame = b64_black_frame()

    payload = {
        "frame":     frame,
        "studentId": "test-student",
        "taskId":    "test-task",
    }

    t0 = time.time()
    try:
        result = post_json(f"{BASE_URL}/emotion", payload)
        elapsed = round((time.time() - t0) * 1000)
        print(f"\n   Response ({elapsed}ms):")
        print(json.dumps(result, indent=4))
    except Exception as e:
        print(f"   ✗ Request failed: {e}")
        sys.exit(1)

    # ── Assertions ────────────────────────────────────
    print("\n── 4. Assertions ────────────────────────────────────────")
    assert "dominant"   in result, "Missing 'dominant'"
    assert "rawScores"  in result, "Missing 'rawScores'"
    assert "look_away"  in result, "Missing 'look_away'"
    assert "confidence" in result, "Missing 'confidence'"
    assert result["dominant"] in {"happy","frustrated","neutral","sad","surprised"}
    scores = result["rawScores"]
    assert set(scores.keys()) == {"happy","frustrated","neutral","sad","surprised"}
    total = sum(scores.values())
    assert abs(total - 1.0) < 0.02 or total == 0.0, f"Scores should sum to ~1.0, got {total:.3f}"
    print("   ✓ All assertions passed")

    print("\n── Done ─────────────────────────────────────────────────\n")


if __name__ == "__main__":
    main()