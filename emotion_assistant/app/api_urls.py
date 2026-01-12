from django.urls import path
from . import views_api

urlpatterns = [
    path('patients/', views_api.patients_list),
    path('patients/<int:pk>/', views_api.patient_detail),
    path('prescriptions/', views_api.prescriptions_list),
    path('prescriptions/<int:pk>/', views_api.prescription_detail),

    # ✅ SNAPSHOTS
    path('snapshots/', views_api.snapshots_list),
    path('snapshots/<int:pk>/', views_api.snapshot_detail),
    # You'll add prescriptions and snapshots later
]
