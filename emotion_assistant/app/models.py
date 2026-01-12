from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.conf import settings


User = get_user_model()

from django.db import models
from django.contrib.auth.models import User

from django.db import models

class Patient(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='patients'
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    dob = models.DateField()
    age = models.IntegerField()
    room = models.CharField(max_length=50)
    photo = models.ImageField(upload_to='patients/', blank=True, null=True)
    notes = models.TextField(blank=True)
    SUPPORT_MODES = [
        ('alz', 'Alzheimer’s / Memory Support'),
        ('asd', 'Autism Support'),
        ('adhd', 'ADHD Support'),
        ('elder', 'Elderly Care'),
        ('general', 'General Wellness'),
    ]
    support_mode = models.CharField(
        max_length=20,
        choices=SUPPORT_MODES,
        default='general'
    )
    voice_enabled = models.BooleanField(default=True)
    speech_speed = models.IntegerField(
        choices=[(1, 'Slow'), (2, 'Normal')],
        default=2
    )    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Snapshot(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='snapshots')
    image = models.ImageField(upload_to='snapshots/')
    timestamp = models.DateTimeField(auto_now_add=True)
    detected_emotion = models.CharField(max_length=50, blank=True)

class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    file = models.FileField(upload_to='prescriptions/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    ocr_text = models.TextField(blank=True)
    parsed_meds = models.JSONField(null=True, blank=True)
    raw_parse_errors = models.TextField(blank=True)
    def __str__(self):
        return f"Prescription {self.id} for {self.patient}"

class ChatMessage(models.Model):
    """
    Stores chat messages for context and auditing.
    sender: 'patient' | 'assistant' | 'system'
    """
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True, related_name='chats')
    sender = models.CharField(max_length=30)  # 'patient' or 'assistant'
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender}: {self.content[:60]}"

class Reminder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True, default='')
    message = models.TextField(blank=True)
    reminder_time = models.DateTimeField()
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reminder for {self.user} at {self.reminder_time}: {self.title}"
    

from django.db import models
from django.contrib.auth.models import User

class UserProgress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    emotion_score = models.FloatField(default=0)
    reminders_completed = models.IntegerField(default=0)
    therapy_sessions = models.IntegerField(default=0)
    last_active = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_progress(sender, instance, created, **kwargs):
    if created:
        UserProgress.objects.create(user=instance)

from django.db import models
from django.contrib.auth.models import User

class DailyRoutine(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    time = models.TimeField()
    completed = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.time}"


from django.db import models
from django.conf import settings

class Medication(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    instruction = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


from django.db import models
from django.contrib.auth.models import User

class FamilyContact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    relation = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    photo = models.ImageField(upload_to="family/", blank=True, null=True)

    def __str__(self):
        return self.name
    
from django.db import models
from django.conf import settings

class MemoryScore(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.IntegerField()
    level = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.score}"


class Routine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=20, default="⏰")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @property
    def title(self):
        return self.name


class RoutineTask(models.Model):
    routine = models.ForeignKey(Routine, related_name="tasks", on_delete=models.CASCADE)
    time = models.TimeField()
    description = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.time} - {self.description}"

    @property
    def task(self):
        return self.description

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    playback_speed = models.CharField(
        max_length=10,
        choices=[("Normal", "Normal"), ("Slow", "Slow"), ("Fast", "Fast")],
        default="Normal"
    )
    dark_mode = models.BooleanField(default=False)
    font_size = models.CharField(
        max_length=10,
        choices=[("Small", "Small"), ("Medium", "Medium"), ("Large", "Large")],
        default="Medium"
    )

    def __str__(self):
        return self.user.username


class EmergencyContact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    relation = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.name





from django.db import models
from django.contrib.auth.models import User
class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    phone = models.CharField(max_length=15, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    playback_speed = models.CharField(
        max_length=10,
        choices=[
            ('Slow', 'Slow'),
            ('Normal', 'Normal'),
            ('Fast', 'Fast')
        ],
        default='Normal'
    )

    dark_mode = models.BooleanField(default=False)

    font_size = models.CharField(
        max_length=10,
        choices=[
            ('Small', 'Small'),
            ('Medium', 'Medium'),
            ('Large', 'Large')
        ],
        default='Medium'
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"
class EmergencyContact(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='emergency_contacts'
    )

    name = models.CharField(max_length=100)
    relation = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.name} ({self.relation})"




from django.db import models

class EmotionSnapshot(models.Model):
    EMOTION_CHOICES = [
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
        ('surprise', 'Surprise'),
        ('fear', 'Fear'),
        ('neutral', 'Neutral'),
        ('disgust', 'Disgust'),
        ('Unknown', 'Unknown'),
    ]

    emotion = models.CharField(max_length=20, choices=EMOTION_CHOICES)
    image = models.ImageField(upload_to='emotion_snapshots/')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.emotion} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"



from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    assistant_image = models.ImageField(
        upload_to='assistant_images/',
        default='assistant_images/default.avif'
    )

    def __str__(self):
        return self.user.username


from django.db import models
from django.contrib.auth.models import User

class EmergencyContact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    relation = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    photo = models.ImageField(
        upload_to="family_photos/",
        default="family_photos/default.jpg",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.name} ({self.relation})"
from django.db import models
from django.contrib.auth.models import User


class FamilyContact(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="family_contacts"
    )

    name = models.CharField(max_length=100)
    relation = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)

    photo = models.ImageField(
        upload_to="family_photos/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.relation})"
from django.db import models
from django.contrib.auth.models import User


class FamilyContact(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="family_contacts"
    )

    name = models.CharField(max_length=100)
    relation = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)

    photo = models.ImageField(
        upload_to="family_photos/",
        blank=True,
        null=True
    )

    # TEMPORARILY nullable to satisfy SQLite
    created_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.relation})"


from django.db import models
from django.contrib.auth.models import User

class FamilyContact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="family_contacts")
    name = models.CharField(max_length=100)
    relation = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    photo = models.ImageField(upload_to="family_photos/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.relation})"
