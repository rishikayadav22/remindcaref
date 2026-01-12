from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_reminder_email(email, subject, body):
    send_mail(subject, body, None, [email])
    return True
