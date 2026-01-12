import base64, uuid, os, json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import random
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from .models import Patient, Snapshot, Prescription
from .forms import PatientForm, PrescriptionForm
from .helpers.ocr_utils import image_to_text, parse_meds

from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from .models import Reminder, Patient
from .forms import ReminderForm


from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


# Dashboard
def dashboard(request, patient_id=None):
    patients = Patient.objects.all().order_by('first_name')
    patient = None
    if patient_id:
        patient = get_object_or_404(Patient, pk=patient_id)
    return render(request, 'dashboard.html', {'patients': patients, 'patient': patient})

def patient_create(request):
    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES)
        if form.is_valid():
            p = form.save()
            return redirect('dashboard', patient_id=p.id)
    else:
        form = PatientForm()
    return render(request, 'patient_form.html', {'form': form})



@csrf_exempt
@login_required
def analyze_emotion(request, patient_id):
    try:
        patient = get_object_or_404(Patient, id=patient_id, user=request.user)
        data = request.POST.get("image")

        if not data:
            return JsonResponse({"error": "No image"}, status=400)

        header, encoded = data.split(",", 1)
        decoded = base64.b64decode(encoded)

        filename = f"{uuid.uuid4().hex}.jpg"
        snapshot = Snapshot.objects.create(
            patient=patient,
            detected_emotion="neutral"
        )
        snapshot.image.save(filename, decoded)

        return JsonResponse({"emotion": "neutral"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def upload_prescription(request, patient_id):

    patient = get_object_or_404(Patient, id=patient_id, user=request.user)
    if request.method == 'POST':
        form = PrescriptionForm(request.POST, request.FILES)
        if form.is_valid():
            pres = form.save(commit=False)
            pres.patient = patient
            pres.save()
            # OCR
            try:
                path = pres.file.path
                text = image_to_text(path)
                pres.ocr_text = text
                pres.parsed_meds = parse_meds(text)
                pres.save()
            except Exception as e:
                pres.raw_parse_errors = str(e)
                pres.save()
            return redirect('prescription_detail', pres.id)
    else:
        form = PrescriptionForm()
    return render(request, 'upload_prescription.html', {'form': form, 'patient': patient})

@login_required
def prescription_detail(request, pres_id):
    prescription = get_object_or_404(Prescription, id=pres_id)
    return render(request, 'prescription_detail.html', {'prescription': prescription})

@csrf_exempt
def voice_assistant(request):
    if request.method == 'POST':
        text = request.POST.get('text','').strip()
        if not text:
            return JsonResponse({'error':'No speech'}, status=400)
        # placeholder reply - replace with Gemini in future
        if 'sad' in text.lower():
            reply = "I hear you're feeling sad. Would you like a calming exercise?"
        elif 'angry' in text.lower():
            reply = "I understand. Let's take deep breaths together."
        else:
            reply = "Thanks for sharing. I'm here to support you."
        return JsonResponse({'reply': reply})
    return JsonResponse({'error':'Invalid method'}, status=405)

import re
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
# from .gemini_client import generate_reply
from .models import ChatMessage, Patient

# Basic self-harm / emergency detection (simple keywords). Improve with better classifier.
EMERGENCY_KEYWORDS = [
    'kill myself', 'i want to die', 'i am going to kill myself', 'end my life',
    'hurt myself', 'suicide', 'want to die', 'i will die'
]

def contains_emergency(text: str) -> bool:
    t = text.lower()
    for kw in EMERGENCY_KEYWORDS:
        if kw in t:
            return True
    return False


@login_required
def add_reminder(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id, user=request.user)
    if request.method == "POST":
        form = ReminderForm(request.POST)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.user = request.user
            reminder.save()
            return redirect("dashboard", patient_id=patient.id)
    else:
        form = ReminderForm()
    return render(request, "add_reminder.html", {"form": form, "patient": patient})

@login_required
def reminders_json(request):
    reminders = Reminder.objects.filter(
        user=request.user,
        completed=False,
        reminder_time__lte=now()
    ).values('id', 'message', 'reminder_time')
    return JsonResponse(list(reminders), safe=False)

@csrf_exempt
@login_required
def mark_reminder_seen(request, pk):
    # if request.method == "POST":
    Reminder.objects.filter(id=pk, user=request.user).update(completed=True)
    return JsonResponse({"status": "ok"})
    # return JsonResponse({"status": "invalid"}, status=400)



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import google.generativeai as genai

# # ✅ Configure your API key (set this properly in settings or env)
genai.configure(api_key="GEMINI_API_KEY")

from openai import OpenAI

client = OpenAI(api_key="OPEB_API_KEY")


@csrf_exempt  # You can remove this if using CSRF tokens instead
def chatbot_reply(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            user_message = data.get("message", "")

            if not user_message:
                return JsonResponse({"reply": "Please type something."})

            try:
                model = genai.GenerativeModel("gemini-2.0-flash")
                response = model.generate_content(user_message)
                bot_reply = response.text if hasattr(response, "text") else str(response)
            except Exception as e:
                bot_reply = f"⚠️ Error communicating with chatbot: {str(e)}"

            return JsonResponse({"reply": bot_reply})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)

from django.shortcuts import render

@login_required
def chat_page(request):
    return render(request, "chat_page.html")
@login_required
def therapy_session(request):
    return render(request, "therapy_session.html")
@login_required
def remember_sequence(request):
    """
    Renders the Remember the Sequence game.
    Optionally accepts ?patient_id= to personalize (show name/photo).
    """
    patient = None
    pid = request.GET.get('patient_id')
    if pid:
        try:
            patient = Patient.objects.get(pk=int(pid))
        except Patient.DoesNotExist:
            patient = None

    return render(request, 'remember_sequence.html', {'patient': patient})


@csrf_exempt
@login_required
def remember_sequence_score(request):
    """
    Optional endpoint to save or receive JSON score data.
    Example POST: {"score": 5, "level": 3, "patient_id": 12}
    Right now it just stores in session and returns acknowledgement.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'invalid json'}, status=400)

    score = data.get('score')
    level = data.get('level')
    pid = data.get('patient_id')
    # store in session keyed by patient id or overall
    sess_key = 'sequence_scores'
    seq_scores = request.session.get(sess_key, {})
    seq_scores[str(pid or 'anon')] = {'score': score, 'level': level}
    request.session[sess_key] = seq_scores

    return JsonResponse({'saved': True, 'score': seq_scores[str(pid or 'anon')]})


from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )
        if user:
            login(request, user)
            return redirect("dashboard")
        else:
            return render(request, "auth/login.html", {
                "error": "Invalid username or password"
            })

    return render(request, "auth/login.html")




# @login_required
def dashboard_redirect(request):
    if request.user.is_staff:
        return redirect("admin_dashboard")
    return redirect("user_dashboard")

@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


from .models import DailyRoutine

@login_required
def user_dashboard(request):
    patient = Patient.objects.filter(user=request.user).first()

    routines = DailyRoutine.objects.filter(
        patient=patient
    ).order_by("time")

    return render(request, "dashboard/user_dashboard.html", {
        "patient": patient,
        "routines": routines
    })

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from django.views.decorators.http import require_POST
from django.http import JsonResponse
# from .models import Routine

@require_POST
@login_required
def mark_routine_done(request, routine_id=None, pk=None):
    rid = routine_id or pk
    routine = get_object_or_404(DailyRoutine, id=rid, user=request.user)
    routine.completed = True
    routine.save()
    return JsonResponse({"status": "ok"})





from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import UserProgress
@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect("user_dashboard")

    progress = UserProgress.objects.select_related("user")
    return render(request, "dashboard/admin_dashboard.html", {
        "progress": progress
    })


from django.shortcuts import get_object_or_404
from .models import Patient

@login_required
def patient_dashboard(request, patient_id):
    
    patient = get_object_or_404(Patient, id=patient_id, user=request.user)

    return render(request, "dashboard/patient_dashboard.html", {
        "patient": patient
    })

@login_required
def patient_create(request):
    if request.method == "POST":
        form = PatientForm(request.POST, request.FILES)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.user = request.user
            patient.save()
            return redirect("patient_dashboard", patient_id=patient.id)
    else:
        form = PatientForm()

    return render(request, "patient_form.html", {"form": form})

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from .forms import UserRegistrationForm
from .models import Patient


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"]
            )

            # Create empty patient profile
            Patient.objects.create(
                user=user,
                first_name="",
                last_name="",
                age=1
            )

            return redirect("login")

    else:
        form = UserRegistrationForm()

    return render(request, "auth/register.html", {"form": form})


from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import login

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if password1 != password2:
            return render(request, "auth/register.html", {
                "error": "Passwords do not match"
            })

        if User.objects.filter(username=username).exists():
            return render(request, "auth/register.html", {
                "error": "Username already exists"
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
        Patient.objects.create(
            user=user,
            first_name="",
            last_name="",
            age=1
        )

        login(request, user)
        return redirect("dashboard")

    return render(request, "auth/register.html")


@login_required
def dashboard(request):
    if request.user.is_staff:
        return redirect("admin_dashboard")
    return redirect("user_dashboard")


import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .helpers.gemini_helper import generate_gemini_reply

@csrf_exempt
@login_required
def chatbot_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body)
        user_message = data.get("message", "").strip()

        if not user_message:
            return JsonResponse({"reply": "Please say something."})

        reply = generate_gemini_reply(user_message)
        return JsonResponse({"reply": reply})

    except Exception:
        return JsonResponse({"error": "Invalid request"}, status=400)
    
@login_required
def chatbot_page(request):
    return render(request, "chatbot.html")

import json
import google.generativeai as genai
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .helpers.gemini_helper import generate_gemini_reply

# Configure SDK if API key available
if getattr(settings, "GEMINI_API_KEY", None):
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
    except Exception:
        pass

@login_required
def chat_page(request):
    return render(request, "chat/chatbot.html")


@csrf_exempt
@login_required
def chatbot_reply(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    data = json.loads(request.body)
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return JsonResponse({"reply": "Please say something."})

    # Safety check
    if contains_emergency(user_message):
        system_msg = (
            "I’m sorry you're feeling that way. If you're thinking about harming yourself, please contact local emergency services or a suicide hotline right now. Would you like me to alert your caretaker?"
        )
        return JsonResponse({"reply": system_msg, "emergency": True})

    try:
        reply_text = generate_gemini_reply(user_message)
        if not reply_text:
            reply_text = "Sorry, I couldn't reach the assistant. Please try again later."
    except Exception:
        reply_text = "Sorry, I couldn't reach the assistant. Please try again later."

    return JsonResponse({"reply": reply_text})






# Chat interface and reply handling consolidated earlier — see the `chatbot_reply` handler above which uses `generate_gemini_reply` (remote when configured) and a safe local fallback.



from .models import DailyRoutine
from .forms import DailyRoutineForm
from django.contrib.auth.decorators import login_required

@login_required
def add_routine(request):
    if request.method == "POST":
        form = DailyRoutineForm(request.POST)
        if form.is_valid():
            routine = form.save(commit=False)
            routine.user = request.user
            routine.save()
            return redirect("user_dashboard")
    else:
        form = DailyRoutineForm()

    return render(request, "dashboard/add_routine.html", {"form": form})


from .models import DailyRoutine
from .forms import DailyRoutineForm
from django.contrib.auth.decorators import login_required

@login_required
def add_routine(request):
    if request.method == "POST":
        form = DailyRoutineForm(request.POST)
        if form.is_valid():
            routine = form.save(commit=False)
            routine.user = request.user
            routine.save()
            return redirect("user_dashboard")
    else:
        form = DailyRoutineForm()

    return render(request, "dashboard/add_routine.html", {"form": form})


@login_required
def user_dashboard(request):
    routines = DailyRoutine.objects.filter(
        user=request.user
    ).order_by("time")

    return render(request, "dashboard/user_dashboard.html", {
        "routines": routines
    })


@login_required
def routine_page(request):
    patient = Patient.objects.filter(user=request.user).first()
    routines = DailyRoutine.objects.filter(
        user_id=request.user.id
    ).order_by("time")

    return render(request, "routine/routine_page.html", {
        "routines": routines
    })



import pytesseract
from PIL import Image
import re
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Medication

# ⚠️ Set Tesseract path (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

@login_required
def medication_page(request):
    extracted_text = ""
    medications = []

    if request.method == "POST" and request.FILES.get("prescription"):
        image = Image.open(request.FILES["prescription"])
        extracted_text = pytesseract.image_to_string(image)

        # VERY BASIC extraction logic
        lines = extracted_text.split("\n")
        for line in lines:
            match = re.search(r"(\w+)\s+(\d+\s?mg)", line, re.I)
            if match:
                medications.append({
                    "name": match.group(1),
                    "dosage": match.group(2),
                    "instruction": "Take as prescribed"
                })

    return render(request, "app/medication.html", {
        "text": extracted_text,
        "medications": medications
    })


from django.contrib.auth.decorators import login_required
from .models import FamilyContact

@login_required
def family_page(request):
    contacts = FamilyContact.objects.filter(user=request.user)
    return render(request, "app/family.html", {
        "contacts": contacts
    })


from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def memory_log(request):
    return render(request, "app/memory.html")


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .models import Reminder

@login_required
def reminders_page(request):
    reminders = Reminder.objects.filter(user=request.user).order_by("reminder_time")
    return render(request, "reminders/reminders.html", {
        "reminders": reminders
    })

from .models import Reminder
from .forms import ReminderForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required

@login_required
def reminder_page(request):
    reminders = Reminder.objects.filter(user=request.user).order_by('reminder_time')

    if request.method == "POST":
        form = ReminderForm(request.POST)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.user = request.user
            # ensure DB 'title' column is set (some DB states still require it)
            reminder.title = (reminder.message or '')[:200]
            reminder.save()
    else:
        form = ReminderForm()

    return render(request, 'reminders/reminders.html', {
        'form': form,
        'reminders': reminders,
        'now': timezone.now()
    })

@login_required
def edit_reminder(request, pk):
    reminder = get_object_or_404(Reminder, pk=pk, user=request.user)
    if request.method == "POST":
        form = ReminderForm(request.POST, instance=reminder)
        if form.is_valid():
            r = form.save(commit=False)
            r.user = request.user
            r.title = (r.message or '')[:200]
            r.save()
            return redirect('reminder_page')
    else:
        form = ReminderForm(instance=reminder)
    return render(request, 'reminders/edit_reminder.html', {
        'form': form,
        'reminder': reminder
    })

@login_required
def delete_reminder(request, pk):
    reminder = get_object_or_404(Reminder, pk=pk, user=request.user)
    if request.method == "POST":
        reminder.delete()
        return redirect('reminder_page')
    return render(request, 'reminders/confirm_delete.html', {'reminder': reminder})
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Routine, RoutineTask


@login_required
def routine_list(request):
    routines = Routine.objects.filter(user=request.user, is_active=True)
    inactive = Routine.objects.filter(user=request.user, is_active=False)

    return render(request, "routines.html", {
        "routines": routines,
        "inactive": inactive
    })

@login_required
def edit_routine(request, id):
    routine = get_object_or_404(Routine, id=id, user=request.user)

    if request.method == "POST":
        routine.name = request.POST["name"]
        routine.save()
        return redirect("routine_page")

    return render(request, "edit_routine.html", {"routine": routine})






from django.shortcuts import render, get_object_or_404
from .models import Routine

def routines_page(request):
    routines = Routine.objects.filter(user=request.user, is_active=True)
    inactive = Routine.objects.filter(user=request.user, is_active=False)

    return render(request, "app/routines.html", {
        "routines": routines,
        "inactive": inactive
    })


def edit_routine(request, pk):
    routine = get_object_or_404(Routine, pk=pk, user=request.user)
    return render(request, "app/edit_routine.html", {"routine": routine})


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import UserProfile, EmergencyContact, FamilyContact

@login_required
def profile_page(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    emergency = EmergencyContact.objects.filter(user=request.user).first()
    family_contacts = list(FamilyContact.objects.filter(user=request.user).order_by('name'))

    return render(request, "app/profile.html", {
        "profile": profile,
        "emergency": emergency,
        "family_contacts": family_contacts
    })


import base64
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def detect_emotion(request):
    import json
    data = json.loads(request.body)

    image_data = data["image"].split(",")[1]
    image_bytes = base64.b64decode(image_data)

    filename = f"emotion_{uuid.uuid4()}.png"
    with open(f"media/emotions/{filename}", "wb") as f:
        f.write(image_bytes)

    # TEMP emotion logic (replace with ML model later)
    emotion = "Neutral"

    return JsonResponse({
        "emotion": emotion,
        "image": filename
    })


def routines_page(request):
    routines = Routine.objects.filter(user=request.user, is_active=True).prefetch_related("tasks")
    return render(request, "app/routines.html", {
        "routines": routines
    })


from django.http import StreamingHttpResponse
from .camera import VideoCamera

camera = VideoCamera()

def gen(camera):
    while True:
        frame, emotion = camera.get_frame()
        if frame is None:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def live_camera(request):
    return StreamingHttpResponse(
        gen(camera),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )

from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def routines(request):
    return render(request, "routine/routines.html")


from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def chatbot(request):
    return render(request, 'chatbot.html')
import google.generativeai as genai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from django.conf import settings
from app.helpers.gemini_helper import generate_gemini_reply
from google.api_core.exceptions import NotFound

# Configure using project settings
genai.configure(api_key=settings.GEMINI_API_KEY)

@csrf_exempt
@login_required
def chatbot_reply(request):
    if request.method == "POST":
        data = json.loads(request.body)
        message = data.get("message") or ""

        # Try using a configured remote model if provided, otherwise fall back to local generator
        model_name = getattr(settings, "GEMINI_MODEL_NAME", None)

        if model_name:
            model = genai.GenerativeModel(model_name)
            try:
                response = model.generate_content(message)
                # response.text is the expected attribute, but handle a couple of possible shapes
                reply_text = getattr(response, "text", None) or (response.get("candidates")[0].get("content") if isinstance(response, dict) and response.get("candidates") else str(response))
            except NotFound:
                # Model not found for this API version — fallback to local generator
                reply_text = generate_gemini_reply(message)
            except Exception:
                # Any other error — keep the user experience stable by using local generator
                reply_text = generate_gemini_reply(message)
        else:
            # No remote model configured — use local generator
            reply_text = generate_gemini_reply(message)

        return JsonResponse({"reply": reply_text})

    return JsonResponse({"error": "Invalid request"}, status=400)


from django.conf import settings
genai.configure(api_key=settings.GEMINI_API_KEY)

import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

@login_required
def chatbot_page(request):
    return render(request, "chatbot.html")


@csrf_exempt
@login_required
def chatbot_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message")

        # TEMP reply (replace with Gemini / OpenAI later)
        reply = f"You said: {user_message}"

        return JsonResponse({"reply": reply})


import google.generativeai as genai
from django.conf import settings

# Configure SDK only if API key present
if getattr(settings, "GEMINI_API_KEY", None):
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
    except Exception:
        pass

# Create a model object only if a model name is configured
model = None
if getattr(settings, "GEMINI_MODEL_NAME", None):
    try:
        model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)
    except Exception:
        model = None


def routine_page(request):
    # Classify routines into morning/evening based on their task times (if available).
    # Routines with morning tasks will appear in the Morning card, routines with
    # evening tasks will appear in the Evening card. If a routine has tasks in
    # both periods it will appear in both cards. Routines without tasks are
    # shown in an "Unscheduled" card.
    routines = list(Routine.objects.filter(user=request.user, is_active=True).prefetch_related('tasks'))

    # Also include older DailyRoutine entries (created via the Add form) so they
    # show up in the Routine list. We convert them to a small object with a
    # tasks list so the same classification logic can operate on them.
    from types import SimpleNamespace
    try:
        daily_routines = DailyRoutine.objects.filter(user=request.user)
    except Exception:
        daily_routines = []

    for dr in daily_routines:
        # Build a small object compatible with Routine used by the template
        pseudo = SimpleNamespace()
        pseudo.name = getattr(dr, 'title', str(dr))
        # Create a single pseudo-task with time and description so classification works
        task_ns = SimpleNamespace()
        task_ns.time = getattr(dr, 'time', None)
        task_ns.description = ''
        pseudo.tasks = [task_ns]
        routines.append(pseudo)

    morning_routines = []
    evening_routines = []
    unscheduled = []

    for r in routines:
        # tasks should be a list-like of objects that have a 'time' attribute
        tasks = list(getattr(r, 'tasks', []))
        if not tasks:
            unscheduled.append(r)
            continue

        # Helper: get hour robustly whether time is a time object or a string
        def _task_hour(t):
            val = getattr(t, 'time', None)
            if val is None:
                return None
            if hasattr(val, 'hour'):
                try:
                    return int(val.hour)
                except Exception:
                    return None
            try:
                s = str(val)
                if ':' in s:
                    parts = s.split(':')
                    return int(parts[0])
            except Exception:
                return None
            return None

        hours = [h for h in (_task_hour(t) for t in tasks) if h is not None]
        if not hours:
            # tasks exist but no parseable times: treat as unscheduled
            unscheduled.append(r)
            continue

        has_morning = any(h < 12 for h in hours)
        has_evening = any(h >= 12 for h in hours)

        if has_morning:
            morning_routines.append(r)
        if has_evening:
            evening_routines.append(r)

    return render(request, "routine/routine_list.html", {
        "morning_routines": morning_routines,
        "evening_routines": evening_routines,
        "unscheduled_routines": unscheduled,
    })


def routine_list(request):
    morning_routines = Routine.objects.filter(routine_type="morning")
    evening_routines = Routine.objects.filter(routine_type="evening")

    context = {
        "morning_routines": morning_routines,
        "evening_routines": evening_routines,
    }
    return render(request, "routine_list.html", context)



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponse
from django.contrib.auth.models import User

from .models import UserProfile, EmergencyContact
@login_required
def profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    emergency = EmergencyContact.objects.filter(user=request.user).first()

    return render(request, 'profile.html', {
        'profile': profile,
        'emergency': emergency
    })
@login_required
def edit_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name')
        request.user.last_name = request.POST.get('last_name')
        profile.phone = request.POST.get('phone')

        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']

        request.user.save()
        profile.save()
        return redirect('profile')

    return render(request, 'edit_profile.html', {
        'profile': profile
    })
@login_required
def add_emergency(request):
    if request.method == 'POST':
        EmergencyContact.objects.create(
            user=request.user,
            name=request.POST['name'],
            relation=request.POST['relation'],
            phone=request.POST['phone']
        )
        return redirect('profile')

    return render(request, 'add_emergency.html')
@login_required
def edit_emergency(request, id):
    emergency = get_object_or_404(EmergencyContact, id=id, user=request.user)

    if request.method == 'POST':
        emergency.name = request.POST['name']
        emergency.relation = request.POST['relation']
        emergency.phone = request.POST['phone']
        emergency.save()
        return redirect('profile')

    return render(request, 'edit_emergency.html', {
        'emergency': emergency
    })
@login_required
def change_playback_speed(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        profile.playback_speed = request.POST.get('speed', 'Normal')
        profile.save()

    return redirect('profile')
@login_required
def toggle_dark_mode(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    profile.dark_mode = not profile.dark_mode
    profile.save()
    return HttpResponse("OK")
@login_required
def change_font_size(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        profile.font_size = request.POST.get('font_size', 'Medium')
        profile.save()

    return redirect('profile')
@login_required
def delete_account(request):
    if request.method == 'POST':
        request.user.delete()
        logout(request)
        return redirect('login')

    return redirect('profile')
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def voice_assistant(request):
    data = json.loads(request.body)
    user_text = data.get("message", "").lower()

    # Simple logic (you can expand later)
    if "routine" in user_text:
        reply = "Here is your daily routine."
    elif "medicine" in user_text:
        reply = "It's time for your medication."
    elif "who am i" in user_text:
        reply = "You are John. You are at home."
    elif "call family" in user_text:
        reply = "Calling your family now."
    else:
        reply = "I am here to help you. Please say a command."

    return JsonResponse({"reply": reply})



import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def voice_assistant(request):
    data = json.loads(request.body)
    user_text = data.get("message", "").lower()

    # 🧠 Daily Assistance
    if "routine" in user_text:
        reply = "Here is your daily routine. Take things slowly and comfortably."

    elif "medicine" in user_text or "medication" in user_text:
        reply = "It is time for your medication. Please take it with water."

    elif "who am i" in user_text:
        reply = "You are John. You are safe at home. I am right here with you."

    elif "call family" in user_text:
        reply = "That sounds like a good idea. I will help you contact your family."

    # 😵 Dizzy / Light-headed
    elif any(word in user_text for word in ["dizzy", "giddy", "light headed", "lightheaded"]):
        reply = (
            "I understand. Please sit down or lie down safely. "
            "Take slow deep breaths. If you can, take a sip of water. "
            "I am here with you."
        )

    # 🧠 Forgetting / Memory loss
    elif any(phrase in user_text for phrase in ["i forget", "i forgot", "forget things", "memory problem"]):
        reply = (
            "That is okay. Forgetting happens sometimes. "
            "You are safe, and I can remind you whenever you need. "
            "Let us take things one step at a time."
        )

    # 😔 Sad / Low emotions
    elif any(word in user_text for word in ["sad", "low", "upset", "unhappy", "depressed"]):
        reply = (
            "I am really sorry you are feeling this way. "
            "You are not alone. Let us take a slow breath together."
        )

    # 😰 Anxiety / Stress
    elif any(word in user_text for word in ["anxious", "anxiety", "stress", "worried", "panic"]):
        reply = (
            "It is okay to feel this way sometimes. "
            "Sit comfortably and breathe slowly. Everything is calm right now."
        )

    # 🧘 Relaxation / Calm
    elif any(word in user_text for word in ["relax", "calm", "peaceful", "rest"]):
        reply = (
            "You are doing well. Close your eyes gently and take three slow breaths."
        )

    # 😊 Happy / Joyful emotions
    elif any(word in user_text for word in ["happy", "joy", "joyful", "excited", "smiling", "great"]):
        reply = (
            "That makes me happy too. You sound cheerful. "
            "Would you like to listen to music or call your family?"
        )

    # 🙏 Gratitude / Contentment
    elif any(word in user_text for word in ["thankful", "grateful", "blessed"]):
        reply = (
            "That is a beautiful feeling. Enjoy this peaceful moment."
        )

    # 💪 Motivation / Encouragement
    elif any(word in user_text for word in ["motivate", "encourage", "support"]):
        reply = (
            "You are doing your best, and that is enough. "
            "Every step matters."
        )

    # 💤 Sleep / Tired
    elif any(word in user_text for word in ["sleep", "tired", "exhausted"]):
        reply = (
            "It sounds like you need some rest. "
            "Lie down comfortably and relax your body."
        )

    # ❓ Safe fallback
    else:
        reply = (
            "I am here with you. You can talk to me anytime. "
            "Tell me how you are feeling."
        )

    return JsonResponse({"reply": reply})

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def voice_assistant(request):
    data = json.loads(request.body)
    user_text = data.get("message", "").lower()

    # -------- Emotional Support --------
    if any(word in user_text for word in ["sad", "low", "depressed", "anxious", "anxiety", "stressed", "worried"]):
        reply = (
            "I’m here with you. You are not alone. "
            "Take a slow deep breath. Inhale… hold… and exhale slowly. "
            "Everything is going to be okay."
        )

    elif any(word in user_text for word in ["relax", "calm", "peace", "tired"]):
        reply = (
            "Let’s relax together. Sit comfortably and take slow deep breaths. "
            "Think of something that makes you feel peaceful."
        )

    elif any(word in user_text for word in ["happy", "joy", "excited", "good", "great"]):
        reply = (
            "That’s wonderful to hear! I’m happy that you are feeling good. "
            "Keep smiling."
        )

    # -------- Health & Memory --------
    elif any(word in user_text for word in ["dizzy", "lightheaded"]):
        reply = (
            "Please sit down safely and take slow breaths. "
            "If you still feel dizzy, you can call your family for help."
        )

    elif any(word in user_text for word in ["forget", "forgot", "forgetting"]):
        reply = (
            "That’s okay. Forgetting sometimes is normal. "
            "You can check your Memory Log to help remember important things."
        )

    elif "who am i" in user_text:
        reply = "You are John. You are at home. You are safe."

    # -------- Navigation Guidance (Exact Paths) --------
    elif "dashboard" in user_text or "home page" in user_text:
        reply = (
            "You are on your Dashboard. "
            "You can always go back to the Dashboard by clicking "
            "'Dashboard' in the left sidebar. Path: Sidebar → Dashboard."
        )

    elif "where are my routines" in user_text or "my routine" in user_text:
        reply = (
            "You can find your routines by clicking on 'Routines' "
            "in the left sidebar. Path: Sidebar → Routines."
        )

    elif "call family" in user_text or "where to call family" in user_text:
        reply = (
            "To call your family, click on 'Call Family' "
            "from the left sidebar or the Call Family button on your dashboard. "
            "Path: Sidebar → Call Family."
        )

    elif "memory game" in user_text or "memory log" in user_text:
        reply = (
            "You can see your memory activities in the Memory Log. "
            "Path: Sidebar → Memory Log."
        )

    elif "my medication" in user_text or "medicine" in user_text:
        reply = (
            "To see your medications, click on 'Medication' "
            "in the left sidebar. Path: Sidebar → Medication."
        )

    elif "set reminder" in user_text or "where are my reminders" in user_text:
        reply = (
            "You can set or view reminders by clicking on 'Reminders' "
            "in the left sidebar. Path: Sidebar → Reminders."
        )

    # -------- Default --------
    else:
        reply = (
            "I am here to help you. "
            "You can ask about your dashboard, routines, medications, "
            "reminders, memory log, or ask me to call your family."
        )

    return JsonResponse({"reply": reply})



from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    profile = request.user.profile
    return render(request, 'user_dashboard.html', {
        'profile': profile
    })

from django.contrib.auth.decorators import login_required
from .models import Profile

@login_required
def dashboard(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    return render(request, 'dashboard/user_dashboard.html', {
        'profile': profile
    })

from django.shortcuts import render, get_object_or_404, redirect
from .models import EmergencyContact
from django.contrib.auth.decorators import login_required

@login_required
def edit_emergency_contact(request, id):
    emergency = get_object_or_404(EmergencyContact, id=id, user=request.user)

    if request.method == "POST":
        emergency.name = request.POST.get("name")
        emergency.relation = request.POST.get("relation")
        emergency.phone = request.POST.get("phone")

        if request.FILES.get("photo"):
            emergency.photo = request.FILES["photo"]

        emergency.save()
        return redirect("family")

    return render(request, "edit_emergency.html", {
        "emergency": emergency
    })
# @login_required
# def add_family_contact(request):
#     if request.method == "POST":
#         FamilyContact.objects.create(
#             user=request.user,
#             name=request.POST["name"],
#             relation=request.POST["relation"],
#             phone=request.POST["phone"],
#             photo=request.FILES.get("photo")
#         )
#         return redirect("family")


# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages

# from .models import FamilyContact


# @login_required
# def family_page(request):
#     """
#     Show all family contacts for the logged-in user
#     """
#     contacts = FamilyContact.objects.filter(user=request.user)

#     return render(request, "templates/app/family.html", {
#         "contacts": contacts
#     })


# @login_required
# def add_family_contact(request):
#     """
#     Handle Add Contact form submission
#     """
#     if request.method == "POST":
#         name = request.POST.get("name")
#         relation = request.POST.get("relation")
#         phone = request.POST.get("phone")
#         photo = request.FILES.get("photo")

#         FamilyContact.objects.create(
#             user=request.user,
#             name=name,
#             relation=relation,
#             phone=phone,
#             photo=photo
#         )

#         messages.success(request, "Family contact added successfully!")

#     return redirect("family")

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import FamilyContact


@login_required
def family_page(request):
    """
    Show all family contacts for the logged-in user
    """
    contacts = FamilyContact.objects.filter(user=request.user)

    return render(request, "app/family.html", {
        "contacts": contacts
    })


@login_required
def add_family_contact(request):
    """
    Handle Add Contact form submission
    """
    if request.method == "POST":
        FamilyContact.objects.create(
            user=request.user,
            name=request.POST.get("name"),
            relation=request.POST.get("relation"),
            phone=request.POST.get("phone"),
            photo=request.FILES.get("photo")
        )

        messages.success(request, "Family contact added successfully!")

    return redirect("family")
