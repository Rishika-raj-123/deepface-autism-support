import sys
print(f"Python Version: {sys.version}")

libs = ['flask', 'flask_cors', 'requests', 'dotenv', 'google.generativeai', 'spacy', 'deepface', 'cv2', 'tensorflow']

for lib in libs:
    try:
        __import__(lib)
        print(f"[OK] {lib} is installed")
    except ImportError as e:
        print(f"[MISSING] {lib} is missing: {e}")
    except Exception as e:
        print(f"[ERROR] {lib} error: {e}")

try:
    import spacy
    # Check if model is available
    import subprocess
    res = subprocess.run([sys.executable, "-m", "spacy", "info", "en_core_web_sm"], capture_output=True)
    if res.returncode == 0:
        print("[OK] spacy model is loaded")
    else:
        print("[MISSING] spacy model 'en_core_web_sm' is missing. Downloading...")
        subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
except Exception as e:
    print(f"[ERROR] spacy check error: {e}")
