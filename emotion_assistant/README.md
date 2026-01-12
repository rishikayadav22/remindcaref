Emotion-Aware AI Assistant - Starter project
--------------------------------------------
This is a starter Django project including:
- Patient CRUD, camera capture, emotion snapshot saving
- Prescription upload + OCR (pytesseract)
- Voice assistant (Web Speech API front-end + Django endpoint)
- Channels skeleton for WebRTC signaling
- Gemini client stub, Celery placeholder, and basic settings

To run locally:
1. Create venv and install requirements.txt
2. Install Tesseract OCR on your system
3. python manage.py migrate
4. python manage.py runserver
