import cv2
from deepface import DeepFace
import logging

# Stop the terminal from being messy
logging.getLogger("tensorflow").setLevel(logging.ERROR)

# 1. Open the Webcam
cap = cv2.VideoCapture(0)

print("Starting Camera... Press 'q' to stop!")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    try:
        # 2. Analyze the face
        # We look at 'emotion' specifically
        results = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        res = results[0]
        
        # 3. GET THE RAW DATA
        # Instead of just taking the top emotion, we look at all the "feelings" scores
        all_emotions = res['emotion']
        dominant = res['dominant_emotion']

        # 4. THE "SAD VS ANGRY" FIX
        # If the AI thinks you are 'angry' but you also have a high 'sad' score,
        # we tell it to prioritize 'sad'. This is common for neutral/sad resting faces.
        if dominant == 'angry' and all_emotions['sad'] > 15:
            emotion_label = "sad"
        else:
            emotion_label = dominant

        # 5. Get the box coordinates
        x, y, w, h = res['region']['x'], res['region']['y'], res['region']['w'], res['region']['h']

        # 6. Draw the UI
        # We use BLUE for Sad/Neutral and GREEN for Joy/Surprise
        color = (255, 0, 0) if emotion_label in ['sad', 'angry'] else (0, 255, 0)
        
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        cv2.putText(frame, f"Emotion: {emotion_label.upper()}", (x, y - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    except Exception:
        pass

    # 7. Show the window
    cv2.imshow('Autism Learning Platform - AI Vision', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()