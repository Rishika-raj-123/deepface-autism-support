@echo off
echo ============================================
echo    CalmPath Backend — Windows Setup
echo ============================================
echo.

echo Step 1: Upgrading pip...
python -m pip install --upgrade pip

echo Step 2: Installing packages (this takes 2-5 minutes)...
pip install -r requirements.txt

echo Step 3: Downloading spaCy English model...
python -m spacy download en_core_web_sm

echo Step 4: Creating .env file...
echo FLASK_DEBUG=true > .env
echo FLASK_HOST=0.0.0.0 >> .env
echo FLASK_PORT=5000 >> .env
echo SECRET_KEY=calmpath-dev-secret-change-in-prod >> .env
echo DEEPFACE_MODEL=VGG-Face >> .env
echo DEEPFACE_DETECTOR=opencv >> .env
echo FRUSTRATION_THRESHOLD=0.72 >> .env
echo SUPABASE_URL=your-project-url.supabase.co >> .env
echo SUPABASE_KEY=your-anon-key >> .env

echo Step 5: Pre-warming DeepFace model (downloads ~550MB first time)...
python -c "from services.emotion_service import _ensure_model; _ensure_model()"

echo.
echo ============================================
echo    Setup complete!
echo.
echo    Run: python app.py
echo    Test: python test_emotion.py
echo ============================================
pause