"""
utils/emotion_mapper.py
Maps DeepFace's raw 7-emotion output to the 5 student-safe labels
used throughout CalmPath, and computes a look_away signal.
"""
from config import EMOTION_MAP, FRUSTRATION_THRESHOLD


def map_emotions(deepface_result: dict) -> dict:
    """
    Input: single DeepFace analysis result dict, e.g.:
        {
          "dominant_emotion": "angry",
          "emotion": {
              "angry": 73.2, "disgust": 1.1, "fear": 5.0,
              "happy": 2.3,  "sad": 8.4,    "surprise": 0.9,
              "neutral": 9.1
          }
        }

    Output:
        {
          "dominant": "frustrated",      # mapped label
          "confidence": 0.73,            # 0–1 fraction
          "look_away": False,
          "rawScores": {
              "happy": 0.02, "frustrated": 0.79, "neutral": 0.09,
              "sad": 0.08,   "surprised": 0.01
          }
        }
    """
    # Validate input
    if not isinstance(deepface_result, dict):
        return safe_emotion_response("invalid_input")
    
    raw_7  = deepface_result.get("emotion", {})
    if not raw_7:
        return safe_emotion_response("no_emotion_data")
    
    dominant_7 = deepface_result.get("dominant_emotion", "neutral")

    # Convert percentages → 0-1 fractions
    raw_fractions = {k: round(v / 100.0, 4) for k, v in raw_7.items()}

    # Bucket into our 5 labels by summing mapped values
    mapped_scores: dict[str, float] = {
        "happy":      0.0,
        "frustrated": 0.0,
        "neutral":    0.0,
        "sad":        0.0,
        "surprised":  0.0,
    }
    for deepface_label, fraction in raw_fractions.items():
        our_label = EMOTION_MAP.get(deepface_label, "neutral")
        mapped_scores[our_label] = round(
            mapped_scores[our_label] + fraction, 4
        )

    # Dominant mapped label
    dominant_mapped = EMOTION_MAP.get(dominant_7, "neutral")
    confidence      = round(mapped_scores.get(dominant_mapped, 0.0), 4)

    # look_away is True when frustration is very high — indicates need for break
    look_away = mapped_scores.get("frustrated", 0.0) >= FRUSTRATION_THRESHOLD

    return {
        "dominant":   dominant_mapped,
        "confidence": confidence,
        "look_away":  look_away,
        "rawScores":  mapped_scores,
    }


def safe_emotion_response(reason: str = "no_face") -> dict:
    """
    Returns a neutral result when DeepFace can't find a face.
    look_away=True tells the student page to start the grace period.
    """
    return {
        "dominant":   "neutral",
        "confidence": 0.0,
        "look_away":  True,   # face not visible → trigger grace period
        "rawScores": {
            "happy": 0.0, "frustrated": 0.0,
            "neutral": 0.0, "sad": 0.0, "surprised": 0.0,
        },
        "reason": reason,
    }