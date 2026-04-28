# Simple CalmPath Setup Script
Write-Host "============================================" 
Write-Host "   CalmPath Backend — Windows Setup         "
Write-Host "============================================"
Write-Host ""

# 1. Upgrade pip
Write-Host "Step 1: Upgrading pip ..."
python -m pip install --upgrade pip

# 2. Install requirements
Write-Host "Step 2: Installing packages (this takes 2-5 minutes) ..."
pip install -r requirements.txt

# 3. Download spaCy model
Write-Host "Step 3: Downloading spaCy English model ..."
python -m spacy download en_core_web_sm

# 4. Create .env file
Write-Host "Step 4: Creating .env file ..."
$content = @"
FLASK_DEBUG=true
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
SECRET_KEY=calmpath-dev-secret-change-in-prod
DEEPFACE_MODEL=VGG-Face
DEEPFACE_DETECTOR=opencv
FRUSTRATION_THRESHOLD=0.72
SUPABASE_URL=your-project-url.supabase.co
SUPABASE_KEY=your-anon-key
"@
$content | Out-File -FilePath .env -Encoding utf8

# 5. Pre-warm DeepFace
Write-Host "Step 5: Pre-warming DeepFace model (downloads ~550MB first time) ..."
python -c "from services.emotion_service import _ensure_model; _ensure_model()"

Write-Host ""
Write-Host "============================================"
Write-Host "   Setup complete!                          "
Write-Host ""
Write-Host "   Run: python app.py"
Write-Host "   Test: python test_emotion.py"
Write-Host "============================================"

# Pause so you can see the result
Read-Host "Press Enter to exit"