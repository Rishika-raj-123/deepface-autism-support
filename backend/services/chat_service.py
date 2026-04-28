try:
    import google.generativeai as genai
    import os
    if os.getenv("GEMINI_API_KEY"):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-1.5-flash")
    else:
        model = None
except ImportError:
    model = None

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

        if model:
            prompt = f"You are a supportive AI companion for an autistic child. The child says: '{message}'. Their current emotion is {emotion}. Give a short, encouraging, and sensory-safe response."
            response = model.generate_content(prompt)
            return response.text

        # 🧠 Default fallback (normal conversation)
        return "Got it. Tell me more."

    except Exception as e:
        print("Chat error:", e)
        return "I'm here for you."