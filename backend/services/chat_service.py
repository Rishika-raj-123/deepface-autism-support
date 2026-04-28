import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

def generate_response(message: str, emotion: str) -> str:
    try:
        message_lower = message.lower()

        # 🧠 Basic intent detection FIRST (important)
        if any(word in message_lower for word in ["hello", "hi", "hey"]):
            return "Hey! 😊 What are you working on today?"

        if "help" in message_lower:
            return "Sure! Tell me what you're stuck on."

        # 🧠 Emotion-aware logic (only when relevant)
        if emotion == "frustrated":
            if any(word in message_lower for word in ["tired", "stress", "hard", "can't", "difficult"]):
                return "It seems a bit tough right now. Want to take a short break or try together?"

            return "I'm here with you. Want help with the task?"

        if emotion == "sad":
            return "Hey, it's okay to feel this way. I'm here with you 💛"

        if emotion == "happy":
            return "Nice! 😊 Keep going, you're doing great!"

        # 🧠 Default fallback (normal conversation)
        return "Got it. Tell me more."

    except Exception as e:
        print("Chat error:", e)
        return "I'm here for you."