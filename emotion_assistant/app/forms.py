from django import forms
from .models import Patient, Prescription, Reminder


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            "first_name",
            "last_name",
            "dob",
            "age",
            "room",
            "photo",
            "notes",
            "support_mode",
            "voice_enabled",
            "speech_speed",
        ]

        widgets = {
            "dob": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['file']

class ReminderForm(forms.ModelForm):
    reminder_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    class Meta:
        model = Reminder
        fields = ['message', 'reminder_time']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter reminder message...'}),
            'reminder_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
        }


from django import forms
from django.contrib.auth.models import User
from .models import Patient


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password"})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm Password"})
    )

    class Meta:
        model = User
        fields = ["username", "email"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")


from django import forms
from .models import DailyRoutine

class DailyRoutineForm(forms.ModelForm):
    class Meta:
        model = DailyRoutine
        fields = ['title', 'time']
        widgets = {
            'time': forms.TimeInput(attrs={'type': 'time'})
        }


from django import forms
from .models import Routine

class RoutineForm(forms.ModelForm):
    class Meta:
        model = Routine
        fields = ['name', 'icon', 'is_active']
        widgets = {
            'icon': forms.TextInput(attrs={'placeholder': 'e.g. ⏰'}),
        }
