from django.urls import path
from . import views
from .views import chatbot_api

urlpatterns = [

    # =========================
    # AUTH
    # =========================
    
    path('', views.login_view, name='login'),   # 👈 LOGIN PAGE
    path('login/', views.login_view, name='login'),
    path("logout/", views.logout_view, name="logout"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("register/", views.register, name="register"),

    # =========================
    # DASHBOARD (ROLE BASED)
    # =========================
    path("dashboard/", views.dashboard_redirect, name="dashboard"),
    path("user/", views.user_dashboard, name="user_dashboard"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    # app/urls.py
    path("routine/<int:pk>/done/", views.mark_routine_done, name="routine_done"),
    path("routine/<int:routine_id>/done/", views.mark_routine_done, name="routine_done"),
    path("chat/", chatbot_api, name="chatbot_api"),



    # =========================
    # PATIENT MANAGEMENT
    # =========================
    path("patient/create/", views.patient_create, name="patient_create"),
    path("patient/<int:patient_id>/", views.patient_dashboard, name="patient_dashboard"),
    path('patient/<int:patient_id>/', views.dashboard, name='dashboard'),
    # =========================
    # EMOTION (CAMERA)
    # =========================
    path(
        "patient/<int:patient_id>/analyze/",
        views.analyze_emotion,
        name="analyze_emotion"
    ),

    # =========================
    # PRESCRIPTION
    # =========================
    path(
        "patient/<int:patient_id>/upload-prescription/",
        views.upload_prescription,
        name="upload_prescription"
    ),
    path(
        "prescription/<int:pres_id>/",
        views.prescription_detail,
        name="prescription_detail"
    ),

    # =========================
    # VOICE ASSISTANT
    # =========================
    path("voice-assistant/", views.voice_assistant, name="voice_assistant"),

    # =========================
    # REMINDERS
    # =========================
    path(
        "reminder/<int:patient_id>/add/",
        views.add_reminder,
        name="add_reminder"
    ),
    path(
        "reminders/json/",
        views.reminders_json,
        name="reminders_json"
    ),
    path(
        "reminders/mark-seen/<int:pk>/",
        views.mark_reminder_seen,
        name="mark_reminder_seen"
    ),
    path("reminder/edit/<int:pk>/", views.edit_reminder, name="edit_reminder"),
    path("reminder/delete/<int:pk>/", views.delete_reminder, name="delete_reminder"),

    # =========================
    # CHATBOT
    # =========================
    path("chat/", views.chat_page, name="chat_page"),
    path("chatbot/reply/", views.chatbot_reply, name="chatbot_reply"),
    path("chatbot/", views.chat_page, name="chatbot_page"),
    path("chatbot/", views.chat_page, name="chatbot_page"),
    path("chatbot/api/", views.chatbot_reply, name="chatbot_reply"),
    # Chat UI page
    path("chatbot/", views.chat_page, name="chatbot_page"),

    # API endpoint (POST only)
    path("chatbot/api/", views.chatbot_reply, name="chatbot_reply"),
    path("user/", views.user_dashboard, name="user_dashboard"),
    path("routine/add/", views.add_routine, name="add_routine"),
    path("routine/done/<int:routine_id>/", views.mark_routine_done, name="mark_routine_done"),
    path("routine/", views.routine_page, name="routine_page"),
    path("routine/add/", views.add_routine, name="add_routine"),
    path("routine/done/<int:routine_id>/", views.mark_routine_done, name="routine_done"),
    path("medication/", views.medication_page, name="medication"),
    path("family/", views.family_page, name="family"),
    path("memory/", views.memory_log, name="memory"),
    path("reminders/", views.reminders_page, name="reminders"),
    path("reminder/", views.reminder_page, name="reminder_page"),
    path("routines/", views.routine_page, name="routine_page"),
    path("routines/add/", views.add_routine, name="add_routine"),
    path("routines/edit/<int:pk>/", views.edit_routine, name="edit_routine"),
    path("profile/", views.profile_page, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("profile/edit", views.edit_profile),
    path("profile/emergency/add/", views.add_emergency, name="add_emergency"),
    path("profile/emergency/add", views.add_emergency),
    path("profile/emergency/edit/<int:id>/", views.edit_emergency, name="edit_emergency"),
    path("profile/emergency/edit/<int:id>", views.edit_emergency),
    path("profile/change-playback-speed/", views.change_playback_speed, name="change_playback_speed"),
    path("profile/change-playback-speed", views.change_playback_speed),
    path("profile/toggle-dark-mode/", views.toggle_dark_mode, name="toggle_dark_mode"),
    path("profile/toggle-dark-mode", views.toggle_dark_mode),
    path("profile/change-font-size/", views.change_font_size, name="change_font_size"),
    path("profile/change-font-size", views.change_font_size),
    path("profile/delete-account/", views.delete_account, name="delete_account"),
    path("profile/delete-account", views.delete_account),
    path("detect-emotion/", views.detect_emotion, name="detect_emotion"),
    path('camera/', views.live_camera, name='live_camera'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path("voice-assistant/", views.voice_assistant, name="voice_assistant"),
    path("voice-assistant/", views.voice_assistant, name="voice_assistant"),
    path("family/edit/<int:id>/", views.edit_emergency_contact, name="edit_emergency"),
    path("family/add/", views.add_family_contact, name="add_family_contact"),



    
    # urls.py

    path("chatbot/", views.chatbot_page, name="chatbot"),
    path("chatbot/api/", views.chatbot_api, name="chatbot_api"),
    

    
    # =========================
    # THERAPY
    # =========================
    path(
        "therapy/session/",
        views.therapy_session,
        name="therapy_session"
    ),

    # =========================
    # MEMORY SEQUENCE
    # =========================
    path(
        "memory/sequence/",
        views.remember_sequence,
        name="remember_sequence"
    ),
    path(
        "memory/sequence/score/",
        views.remember_sequence_score,
        name="remember_sequence_score"
    ),
]
